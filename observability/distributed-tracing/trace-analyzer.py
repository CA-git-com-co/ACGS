#!/usr/bin/env python3
"""
ACGS-2 Distributed Trace Analyzer
Constitutional Hash: cdd01ef066bc6cf2

Advanced trace analysis system for ACGS-2 with constitutional compliance monitoring,
performance analysis, and anomaly detection.
"""

import asyncio
import json
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
import aiohttp
import numpy as np
from elasticsearch import AsyncElasticsearch
from jaeger_client import Config as JaegerConfig
from opentelemetry.trace import Status, StatusCode

class AnalysisType(Enum):
    """Types of trace analysis"""
    PERFORMANCE = "performance"
    CONSTITUTIONAL = "constitutional"
    SECURITY = "security"
    ANOMALY = "anomaly"
    DEPENDENCY = "dependency"
    ERROR = "error"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class TraceSpan:
    """Trace span data structure"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: int
    duration: int
    status: str
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]
    process: Dict[str, Any]
    
    @property
    def constitutional_hash(self) -> Optional[str]:
        """Get constitutional hash from tags"""
        return self.tags.get("constitutional_hash")
    
    @property
    def is_constitutional_compliant(self) -> bool:
        """Check if span is constitutionally compliant"""
        return self.constitutional_hash == "cdd01ef066bc6cf2"
    
    @property
    def duration_ms(self) -> float:
        """Get duration in milliseconds"""
        return self.duration / 1000.0
    
    @property
    def is_error(self) -> bool:
        """Check if span has error status"""
        return self.status == "error" or self.tags.get("error", False)
    
    @property
    def is_high_latency(self) -> bool:
        """Check if span exceeds P99 latency threshold (5ms)"""
        return self.duration_ms > 5.0

@dataclass
class TraceAnalysisResult:
    """Trace analysis result"""
    trace_id: str
    analysis_type: AnalysisType
    severity: AlertSeverity
    title: str
    description: str
    metrics: Dict[str, Any]
    recommendations: List[str]
    affected_services: List[str]
    constitutional_compliance: bool
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "trace_id": self.trace_id,
            "analysis_type": self.analysis_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "metrics": self.metrics,
            "recommendations": self.recommendations,
            "affected_services": self.affected_services,
            "constitutional_compliance": self.constitutional_compliance,
            "timestamp": self.timestamp.isoformat()
        }

class ACGSTraceAnalyzer:
    """
    ACGS-2 Distributed Trace Analyzer
    Constitutional Hash: cdd01ef066bc6cf2
    
    Analyzes distributed traces for:
    - Constitutional compliance violations
    - Performance anomalies
    - Security issues
    - Service dependencies
    - Error patterns
    """
    
    def __init__(self, 
                 jaeger_query_url: str = "http://jaeger-query.jaeger-system.svc.cluster.local:16686",
                 elasticsearch_url: str = "http://elasticsearch.jaeger-system.svc.cluster.local:9200",
                 constitutional_hash: str = "cdd01ef066bc6cf2"):
        
        self.jaeger_query_url = jaeger_query_url
        self.elasticsearch_url = elasticsearch_url
        self.constitutional_hash = constitutional_hash
        self.logger = self._setup_logging()
        
        # Analysis configuration
        self.analysis_config = {
            "performance_thresholds": {
                "p50_latency_ms": 1.0,
                "p95_latency_ms": 3.0,
                "p99_latency_ms": 5.0,
                "error_rate_threshold": 0.05,
                "throughput_threshold": 100
            },
            "constitutional_requirements": {
                "hash_validation": True,
                "compliance_tracking": True,
                "violation_alerting": True
            },
            "anomaly_detection": {
                "enabled": True,
                "window_size": 100,
                "deviation_threshold": 2.0,
                "min_samples": 10
            }
        }
        
        # Initialize clients
        self.es_client = AsyncElasticsearch([elasticsearch_url])
        self.session = None
        
        # Analysis state
        self.trace_cache = {}
        self.performance_history = defaultdict(lambda: deque(maxlen=1000))
        self.constitutional_violations = deque(maxlen=1000)
        self.anomaly_baselines = defaultdict(dict)
        
        # Analysis results
        self.analysis_results = deque(maxlen=10000)
        self.alert_history = deque(maxlen=1000)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for trace analyzer"""
        logger = logging.getLogger("acgs_trace_analyzer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - CONSTITUTIONAL_HASH:{self.constitutional_hash} - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def initialize(self):
        """Initialize analyzer"""
        self.session = aiohttp.ClientSession()
        
        # Initialize Elasticsearch index template
        await self._create_analysis_index_template()
        
        self.logger.info("✅ Trace analyzer initialized")
    
    async def _create_analysis_index_template(self):
        """Create Elasticsearch index template for analysis results"""
        template = {
            "index_patterns": ["acgs-trace-analysis-*"],
            "template": {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "refresh_interval": "30s"
                },
                "mappings": {
                    "properties": {
                        "trace_id": {"type": "keyword"},
                        "analysis_type": {"type": "keyword"},
                        "severity": {"type": "keyword"},
                        "title": {"type": "text"},
                        "description": {"type": "text"},
                        "constitutional_compliance": {"type": "boolean"},
                        "affected_services": {"type": "keyword"},
                        "metrics": {"type": "object"},
                        "recommendations": {"type": "text"},
                        "timestamp": {"type": "date"},
                        "constitutional_hash": {"type": "keyword"}
                    }
                }
            }
        }
        
        try:
            await self.es_client.indices.put_index_template(
                name="acgs-trace-analysis",
                body=template
            )
            self.logger.info("✅ Created Elasticsearch index template")
        except Exception as e:
            self.logger.error(f"❌ Failed to create index template: {e}")
    
    async def fetch_traces(self, 
                          service_name: Optional[str] = None,
                          operation_name: Optional[str] = None,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          limit: int = 100) -> List[TraceSpan]:
        """
        Fetch traces from Jaeger
        
        Args:
            service_name: Service name filter
            operation_name: Operation name filter
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of traces to fetch
        
        Returns:
            List of TraceSpan objects
        """
        params = {
            "limit": limit,
            "lookback": "1h"
        }
        
        if service_name:
            params["service"] = service_name
        if operation_name:
            params["operation"] = operation_name
        if start_time:
            params["start"] = int(start_time.timestamp() * 1000000)
        if end_time:
            params["end"] = int(end_time.timestamp() * 1000000)
        
        try:
            url = f"{self.jaeger_query_url}/api/traces"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    traces = []
                    
                    for trace_data in data.get("data", []):
                        for span_data in trace_data.get("spans", []):
                            span = self._parse_span_data(span_data)
                            traces.append(span)
                    
                    return traces
                else:
                    self.logger.error(f"❌ Failed to fetch traces: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"❌ Error fetching traces: {e}")
            return []
    
    def _parse_span_data(self, span_data: Dict[str, Any]) -> TraceSpan:
        """Parse Jaeger span data into TraceSpan object"""
        tags = {}
        for tag in span_data.get("tags", []):
            tags[tag.get("key")] = tag.get("value")
        
        logs = span_data.get("logs", [])
        process = span_data.get("process", {})
        
        return TraceSpan(
            trace_id=span_data.get("traceID"),
            span_id=span_data.get("spanID"),
            parent_span_id=span_data.get("parentSpanID"),
            operation_name=span_data.get("operationName"),
            service_name=process.get("serviceName", "unknown"),
            start_time=span_data.get("startTime", 0),
            duration=span_data.get("duration", 0),
            status="error" if any(tag.get("key") == "error" for tag in span_data.get("tags", [])) else "ok",
            tags=tags,
            logs=logs,
            process=process
        )
    
    async def analyze_constitutional_compliance(self, traces: List[TraceSpan]) -> List[TraceAnalysisResult]:
        """
        Analyze constitutional compliance of traces
        
        Args:
            traces: List of TraceSpan objects
            
        Returns:
            List of TraceAnalysisResult objects
        """
        results = []
        
        for trace in traces:
            # Check constitutional hash compliance
            if not trace.is_constitutional_compliant:
                result = TraceAnalysisResult(
                    trace_id=trace.trace_id,
                    analysis_type=AnalysisType.CONSTITUTIONAL,
                    severity=AlertSeverity.CRITICAL,
                    title="Constitutional Hash Violation",
                    description=f"Trace {trace.trace_id} missing or invalid constitutional hash",
                    metrics={
                        "expected_hash": self.constitutional_hash,
                        "actual_hash": trace.constitutional_hash,
                        "service": trace.service_name,
                        "operation": trace.operation_name
                    },
                    recommendations=[
                        "Verify constitutional hash injection in service instrumentation",
                        "Check service mesh configuration for header propagation",
                        "Review authentication and authorization policies"
                    ],
                    affected_services=[trace.service_name],
                    constitutional_compliance=False,
                    timestamp=datetime.now()
                )
                results.append(result)
                self.constitutional_violations.append(result)
        
        return results
    
    async def analyze_performance(self, traces: List[TraceSpan]) -> List[TraceAnalysisResult]:
        """
        Analyze performance characteristics of traces
        
        Args:
            traces: List of TraceSpan objects
            
        Returns:
            List of TraceAnalysisResult objects
        """
        results = []
        
        # Group traces by service and operation
        service_traces = defaultdict(list)
        for trace in traces:
            key = f"{trace.service_name}:{trace.operation_name}"
            service_traces[key].append(trace)
        
        # Analyze each service/operation group
        for service_op, trace_group in service_traces.items():
            if len(trace_group) < 5:  # Need minimum samples
                continue
                
            service_name, operation_name = service_op.split(":", 1)
            durations = [trace.duration_ms for trace in trace_group]
            
            # Calculate performance metrics
            p50 = statistics.median(durations)
            p95 = np.percentile(durations, 95)
            p99 = np.percentile(durations, 99)
            mean_duration = statistics.mean(durations)
            error_rate = sum(1 for trace in trace_group if trace.is_error) / len(trace_group)
            
            # Check thresholds
            thresholds = self.analysis_config["performance_thresholds"]
            
            # P99 latency check
            if p99 > thresholds["p99_latency_ms"]:
                result = TraceAnalysisResult(
                    trace_id=trace_group[0].trace_id,
                    analysis_type=AnalysisType.PERFORMANCE,
                    severity=AlertSeverity.WARNING if p99 < thresholds["p99_latency_ms"] * 2 else AlertSeverity.ERROR,
                    title="High P99 Latency",
                    description=f"P99 latency ({p99:.2f}ms) exceeds threshold ({thresholds['p99_latency_ms']}ms)",
                    metrics={
                        "p50_latency_ms": p50,
                        "p95_latency_ms": p95,
                        "p99_latency_ms": p99,
                        "mean_latency_ms": mean_duration,
                        "sample_count": len(trace_group),
                        "error_rate": error_rate
                    },
                    recommendations=[
                        "Review service performance bottlenecks",
                        "Check database query optimization",
                        "Verify resource allocation and scaling",
                        "Implement caching strategies"
                    ],
                    affected_services=[service_name],
                    constitutional_compliance=all(trace.is_constitutional_compliant for trace in trace_group),
                    timestamp=datetime.now()
                )
                results.append(result)
            
            # Error rate check
            if error_rate > thresholds["error_rate_threshold"]:
                result = TraceAnalysisResult(
                    trace_id=trace_group[0].trace_id,
                    analysis_type=AnalysisType.ERROR,
                    severity=AlertSeverity.ERROR,
                    title="High Error Rate",
                    description=f"Error rate ({error_rate:.2%}) exceeds threshold ({thresholds['error_rate_threshold']:.2%})",
                    metrics={
                        "error_rate": error_rate,
                        "total_traces": len(trace_group),
                        "error_traces": sum(1 for trace in trace_group if trace.is_error),
                        "service": service_name,
                        "operation": operation_name
                    },
                    recommendations=[
                        "Investigate error patterns and root causes",
                        "Review service dependencies and circuit breakers",
                        "Check authentication and authorization flows",
                        "Verify external API integrations"
                    ],
                    affected_services=[service_name],
                    constitutional_compliance=all(trace.is_constitutional_compliant for trace in trace_group),
                    timestamp=datetime.now()
                )
                results.append(result)
        
        return results
    
    async def analyze_security(self, traces: List[TraceSpan]) -> List[TraceAnalysisResult]:
        """
        Analyze security aspects of traces
        
        Args:
            traces: List of TraceSpan objects
            
        Returns:
            List of TraceAnalysisResult objects
        """
        results = []
        
        for trace in traces:
            security_issues = []
            
            # Check for missing authentication
            if not trace.tags.get("user.id") and not trace.tags.get("service_account"):
                security_issues.append("Missing authentication information")
            
            # Check for insecure communications
            if trace.tags.get("tls_version") is None and trace.service_name not in ["health-check", "metrics"]:
                security_issues.append("Potentially insecure communication")
            
            # Check for unauthorized access attempts
            if trace.tags.get("http.status_code") == "403":
                security_issues.append("Unauthorized access attempt")
            
            # Check for suspicious patterns
            if trace.duration_ms > 1000:  # Very slow operations might indicate attacks
                security_issues.append("Unusually slow operation (potential DoS)")
            
            if security_issues:
                result = TraceAnalysisResult(
                    trace_id=trace.trace_id,
                    analysis_type=AnalysisType.SECURITY,
                    severity=AlertSeverity.WARNING,
                    title="Security Issues Detected",
                    description="; ".join(security_issues),
                    metrics={
                        "service": trace.service_name,
                        "operation": trace.operation_name,
                        "duration_ms": trace.duration_ms,
                        "status_code": trace.tags.get("http.status_code"),
                        "user_id": trace.tags.get("user.id"),
                        "issues": security_issues
                    },
                    recommendations=[
                        "Review authentication and authorization policies",
                        "Ensure TLS encryption for all communications",
                        "Implement rate limiting and DDoS protection",
                        "Monitor for unauthorized access patterns"
                    ],
                    affected_services=[trace.service_name],
                    constitutional_compliance=trace.is_constitutional_compliant,
                    timestamp=datetime.now()
                )
                results.append(result)
        
        return results
    
    async def detect_anomalies(self, traces: List[TraceSpan]) -> List[TraceAnalysisResult]:
        """
        Detect anomalies in traces using statistical analysis
        
        Args:
            traces: List of TraceSpan objects
            
        Returns:
            List of TraceAnalysisResult objects
        """
        results = []
        
        if not self.analysis_config["anomaly_detection"]["enabled"]:
            return results
        
        # Group traces by service and operation
        service_traces = defaultdict(list)
        for trace in traces:
            key = f"{trace.service_name}:{trace.operation_name}"
            service_traces[key].append(trace)
        
        # Analyze each service/operation group
        for service_op, trace_group in service_traces.items():
            if len(trace_group) < self.analysis_config["anomaly_detection"]["min_samples"]:
                continue
                
            service_name, operation_name = service_op.split(":", 1)
            durations = [trace.duration_ms for trace in trace_group]
            
            # Calculate baseline metrics
            mean_duration = statistics.mean(durations)
            std_duration = statistics.stdev(durations) if len(durations) > 1 else 0
            
            # Update baseline history
            baseline_key = f"{service_name}:{operation_name}"
            if baseline_key not in self.anomaly_baselines:
                self.anomaly_baselines[baseline_key] = {
                    "mean_history": deque(maxlen=100),
                    "std_history": deque(maxlen=100)
                }
            
            baseline = self.anomaly_baselines[baseline_key]
            baseline["mean_history"].append(mean_duration)
            baseline["std_history"].append(std_duration)
            
            # Check for anomalies if we have enough baseline data
            if len(baseline["mean_history"]) >= 10:
                historical_mean = statistics.mean(baseline["mean_history"])
                historical_std = statistics.mean(baseline["std_history"])
                
                threshold = self.analysis_config["anomaly_detection"]["deviation_threshold"]
                
                # Check if current performance deviates significantly from baseline
                if abs(mean_duration - historical_mean) > threshold * historical_std:
                    severity = AlertSeverity.WARNING
                    if abs(mean_duration - historical_mean) > threshold * 2 * historical_std:
                        severity = AlertSeverity.ERROR
                    
                    result = TraceAnalysisResult(
                        trace_id=trace_group[0].trace_id,
                        analysis_type=AnalysisType.ANOMALY,
                        severity=severity,
                        title="Performance Anomaly Detected",
                        description=f"Performance deviation detected in {service_name}:{operation_name}",
                        metrics={
                            "current_mean_ms": mean_duration,
                            "historical_mean_ms": historical_mean,
                            "deviation_factor": abs(mean_duration - historical_mean) / historical_std,
                            "sample_count": len(trace_group),
                            "service": service_name,
                            "operation": operation_name
                        },
                        recommendations=[
                            "Investigate recent changes to the service",
                            "Check for infrastructure issues",
                            "Review resource utilization",
                            "Verify dependencies are healthy"
                        ],
                        affected_services=[service_name],
                        constitutional_compliance=all(trace.is_constitutional_compliant for trace in trace_group),
                        timestamp=datetime.now()
                    )
                    results.append(result)
        
        return results
    
    async def analyze_service_dependencies(self, traces: List[TraceSpan]) -> List[TraceAnalysisResult]:
        """
        Analyze service dependencies and communication patterns
        
        Args:
            traces: List of TraceSpan objects
            
        Returns:
            List of TraceAnalysisResult objects
        """
        results = []
        
        # Group traces by trace_id to reconstruct call chains
        trace_groups = defaultdict(list)
        for trace in traces:
            trace_groups[trace.trace_id].append(trace)
        
        # Analyze each trace
        for trace_id, spans in trace_groups.items():
            # Sort spans by start time
            spans.sort(key=lambda x: x.start_time)
            
            # Build dependency graph
            dependencies = set()
            for span in spans:
                if span.parent_span_id:
                    parent_span = next((s for s in spans if s.span_id == span.parent_span_id), None)
                    if parent_span and parent_span.service_name != span.service_name:
                        dependencies.add((parent_span.service_name, span.service_name))
            
            # Check for constitutional compliance across dependencies
            non_compliant_services = [span.service_name for span in spans if not span.is_constitutional_compliant]
            
            if non_compliant_services:
                result = TraceAnalysisResult(
                    trace_id=trace_id,
                    analysis_type=AnalysisType.DEPENDENCY,
                    severity=AlertSeverity.ERROR,
                    title="Constitutional Compliance Violation in Service Chain",
                    description=f"Non-compliant services detected in dependency chain: {', '.join(set(non_compliant_services))}",
                    metrics={
                        "total_services": len(set(span.service_name for span in spans)),
                        "non_compliant_services": len(set(non_compliant_services)),
                        "dependencies": list(dependencies),
                        "trace_duration_ms": sum(span.duration_ms for span in spans)
                    },
                    recommendations=[
                        "Review service mesh configuration",
                        "Ensure constitutional headers are propagated",
                        "Check authentication policies for all services",
                        "Verify service-to-service communication security"
                    ],
                    affected_services=list(set(span.service_name for span in spans)),
                    constitutional_compliance=False,
                    timestamp=datetime.now()
                )
                results.append(result)
        
        return results
    
    async def store_analysis_results(self, results: List[TraceAnalysisResult]):
        """
        Store analysis results in Elasticsearch
        
        Args:
            results: List of TraceAnalysisResult objects
        """
        if not results:
            return
        
        index_name = f"acgs-trace-analysis-{datetime.now().strftime('%Y-%m-%d')}"
        
        try:
            for result in results:
                doc = result.to_dict()
                doc["constitutional_hash"] = self.constitutional_hash
                
                await self.es_client.index(
                    index=index_name,
                    body=doc
                )
            
            # Add to local storage
            self.analysis_results.extend(results)
            
            self.logger.info(f"✅ Stored {len(results)} analysis results")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store analysis results: {e}")
    
    async def run_comprehensive_analysis(self, 
                                       service_name: Optional[str] = None,
                                       lookback_minutes: int = 60) -> Dict[str, Any]:
        """
        Run comprehensive trace analysis
        
        Args:
            service_name: Optional service name filter
            lookback_minutes: Time window for analysis
            
        Returns:
            Analysis summary
        """
        self.logger.info(f"🔍 Starting comprehensive trace analysis (lookback: {lookback_minutes}m)")
        
        # Fetch traces
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=lookback_minutes)
        
        traces = await self.fetch_traces(
            service_name=service_name,
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )
        
        if not traces:
            self.logger.warning("⚠️ No traces found for analysis")
            return {"status": "no_traces"}
        
        self.logger.info(f"📊 Analyzing {len(traces)} traces")
        
        # Run all analyses
        all_results = []
        
        # Constitutional compliance analysis
        constitutional_results = await self.analyze_constitutional_compliance(traces)
        all_results.extend(constitutional_results)
        
        # Performance analysis
        performance_results = await self.analyze_performance(traces)
        all_results.extend(performance_results)
        
        # Security analysis
        security_results = await self.analyze_security(traces)
        all_results.extend(security_results)
        
        # Anomaly detection
        anomaly_results = await self.detect_anomalies(traces)
        all_results.extend(anomaly_results)
        
        # Dependency analysis
        dependency_results = await self.analyze_service_dependencies(traces)
        all_results.extend(dependency_results)
        
        # Store results
        await self.store_analysis_results(all_results)
        
        # Generate summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "analysis_period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": lookback_minutes
            },
            "traces_analyzed": len(traces),
            "results": {
                "total_issues": len(all_results),
                "constitutional_violations": len(constitutional_results),
                "performance_issues": len(performance_results),
                "security_issues": len(security_results),
                "anomalies": len(anomaly_results),
                "dependency_issues": len(dependency_results)
            },
            "severity_breakdown": {
                "critical": len([r for r in all_results if r.severity == AlertSeverity.CRITICAL]),
                "error": len([r for r in all_results if r.severity == AlertSeverity.ERROR]),
                "warning": len([r for r in all_results if r.severity == AlertSeverity.WARNING]),
                "info": len([r for r in all_results if r.severity == AlertSeverity.INFO])
            },
            "constitutional_compliance": {
                "compliant_traces": len([t for t in traces if t.is_constitutional_compliant]),
                "non_compliant_traces": len([t for t in traces if not t.is_constitutional_compliant]),
                "compliance_rate": len([t for t in traces if t.is_constitutional_compliant]) / len(traces) * 100
            },
            "performance_metrics": {
                "high_latency_traces": len([t for t in traces if t.is_high_latency]),
                "error_traces": len([t for t in traces if t.is_error]),
                "average_duration_ms": sum(t.duration_ms for t in traces) / len(traces)
            }
        }
        
        self.logger.info(f"✅ Analysis complete: {len(all_results)} issues found")
        
        return summary
    
    async def shutdown(self):
        """Shutdown trace analyzer"""
        if self.session:
            await self.session.close()
        if self.es_client:
            await self.es_client.close()
        
        self.logger.info("✅ Trace analyzer shutdown complete")

async def main():
    """Main function for running trace analysis"""
    analyzer = ACGSTraceAnalyzer()
    
    try:
        await analyzer.initialize()
        
        # Run comprehensive analysis
        summary = await analyzer.run_comprehensive_analysis()
        
        print("=== ACGS-2 Trace Analysis Summary ===")
        print(json.dumps(summary, indent=2))
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
    finally:
        await analyzer.shutdown()

if __name__ == "__main__":
    asyncio.run(main())