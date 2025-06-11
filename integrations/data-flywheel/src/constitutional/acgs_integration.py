"""
ACGS-1 Service Integration for Data Flywheel

This module provides integration with ACGS-1 constitutional governance services,
enabling the Data Flywheel to collect governance traffic, validate constitutional
compliance, and optimize governance models while maintaining constitutional adherence.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

import httpx
import yaml
from elasticsearch import Elasticsearch
from pydantic import BaseModel


@dataclass
class GovernanceTrafficLog:
    """Governance traffic log entry for Data Flywheel processing"""
    timestamp: int
    workload_id: str
    client_id: str
    service_name: str
    request: Dict[str, Any]
    response: Dict[str, Any]
    constitutional_context: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class ACGSServiceIntegration:
    """
    Integration layer between ACGS-1 constitutional governance services
    and the Data Flywheel optimization system.
    """
    
    def __init__(self, config_path: str = "config/acgs_config.yaml"):
        """Initialize ACGS-1 service integration"""
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
        # ACGS-1 service configuration
        self.acgs_config = self.config.get("acgs_config", {})
        self.base_url = self.acgs_config.get("base_url", "http://localhost")
        self.services = self.acgs_config.get("services", {})
        
        # Constitutional configuration
        self.constitutional_config = self.config.get("constitutional_config", {})
        
        # Governance flywheel configuration
        self.governance_config = self.config.get("governance_flywheel_config", {})
        self.workload_mapping = self.governance_config.get("workload_mapping", {})
        
        # Initialize Elasticsearch for governance traffic logging
        self.es_client = None
        self._init_elasticsearch()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load ACGS-1 configuration"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config from {config_path}: {e}")
            return {}
    
    def _init_elasticsearch(self):
        """Initialize Elasticsearch client for governance traffic logging"""
        try:
            es_url = self.config.get("elasticsearch_url", "http://localhost:9200")
            self.es_client = Elasticsearch([es_url])
            
            # Create governance traffic index if it doesn't exist
            index_name = "acgs_governance_traffic"
            if not self.es_client.indices.exists(index=index_name):
                self.es_client.indices.create(
                    index=index_name,
                    body={
                        "mappings": {
                            "properties": {
                                "timestamp": {"type": "date"},
                                "workload_id": {"type": "keyword"},
                                "client_id": {"type": "keyword"},
                                "service_name": {"type": "keyword"},
                                "request": {"type": "object"},
                                "response": {"type": "object"},
                                "constitutional_context": {"type": "object"},
                                "performance_metrics": {"type": "object"}
                            }
                        }
                    }
                )
                self.logger.info(f"Created Elasticsearch index: {index_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Elasticsearch: {e}")
            self.es_client = None
    
    async def collect_governance_traffic(
        self,
        time_range: timedelta = timedelta(hours=24),
        workload_filter: Optional[List[str]] = None
    ) -> List[GovernanceTrafficLog]:
        """
        Collect governance traffic from ACGS-1 services for Data Flywheel processing
        
        Args:
            time_range: Time range for traffic collection
            workload_filter: Optional filter for specific workload types
            
        Returns:
            List of governance traffic logs
        """
        self.logger.info(f"Collecting governance traffic for the last {time_range}")
        
        traffic_logs = []
        
        # Collect traffic from each ACGS-1 service
        for service_name, service_config in self.services.items():
            if not service_config.get("required", False):
                continue
                
            try:
                service_logs = await self._collect_service_traffic(
                    service_name, service_config, time_range, workload_filter
                )
                traffic_logs.extend(service_logs)
                
            except Exception as e:
                self.logger.error(f"Failed to collect traffic from {service_name}: {e}")
        
        self.logger.info(f"Collected {len(traffic_logs)} governance traffic logs")
        return traffic_logs
    
    async def _collect_service_traffic(
        self,
        service_name: str,
        service_config: Dict,
        time_range: timedelta,
        workload_filter: Optional[List[str]]
    ) -> List[GovernanceTrafficLog]:
        """Collect traffic from a specific ACGS-1 service"""
        
        port = service_config.get("port")
        service_url = f"{self.base_url}:{port}"
        
        try:
            async with httpx.AsyncClient() as client:
                # Request traffic logs from the service
                response = await client.get(
                    f"{service_url}/api/v1/traffic/logs",
                    params={
                        "time_range_hours": int(time_range.total_seconds() / 3600),
                        "workload_filter": workload_filter or []
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logs_data = response.json()
                    return self._parse_service_logs(service_name, logs_data)
                else:
                    self.logger.warning(f"Failed to get logs from {service_name}: {response.status_code}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error collecting traffic from {service_name}: {e}")
            return []
    
    def _parse_service_logs(self, service_name: str, logs_data: Dict) -> List[GovernanceTrafficLog]:
        """Parse service logs into GovernanceTrafficLog objects"""
        traffic_logs = []
        
        for log_entry in logs_data.get("logs", []):
            try:
                traffic_log = GovernanceTrafficLog(
                    timestamp=log_entry.get("timestamp", 0),
                    workload_id=log_entry.get("workload_id", "unknown"),
                    client_id=log_entry.get("client_id", "acgs_governance"),
                    service_name=service_name,
                    request=log_entry.get("request", {}),
                    response=log_entry.get("response", {}),
                    constitutional_context=log_entry.get("constitutional_context", {}),
                    performance_metrics=log_entry.get("performance_metrics", {})
                )
                traffic_logs.append(traffic_log)
                
            except Exception as e:
                self.logger.error(f"Failed to parse log entry: {e}")
                continue
        
        return traffic_logs
    
    async def log_governance_interaction(
        self,
        workload_id: str,
        service_name: str,
        request_data: Dict,
        response_data: Dict,
        constitutional_context: Optional[Dict] = None,
        performance_metrics: Optional[Dict] = None
    ):
        """
        Log a governance interaction for Data Flywheel processing
        
        Args:
            workload_id: Identifier for the governance workload
            service_name: Name of the ACGS-1 service
            request_data: Request data
            response_data: Response data
            constitutional_context: Constitutional context information
            performance_metrics: Performance metrics
        """
        if not self.es_client:
            self.logger.warning("Elasticsearch not available for logging")
            return
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "workload_id": workload_id,
            "client_id": "acgs_governance",
            "service_name": service_name,
            "request": request_data,
            "response": response_data,
            "constitutional_context": constitutional_context or {},
            "performance_metrics": performance_metrics or {}
        }
        
        try:
            self.es_client.index(
                index="acgs_governance_traffic",
                body=log_entry
            )
            self.logger.debug(f"Logged governance interaction: {workload_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to log governance interaction: {e}")
    
    async def validate_service_health(self) -> Dict[str, bool]:
        """Validate health of all ACGS-1 services"""
        health_status = {}
        
        for service_name, service_config in self.services.items():
            port = service_config.get("port")
            endpoint = service_config.get("endpoint", "/health")
            url = f"{self.base_url}:{port}{endpoint}"
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=5.0)
                    health_status[service_name] = response.status_code == 200
                    
            except Exception as e:
                self.logger.error(f"Health check failed for {service_name}: {e}")
                health_status[service_name] = False
        
        return health_status
    
    async def get_constitutional_context(self, workload_id: str) -> Dict[str, Any]:
        """
        Get constitutional context for a specific governance workload
        
        Args:
            workload_id: Identifier for the governance workload
            
        Returns:
            Constitutional context information
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}:8001/api/v1/constitutional/context/{workload_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"Failed to get constitutional context: {response.status_code}")
                    
        except Exception as e:
            self.logger.error(f"Error getting constitutional context: {e}")
        
        # Return default constitutional context
        return {
            "principles": self.constitutional_config.get("principles", []),
            "compliance_threshold": self.constitutional_config.get("compliance_threshold", 0.95),
            "validation_required": self.constitutional_config.get("validation_required", True)
        }
    
    async def notify_optimization_result(
        self,
        workload_id: str,
        optimization_result: Dict[str, Any],
        constitutional_compliance: Dict[str, Any]
    ):
        """
        Notify ACGS-1 services about Data Flywheel optimization results
        
        Args:
            workload_id: Identifier for the governance workload
            optimization_result: Results from Data Flywheel optimization
            constitutional_compliance: Constitutional compliance validation results
        """
        notification_data = {
            "workload_id": workload_id,
            "optimization_result": optimization_result,
            "constitutional_compliance": constitutional_compliance,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Notify relevant services based on workload type
        service_mapping = self.workload_mapping.get(workload_id, "gs_service")
        
        if service_mapping in self.services:
            service_config = self.services[service_mapping]
            port = service_config.get("port")
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}:{port}/api/v1/flywheel/optimization_result",
                        json=notification_data,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        self.logger.info(f"Notified {service_mapping} of optimization result")
                    else:
                        self.logger.warning(f"Failed to notify {service_mapping}: {response.status_code}")
                        
            except Exception as e:
                self.logger.error(f"Error notifying {service_mapping}: {e}")
    
    def get_workload_service_mapping(self) -> Dict[str, str]:
        """Get mapping of governance workloads to ACGS-1 services"""
        return self.workload_mapping.copy()
    
    def get_optimization_targets(self) -> Dict[str, float]:
        """Get optimization targets for governance models"""
        return self.governance_config.get("optimization_targets", {})
    
    def get_evaluation_criteria(self) -> Dict[str, float]:
        """Get evaluation criteria weights for governance models"""
        return self.governance_config.get("evaluation_criteria", {})
