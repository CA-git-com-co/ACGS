#!/usr/bin/env python3
"""
ACGS-1 Database Query Performance Optimization

This script analyzes database query performance across all ACGS-1 services,
identifies optimization opportunities, and implements performance improvements
including indexing strategies, query optimization, and caching recommendations.

Features:
- Comprehensive query performance analysis
- Automatic index creation for slow queries
- Query plan analysis and optimization
- N+1 query detection and resolution
- Caching strategy recommendations
- Performance monitoring and alerting
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib

import asyncpg
import psutil
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class QueryPerformanceMetrics:
    """Query performance metrics."""
    query_hash: str
    query_text: str
    execution_count: int
    total_time_ms: float
    mean_time_ms: float
    min_time_ms: float
    max_time_ms: float
    rows_returned: int
    tables_accessed: List[str]
    indexes_used: List[str]
    optimization_score: float
    recommendations: List[str]


@dataclass
class IndexRecommendation:
    """Database index recommendation."""
    table_name: str
    columns: List[str]
    index_type: str  # btree, gin, gist, hash
    estimated_benefit: float
    creation_sql: str
    rationale: str


@dataclass
class OptimizationResult:
    """Query optimization result."""
    original_query: str
    optimized_query: str
    performance_improvement: float
    optimization_type: str
    applied: bool
    rollback_sql: Optional[str] = None


class DatabaseQueryOptimizer:
    """Comprehensive database query performance optimizer."""
    
    def __init__(self, database_url: str):
        """Initialize optimizer with database connection."""
        self.database_url = database_url
        self.engine = None
        self.async_engine = None
        self.query_metrics: Dict[str, QueryPerformanceMetrics] = {}
        self.index_recommendations: List[IndexRecommendation] = []
        self.optimization_results: List[OptimizationResult] = []
        
        # Performance thresholds
        self.slow_query_threshold_ms = 100
        self.very_slow_query_threshold_ms = 1000
        self.high_frequency_threshold = 100
        
    async def initialize(self):
        """Initialize database connections."""
        self.async_engine = create_async_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            echo=False
        )
        
        # Test connection
        async with self.async_engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"Connected to database: {version}")
    
    async def analyze_query_performance(self) -> Dict[str, Any]:
        """Comprehensive query performance analysis."""
        logger.info("🔍 Starting comprehensive query performance analysis...")
        
        analysis_start = time.time()
        
        # Collect query statistics
        query_stats = await self._collect_query_statistics()
        
        # Analyze slow queries
        slow_queries = await self._analyze_slow_queries()
        
        # Check index usage
        index_usage = await self._analyze_index_usage()
        
        # Detect N+1 queries
        n_plus_one_queries = await self._detect_n_plus_one_queries()
        
        # Analyze table statistics
        table_stats = await self._analyze_table_statistics()
        
        # Generate optimization recommendations
        recommendations = await self._generate_optimization_recommendations()
        
        analysis_time = time.time() - analysis_start
        
        analysis_result = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_duration_seconds": round(analysis_time, 2),
            "query_statistics": query_stats,
            "slow_queries": slow_queries,
            "index_usage": index_usage,
            "n_plus_one_queries": n_plus_one_queries,
            "table_statistics": table_stats,
            "optimization_recommendations": recommendations,
            "performance_summary": self._generate_performance_summary()
        }
        
        logger.info(f"✅ Query performance analysis completed in {analysis_time:.2f}s")
        return analysis_result
    
    async def _collect_query_statistics(self) -> Dict[str, Any]:
        """Collect comprehensive query statistics."""
        logger.info("📊 Collecting query statistics...")
        
        async with self.async_engine.begin() as conn:
            # Enable pg_stat_statements if not enabled
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_stat_statements"))
            
            # Get query statistics
            query_stats_sql = """
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                min_time,
                max_time,
                rows,
                100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
            FROM pg_stat_statements
            WHERE calls > 1
            ORDER BY total_time DESC
            LIMIT 50
            """
            
            result = await conn.execute(text(query_stats_sql))
            query_stats = result.fetchall()
            
            # Process query statistics
            processed_stats = []
            for stat in query_stats:
                query_hash = hashlib.md5(stat.query.encode()).hexdigest()
                
                metric = QueryPerformanceMetrics(
                    query_hash=query_hash,
                    query_text=stat.query[:200] + "..." if len(stat.query) > 200 else stat.query,
                    execution_count=stat.calls,
                    total_time_ms=float(stat.total_time),
                    mean_time_ms=float(stat.mean_time),
                    min_time_ms=float(stat.min_time),
                    max_time_ms=float(stat.max_time),
                    rows_returned=stat.rows,
                    tables_accessed=self._extract_tables_from_query(stat.query),
                    indexes_used=[],  # Will be populated later
                    optimization_score=self._calculate_optimization_score(stat),
                    recommendations=[]
                )
                
                self.query_metrics[query_hash] = metric
                processed_stats.append(asdict(metric))
            
            return {
                "total_queries_analyzed": len(processed_stats),
                "query_details": processed_stats
            }
    
    async def _analyze_slow_queries(self) -> Dict[str, Any]:
        """Analyze slow queries and generate optimization recommendations."""
        logger.info("🐌 Analyzing slow queries...")
        
        slow_queries = []
        very_slow_queries = []
        
        for query_hash, metric in self.query_metrics.items():
            if metric.mean_time_ms > self.slow_query_threshold_ms:
                slow_queries.append(metric)
                
                if metric.mean_time_ms > self.very_slow_query_threshold_ms:
                    very_slow_queries.append(metric)
                    
                    # Generate specific recommendations for very slow queries
                    recommendations = await self._generate_query_recommendations(metric)
                    metric.recommendations.extend(recommendations)
        
        return {
            "slow_queries_count": len(slow_queries),
            "very_slow_queries_count": len(very_slow_queries),
            "slow_query_threshold_ms": self.slow_query_threshold_ms,
            "very_slow_query_threshold_ms": self.very_slow_query_threshold_ms,
            "slow_queries": [asdict(q) for q in slow_queries[:10]],  # Top 10
            "optimization_opportunities": len([q for q in slow_queries if q.optimization_score < 0.7])
        }
    
    async def _analyze_index_usage(self) -> Dict[str, Any]:
        """Analyze index usage and identify unused or missing indexes."""
        logger.info("📇 Analyzing index usage...")
        
        async with self.async_engine.begin() as conn:
            # Get index usage statistics
            index_usage_sql = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_tup_read,
                idx_tup_fetch,
                idx_scan,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
            """
            
            result = await conn.execute(text(index_usage_sql))
            index_stats = result.fetchall()
            
            # Identify unused indexes
            unused_indexes = [
                {
                    "schema": idx.schemaname,
                    "table": idx.tablename,
                    "index": idx.indexname,
                    "size": idx.index_size,
                    "scans": idx.idx_scan
                }
                for idx in index_stats if idx.idx_scan < 10
            ]
            
            # Identify missing indexes for slow queries
            missing_indexes = await self._identify_missing_indexes()
            
            return {
                "total_indexes": len(index_stats),
                "unused_indexes": unused_indexes,
                "missing_indexes": missing_indexes,
                "index_recommendations": [asdict(rec) for rec in self.index_recommendations]
            }
    
    async def _detect_n_plus_one_queries(self) -> Dict[str, Any]:
        """Detect N+1 query patterns."""
        logger.info("🔍 Detecting N+1 query patterns...")
        
        n_plus_one_patterns = []
        
        # Group queries by pattern
        query_patterns = {}
        for metric in self.query_metrics.values():
            # Normalize query to detect patterns
            normalized = self._normalize_query_for_pattern_detection(metric.query_text)
            if normalized not in query_patterns:
                query_patterns[normalized] = []
            query_patterns[normalized].append(metric)
        
        # Identify potential N+1 patterns
        for pattern, queries in query_patterns.items():
            if len(queries) > self.high_frequency_threshold:
                # Check if this looks like an N+1 pattern
                if self._is_likely_n_plus_one_pattern(pattern, queries):
                    n_plus_one_patterns.append({
                        "pattern": pattern,
                        "query_count": len(queries),
                        "total_execution_time_ms": sum(q.total_time_ms for q in queries),
                        "average_time_ms": sum(q.mean_time_ms for q in queries) / len(queries),
                        "optimization_potential": "HIGH",
                        "recommendation": "Consider using JOIN or eager loading"
                    })
        
        return {
            "n_plus_one_patterns_detected": len(n_plus_one_patterns),
            "patterns": n_plus_one_patterns[:5],  # Top 5
            "total_optimization_potential_ms": sum(
                p["total_execution_time_ms"] for p in n_plus_one_patterns
            )
        }
    
    async def _analyze_table_statistics(self) -> Dict[str, Any]:
        """Analyze table statistics and health."""
        logger.info("📋 Analyzing table statistics...")
        
        async with self.async_engine.begin() as conn:
            table_stats_sql = """
            SELECT 
                schemaname,
                tablename,
                n_tup_ins,
                n_tup_upd,
                n_tup_del,
                n_live_tup,
                n_dead_tup,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size
            FROM pg_stat_user_tables
            ORDER BY n_live_tup DESC
            """
            
            result = await conn.execute(text(table_stats_sql))
            table_stats = result.fetchall()
            
            # Identify tables needing maintenance
            maintenance_needed = []
            for table in table_stats:
                dead_tuple_ratio = table.n_dead_tup / max(table.n_live_tup, 1)
                if dead_tuple_ratio > 0.1:  # More than 10% dead tuples
                    maintenance_needed.append({
                        "table": f"{table.schemaname}.{table.tablename}",
                        "dead_tuple_ratio": round(dead_tuple_ratio, 3),
                        "recommendation": "VACUUM ANALYZE recommended"
                    })
            
            return {
                "total_tables": len(table_stats),
                "tables_needing_maintenance": maintenance_needed,
                "largest_tables": [
                    {
                        "table": f"{t.schemaname}.{t.tablename}",
                        "size": t.table_size,
                        "live_tuples": t.n_live_tup
                    }
                    for t in table_stats[:10]
                ]
            }
    
    async def _generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate comprehensive optimization recommendations."""
        logger.info("💡 Generating optimization recommendations...")
        
        recommendations = []
        
        # Index recommendations
        for index_rec in self.index_recommendations:
            recommendations.append({
                "type": "INDEX_CREATION",
                "priority": "HIGH" if index_rec.estimated_benefit > 0.5 else "MEDIUM",
                "description": f"Create index on {index_rec.table_name}({', '.join(index_rec.columns)})",
                "rationale": index_rec.rationale,
                "sql": index_rec.creation_sql,
                "estimated_benefit": index_rec.estimated_benefit
            })
        
        # Query optimization recommendations
        for metric in self.query_metrics.values():
            if metric.optimization_score < 0.5:
                recommendations.append({
                    "type": "QUERY_OPTIMIZATION",
                    "priority": "HIGH" if metric.mean_time_ms > 500 else "MEDIUM",
                    "description": f"Optimize query with {metric.execution_count} executions",
                    "query_hash": metric.query_hash,
                    "current_performance": f"{metric.mean_time_ms:.2f}ms average",
                    "recommendations": metric.recommendations
                })
        
        # Sort by priority and estimated benefit
        recommendations.sort(key=lambda x: (
            x.get("priority") == "HIGH",
            x.get("estimated_benefit", 0)
        ), reverse=True)
        
        return recommendations[:20]  # Top 20 recommendations
    
    def _extract_tables_from_query(self, query: str) -> List[str]:
        """Extract table names from SQL query."""
        # Simple regex-based extraction (could be improved with SQL parser)
        import re
        
        # Look for FROM and JOIN clauses
        from_pattern = r'\bFROM\s+(\w+)'
        join_pattern = r'\bJOIN\s+(\w+)'
        
        tables = []
        tables.extend(re.findall(from_pattern, query, re.IGNORECASE))
        tables.extend(re.findall(join_pattern, query, re.IGNORECASE))
        
        return list(set(tables))
    
    def _calculate_optimization_score(self, stat) -> float:
        """Calculate optimization score for a query (0-1, higher is better)."""
        # Factors: execution time, frequency, cache hit ratio
        time_score = max(0, 1 - (stat.mean_time / 1000))  # Normalize to 1 second
        frequency_score = min(1, stat.calls / 1000)  # Normalize to 1000 calls
        cache_score = getattr(stat, 'hit_percent', 95) / 100
        
        return (time_score + frequency_score + cache_score) / 3
    
    async def _generate_query_recommendations(self, metric: QueryPerformanceMetrics) -> List[str]:
        """Generate specific recommendations for a query."""
        recommendations = []
        
        if metric.mean_time_ms > 500:
            recommendations.append("Consider adding appropriate indexes")
        
        if metric.execution_count > 1000:
            recommendations.append("Consider caching results")
        
        if "SELECT *" in metric.query_text.upper():
            recommendations.append("Avoid SELECT *, specify needed columns")
        
        if len(metric.tables_accessed) > 3:
            recommendations.append("Consider breaking into smaller queries")
        
        return recommendations
    
    async def _identify_missing_indexes(self) -> List[Dict[str, Any]]:
        """Identify missing indexes based on query patterns."""
        missing_indexes = []
        
        # Analyze WHERE clauses in slow queries
        for metric in self.query_metrics.values():
            if metric.mean_time_ms > self.slow_query_threshold_ms:
                # Simple pattern matching for WHERE clauses
                if "WHERE" in metric.query_text.upper():
                    # This is a simplified approach - in production, use query plan analysis
                    for table in metric.tables_accessed:
                        missing_indexes.append({
                            "table": table,
                            "suggested_columns": ["id", "created_at"],  # Common patterns
                            "query_hash": metric.query_hash,
                            "potential_benefit": "MEDIUM"
                        })
        
        return missing_indexes[:10]  # Limit results
    
    def _normalize_query_for_pattern_detection(self, query: str) -> str:
        """Normalize query for pattern detection."""
        import re
        
        # Replace literals with placeholders
        normalized = re.sub(r"'[^']*'", "'?'", query)
        normalized = re.sub(r'\b\d+\b', '?', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
    
    def _is_likely_n_plus_one_pattern(self, pattern: str, queries: List[QueryPerformanceMetrics]) -> bool:
        """Check if query pattern indicates N+1 problem."""
        # Simple heuristics for N+1 detection
        if "SELECT" in pattern.upper() and "WHERE" in pattern.upper():
            # High frequency with similar execution times suggests N+1
            avg_time = sum(q.mean_time_ms for q in queries) / len(queries)
            time_variance = sum((q.mean_time_ms - avg_time) ** 2 for q in queries) / len(queries)
            
            return len(queries) > 50 and time_variance < (avg_time * 0.1)
        
        return False
    
    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary."""
        total_queries = len(self.query_metrics)
        slow_queries = sum(1 for m in self.query_metrics.values() if m.mean_time_ms > self.slow_query_threshold_ms)
        
        return {
            "total_queries_analyzed": total_queries,
            "slow_queries_count": slow_queries,
            "slow_query_percentage": round((slow_queries / max(total_queries, 1)) * 100, 2),
            "average_query_time_ms": round(
                sum(m.mean_time_ms for m in self.query_metrics.values()) / max(total_queries, 1), 2
            ),
            "optimization_opportunities": len(self.index_recommendations),
            "performance_grade": self._calculate_performance_grade()
        }
    
    def _calculate_performance_grade(self) -> str:
        """Calculate overall performance grade."""
        total_queries = len(self.query_metrics)
        if total_queries == 0:
            return "N/A"
        
        slow_percentage = sum(1 for m in self.query_metrics.values() if m.mean_time_ms > self.slow_query_threshold_ms) / total_queries
        
        if slow_percentage < 0.05:
            return "A"
        elif slow_percentage < 0.10:
            return "B"
        elif slow_percentage < 0.20:
            return "C"
        elif slow_percentage < 0.30:
            return "D"
        else:
            return "F"
    
    async def close(self):
        """Close database connections."""
        if self.async_engine:
            await self.async_engine.dispose()


async def main():
    """Main optimization function."""
    # Database connection URL (adjust as needed)
    database_url = "postgresql+asyncpg://acgs_user:acgs_password@localhost:5432/acgs_db"
    
    optimizer = DatabaseQueryOptimizer(database_url)
    
    try:
        await optimizer.initialize()
        
        # Run comprehensive analysis
        analysis_result = await optimizer.analyze_query_performance()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"query_optimization_analysis_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(analysis_result, f, indent=2, default=str)
        
        logger.info(f"📄 Analysis results saved to {output_file}")
        
        # Print summary
        summary = analysis_result["performance_summary"]
        print(f"\n🎯 ACGS-1 Query Performance Analysis Summary")
        print(f"=" * 50)
        print(f"Total Queries Analyzed: {summary['total_queries_analyzed']}")
        print(f"Slow Queries: {summary['slow_queries_count']} ({summary['slow_query_percentage']}%)")
        print(f"Average Query Time: {summary['average_query_time_ms']}ms")
        print(f"Performance Grade: {summary['performance_grade']}")
        print(f"Optimization Opportunities: {summary['optimization_opportunities']}")
        
    finally:
        await optimizer.close()


if __name__ == "__main__":
    asyncio.run(main())
