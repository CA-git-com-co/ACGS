#!/usr/bin/env python3
"""
ACGS-1 Redis Infrastructure Setup Script

This script sets up Redis infrastructure for caching, session management,
and distributed task queues for the ACGS-1 system.
"""

import logging
import subprocess
import sys
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


def setup_redis_infrastructure():
    """Set up Redis infrastructure for ACGS-1."""
    logger.info("Setting up Redis infrastructure...")

    # Create Redis configuration directory
    redis_config_dir = PROJECT_ROOT / "infrastructure" / "redis"
    redis_config_dir.mkdir(exist_ok=True)

    # Create Redis configuration file
    redis_conf = redis_config_dir / "redis.conf"
    with open(redis_conf, "w") as f:
        f.write(
            """# ACGS-1 Redis Configuration
bind 127.0.0.1
protected-mode yes
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize no
supervised no
pidfile /var/run/redis_6379.pid
loglevel notice
logfile ""
databases 16
always-show-logo yes
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
replica-priority 100
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
lua-time-limit 5000
maxmemory 256mb
maxmemory-policy allkeys-lru
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
"""
        )

    # Create Docker Compose file for Redis
    redis_docker_compose = redis_config_dir / "docker-compose.yml"
    with open(redis_docker_compose, "w") as f:
        f.write(
            """version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: acgs_redis
    command: redis-server /usr/local/etc/redis/redis.conf
    ports:
      - "6379:6379"
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: acgs_redis_commander
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8081:8081"
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis_data:
"""
        )

    # Update service dependencies to include Redis
    logger.info("Updating service dependencies to include Redis...")
    for service_dir in (PROJECT_ROOT / "services" / "core").glob("*"):
        if service_dir.is_dir():
            requirements_file = service_dir / "config/environments/requirements.txt"
            if requirements_file.exists():
                with open(requirements_file) as f:
                    content = f.read()

                if "redis" not in content:
                    with open(requirements_file, "a") as f:
                        f.write(
                            "\n# Redis client for caching and session management\nredis[hiredis]>=5.0.0\n"
                        )
                    logger.info(f"Added Redis dependency to {service_dir.name}")

    # Start Redis services
    logger.info("Starting Redis services...")
    try:
        subprocess.run(
            ["docker-compose", "-f", str(redis_docker_compose), "up", "-d"],
            check=True,
        )
        logger.info("✅ Redis services started successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to start Redis services: {e}")
        return False

    logger.info("✅ Redis infrastructure setup completed successfully")
    return True


if __name__ == "__main__":
    success = setup_redis_infrastructure()
    sys.exit(0 if success else 1)
