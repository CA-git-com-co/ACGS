"""
ACGS-1 PgBouncer Prometheus Exporter
Phase 2 - Enterprise Scalability & Performance

Custom Prometheus exporter for PgBouncer metrics collection
and performance monitoring integration.
"""

import asyncio
import logging
import time

import asyncpg
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
    start_http_server,
)

logger = logging.getLogger(__name__)


class PgBouncerMetricsCollector:
    """Collects metrics from PgBouncer for Prometheus."""

    def __init__(self, pgbouncer_host: str = "localhost", pgbouncer_port: int = 6432):
        self.pgbouncer_host = pgbouncer_host
        self.pgbouncer_port = pgbouncer_port
        self.registry = CollectorRegistry()

        # Initialize Prometheus metrics
        self._init_metrics()

        logger.info(
            f"PgBouncer metrics collector initialized for {pgbouncer_host}:{pgbouncer_port}"
        )

    def _init_metrics(self):
        """Initialize Prometheus metrics."""

        # Connection metrics
        self.total_connections = Gauge(
            "pgbouncer_total_connections",
            "Total number of connections",
            ["database", "user"],
            registry=self.registry,
        )

        self.active_connections = Gauge(
            "pgbouncer_active_connections",
            "Number of active connections",
            ["database", "user"],
            registry=self.registry,
        )

        self.waiting_connections = Gauge(
            "pgbouncer_waiting_connections",
            "Number of waiting connections",
            ["database", "user"],
            registry=self.registry,
        )

        # Pool metrics
        self.pool_size = Gauge(
            "pgbouncer_pool_size",
            "Current pool size",
            ["database"],
            registry=self.registry,
        )

        self.pool_used = Gauge(
            "pgbouncer_pool_used",
            "Number of used connections in pool",
            ["database"],
            registry=self.registry,
        )

        self.pool_tested = Gauge(
            "pgbouncer_pool_tested",
            "Number of tested connections in pool",
            ["database"],
            registry=self.registry,
        )

        # Transaction metrics
        self.total_requests = Counter(
            "pgbouncer_total_requests_total",
            "Total number of requests",
            ["database"],
            registry=self.registry,
        )

        self.total_received = Counter(
            "pgbouncer_total_received_bytes_total",
            "Total bytes received",
            ["database"],
            registry=self.registry,
        )

        self.total_sent = Counter(
            "pgbouncer_total_sent_bytes_total",
            "Total bytes sent",
            ["database"],
            registry=self.registry,
        )

        # Performance metrics
        self.avg_req_time = Gauge(
            "pgbouncer_avg_request_time_seconds",
            "Average request time in seconds",
            ["database"],
            registry=self.registry,
        )

        self.avg_wait_time = Gauge(
            "pgbouncer_avg_wait_time_seconds",
            "Average wait time in seconds",
            ["database"],
            registry=self.registry,
        )

        # Health metrics
        self.up = Gauge(
            "pgbouncer_up", "PgBouncer is up and responding", registry=self.registry
        )

        self.scrape_duration = Histogram(
            "pgbouncer_scrape_duration_seconds",
            "Time spent scraping PgBouncer metrics",
            registry=self.registry,
        )

        # Info metrics
        self.info = Info(
            "pgbouncer_info",
            "PgBouncer version and configuration info",
            registry=self.registry,
        )

    async def collect_metrics(self) -> bool:
        """Collect metrics from PgBouncer."""
        start_time = time.time()

        try:
            # Connect to PgBouncer admin interface
            conn = await asyncpg.connect(
                host=self.pgbouncer_host,
                port=self.pgbouncer_port,
                database="pgbouncer",
                user="acgs_user",
                password="acgs_password",
                timeout=10,
            )

            # Collect various metrics
            await self._collect_pool_metrics(conn)
            await self._collect_client_metrics(conn)
            await self._collect_database_metrics(conn)
            await self._collect_stats_metrics(conn)
            await self._collect_config_info(conn)

            await conn.close()

            # Mark as healthy
            self.up.set(1)

            # Record scrape duration
            scrape_time = time.time() - start_time
            self.scrape_duration.observe(scrape_time)

            logger.debug(f"Metrics collection completed in {scrape_time:.3f}s")
            return True

        except Exception as e:
            logger.error(f"Failed to collect PgBouncer metrics: {e}")
            self.up.set(0)
            return False

    async def _collect_pool_metrics(self, conn):
        """Collect pool-related metrics."""
        try:
            pools = await conn.fetch("SHOW POOLS")

            for pool in pools:
                database = pool["database"]

                self.pool_size.labels(database=database).set(pool["pool_size"])
                self.pool_used.labels(database=database).set(pool["pool_used"])
                self.pool_tested.labels(database=database).set(pool["pool_tested"])

        except Exception as e:
            logger.warning(f"Failed to collect pool metrics: {e}")

    async def _collect_client_metrics(self, conn):
        """Collect client connection metrics."""
        try:
            clients = await conn.fetch("SHOW CLIENTS")

            # Group by database and user
            connection_counts = {}

            for client in clients:
                database = client["database"]
                user = client["user"]
                state = client["state"]

                key = (database, user)
                if key not in connection_counts:
                    connection_counts[key] = {"total": 0, "active": 0, "waiting": 0}

                connection_counts[key]["total"] += 1

                if state == "active":
                    connection_counts[key]["active"] += 1
                elif state == "waiting":
                    connection_counts[key]["waiting"] += 1

            # Update metrics
            for (database, user), counts in connection_counts.items():
                self.total_connections.labels(database=database, user=user).set(
                    counts["total"]
                )
                self.active_connections.labels(database=database, user=user).set(
                    counts["active"]
                )
                self.waiting_connections.labels(database=database, user=user).set(
                    counts["waiting"]
                )

        except Exception as e:
            logger.warning(f"Failed to collect client metrics: {e}")

    async def _collect_database_metrics(self, conn):
        """Collect database-level metrics."""
        try:
            databases = await conn.fetch("SHOW DATABASES")

            for db in databases:
                database = db["name"]

                # Skip special databases
                if database in ["pgbouncer", "template0", "template1"]:
                    continue

                # Additional database-specific metrics can be added here

        except Exception as e:
            logger.warning(f"Failed to collect database metrics: {e}")

    async def _collect_stats_metrics(self, conn):
        """Collect statistics metrics."""
        try:
            stats = await conn.fetch("SHOW STATS")

            for stat in stats:
                database = stat["database"]

                # Skip special databases
                if database in ["pgbouncer"]:
                    continue

                # Update counters (these are cumulative)
                self.total_requests.labels(database=database)._value._value = stat[
                    "total_requests"
                ]
                self.total_received.labels(database=database)._value._value = stat[
                    "total_received"
                ]
                self.total_sent.labels(database=database)._value._value = stat[
                    "total_sent"
                ]

                # Update gauges for average times (convert microseconds to seconds)
                if stat["total_requests"] > 0:
                    avg_req_time = (
                        stat["total_query_time"] / stat["total_requests"] / 1000000
                    )
                    avg_wait_time = (
                        stat["total_wait_time"] / stat["total_requests"] / 1000000
                    )

                    self.avg_req_time.labels(database=database).set(avg_req_time)
                    self.avg_wait_time.labels(database=database).set(avg_wait_time)

        except Exception as e:
            logger.warning(f"Failed to collect stats metrics: {e}")

    async def _collect_config_info(self, conn):
        """Collect configuration information."""
        try:
            config = await conn.fetch("SHOW CONFIG")

            config_dict = {}
            for item in config:
                config_dict[item["key"]] = item["value"]

            # Set info metric with configuration
            self.info.info(
                {
                    "version": config_dict.get("version", "unknown"),
                    "listen_addr": config_dict.get("listen_addr", "unknown"),
                    "listen_port": config_dict.get("listen_port", "unknown"),
                    "pool_mode": config_dict.get("pool_mode", "unknown"),
                    "max_client_conn": config_dict.get("max_client_conn", "unknown"),
                    "default_pool_size": config_dict.get(
                        "default_pool_size", "unknown"
                    ),
                }
            )

        except Exception as e:
            logger.warning(f"Failed to collect config info: {e}")

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry).decode("utf-8")


class PgBouncerExporter:
    """Prometheus exporter for PgBouncer metrics."""

    def __init__(
        self,
        pgbouncer_host: str = "localhost",
        pgbouncer_port: int = 6432,
        exporter_port: int = 9187,
        scrape_interval: int = 15,
    ):
        self.pgbouncer_host = pgbouncer_host
        self.pgbouncer_port = pgbouncer_port
        self.exporter_port = exporter_port
        self.scrape_interval = scrape_interval

        self.collector = PgBouncerMetricsCollector(pgbouncer_host, pgbouncer_port)
        self.is_running = False

        logger.info(f"PgBouncer exporter initialized on port {exporter_port}")

    async def start(self):
        """Start the metrics exporter."""
        self.is_running = True

        # Start HTTP server for metrics endpoint
        start_http_server(self.exporter_port, registry=self.collector.registry)
        logger.info(f"Metrics server started on port {self.exporter_port}")

        # Start metrics collection loop
        await self._collection_loop()

    async def stop(self):
        """Stop the metrics exporter."""
        self.is_running = False
        logger.info("PgBouncer exporter stopped")

    async def _collection_loop(self):
        """Main metrics collection loop."""
        while self.is_running:
            try:
                await self.collector.collect_metrics()
                await asyncio.sleep(self.scrape_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(self.scrape_interval)


async def main():
    """Main function for running the exporter."""
    import argparse

    parser = argparse.ArgumentParser(description="PgBouncer Prometheus Exporter")
    parser.add_argument("--pgbouncer-host", default="localhost", help="PgBouncer host")
    parser.add_argument(
        "--pgbouncer-port", type=int, default=6432, help="PgBouncer port"
    )
    parser.add_argument("--exporter-port", type=int, default=9187, help="Exporter port")
    parser.add_argument(
        "--scrape-interval", type=int, default=15, help="Scrape interval in seconds"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create and start exporter
    exporter = PgBouncerExporter(
        pgbouncer_host=args.pgbouncer_host,
        pgbouncer_port=args.pgbouncer_port,
        exporter_port=args.exporter_port,
        scrape_interval=args.scrape_interval,
    )

    try:
        await exporter.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await exporter.stop()


if __name__ == "__main__":
    asyncio.run(main())
