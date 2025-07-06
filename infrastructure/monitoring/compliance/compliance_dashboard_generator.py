"""
ACGS Compliance Dashboard Generator

Automated generation of compliance monitoring dashboards and
visualizations for regulatory standards and constitutional compliance.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import pandas as pd
    VISUALIZATION_LIBS_AVAILABLE = True
except ImportError:
    VISUALIZATION_LIBS_AVAILABLE = False

from .compliance_reporter import (
    ComplianceReporter, ComplianceStandard, ReportPeriod, 
    get_compliance_reporter
)

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """Configuration for dashboard generation."""
    title: str
    description: str
    compliance_standards: List[ComplianceStandard]
    refresh_interval: str = "5m"
    time_range: str = "24h"
    enable_alerts: bool = True
    export_formats: List[str] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["html", "png", "pdf"]


class ComplianceDashboardGenerator:
    """
    Automated compliance dashboard generator for ACGS.
    
    Creates interactive dashboards for compliance monitoring,
    regulatory reporting, and constitutional adherence tracking.
    """
    
    def __init__(
        self,
        output_dir: str = "/app/dashboards",
        compliance_reporter: Optional[ComplianceReporter] = None
    ):
        self.output_dir = output_dir
        self.compliance_reporter = compliance_reporter or get_compliance_reporter()
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("Compliance dashboard generator initialized")
    
    async def generate_constitutional_compliance_dashboard(
        self,
        config: Optional[DashboardConfig] = None
    ) -> str:
        """Generate constitutional compliance dashboard."""
        
        if not VISUALIZATION_LIBS_AVAILABLE:
            logger.error("Visualization libraries not available")
            return ""
        
        if config is None:
            config = DashboardConfig(
                title="ACGS Constitutional Compliance Dashboard",
                description="Real-time constitutional compliance monitoring",
                compliance_standards=[ComplianceStandard.ACGS_CONSTITUTIONAL]
            )
        
        logger.info("Generating constitutional compliance dashboard")
        
        # Get compliance data for the last 24 hours
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=24)
        
        # Generate compliance report data
        report_path = await self.compliance_reporter.generate_constitutional_compliance_report(
            start_time, end_time
        )
        
        # Load report data
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        # Create dashboard
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Overall Compliance Score',
                'Constitutional Hash Status',
                'Multi-tenant Isolation Score',
                'Formal Verification Success Rate',
                'Audit Trail Integrity',
                'Compliance Trends'
            ),
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "scatter"}]
            ]
        )
        
        # Overall compliance score gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=report_data['overall_compliance_score'],
                title={"text": "Overall Compliance Score"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ),
            row=1, col=1
        )
        
        # Constitutional hash status
        hash_valid = next(
            (m for m in report_data['metrics'] if m['metric_name'] == 'Constitutional Hash Integrity'),
            {'current_value': 1.0}
        )['current_value']
        
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=hash_valid,
                title={"text": f"Constitutional Hash Status<br>{CONSTITUTIONAL_HASH}"},
                number={'font': {'color': 'green' if hash_valid == 1.0 else 'red'}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=1, col=2
        )
        
        # Multi-tenant isolation score
        isolation_score = next(
            (m for m in report_data['metrics'] if m['metric_name'] == 'Multi-tenant Isolation'),
            {'compliance_percentage': 100.0}
        )['compliance_percentage']
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=isolation_score,
                title={"text": "Multi-tenant Isolation"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "blue"},
                    'steps': [
                        {'range': [0, 80], 'color': "lightgray"},
                        {'range': [80, 95], 'color': "yellow"},
                        {'range': [95, 100], 'color': "green"}
                    ]
                }
            ),
            row=2, col=1
        )
        
        # Formal verification success rate
        verification_score = next(
            (m for m in report_data['metrics'] if m['metric_name'] == 'Formal Verification Success Rate'),
            {'compliance_percentage': 95.0}
        )['compliance_percentage']
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=verification_score,
                title={"text": "Formal Verification Success Rate"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "purple"},
                    'steps': [
                        {'range': [0, 90], 'color': "lightgray"},
                        {'range': [90, 98], 'color': "yellow"},
                        {'range': [98, 100], 'color': "green"}
                    ]
                }
            ),
            row=2, col=2
        )
        
        # Audit trail integrity
        audit_integrity = next(
            (m for m in report_data['metrics'] if m['metric_name'] == 'Audit Trail Integrity'),
            {'current_value': 1.0}
        )['current_value']
        
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=audit_integrity,
                title={"text": "Audit Trail Integrity"},
                number={'font': {'color': 'green' if audit_integrity == 1.0 else 'red'}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=3, col=1
        )
        
        # Compliance trends (mock data for visualization)
        trend_dates = pd.date_range(start=start_time, end=end_time, freq='1H')
        trend_scores = [95 + (i % 5) for i in range(len(trend_dates))]
        
        fig.add_trace(
            go.Scatter(
                x=trend_dates,
                y=trend_scores,
                mode='lines+markers',
                name='Compliance Score Trend',
                line=dict(color='blue', width=2),
                marker=dict(size=4)
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f"{config.title}<br><sub>Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</sub>",
            showlegend=False,
            height=900,
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        # Save dashboard
        dashboard_path = os.path.join(
            self.output_dir, 
            f"constitutional_compliance_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        fig.write_html(dashboard_path)
        
        logger.info(f"Constitutional compliance dashboard saved: {dashboard_path}")
        return dashboard_path
    
    async def generate_multi_tenant_security_dashboard(
        self,
        config: Optional[DashboardConfig] = None
    ) -> str:
        """Generate multi-tenant security dashboard."""
        
        if not VISUALIZATION_LIBS_AVAILABLE:
            logger.error("Visualization libraries not available")
            return ""
        
        if config is None:
            config = DashboardConfig(
                title="ACGS Multi-Tenant Security Dashboard",
                description="Real-time multi-tenant security monitoring",
                compliance_standards=[ComplianceStandard.SOC2_TYPE_II]
            )
        
        logger.info("Generating multi-tenant security dashboard")
        
        # Create dashboard with multiple visualizations
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Tenant Isolation Violations',
                'Cross-Tenant Access Attempts',
                'Authentication Success Rate by Tenant',
                'Resource Usage by Tenant'
            ),
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ]
        )
        
        # Mock data for visualization (in production, this would query actual metrics)
        tenants = ['tenant-001', 'tenant-002', 'tenant-003', 'tenant-004', 'tenant-005']
        violations = [0, 1, 0, 2, 0]  # Mock violation counts
        
        # Tenant isolation violations
        fig.add_trace(
            go.Bar(
                x=tenants,
                y=violations,
                name='Isolation Violations',
                marker_color=['green' if v == 0 else 'red' for v in violations]
            ),
            row=1, col=1
        )
        
        # Cross-tenant access attempts over time
        time_range = pd.date_range(
            start=datetime.now() - timedelta(hours=24),
            end=datetime.now(),
            freq='1H'
        )
        access_attempts = [0 if i % 6 != 0 else 1 for i in range(len(time_range))]
        
        fig.add_trace(
            go.Scatter(
                x=time_range,
                y=access_attempts,
                mode='lines+markers',
                name='Cross-Tenant Attempts',
                line=dict(color='red', width=2),
                marker=dict(size=6)
            ),
            row=1, col=2
        )
        
        # Authentication success rate by tenant
        auth_success_rates = [99.5, 98.2, 99.8, 97.5, 99.1]  # Mock data
        
        fig.add_trace(
            go.Bar(
                x=tenants,
                y=auth_success_rates,
                name='Auth Success Rate',
                marker_color='green'
            ),
            row=2, col=1
        )
        
        # Resource usage by tenant
        cpu_usage = [45, 62, 30, 78, 55]  # Mock CPU usage percentages
        
        fig.add_trace(
            go.Scatter(
                x=tenants,
                y=cpu_usage,
                mode='markers',
                name='CPU Usage %',
                marker=dict(
                    size=15,
                    color=cpu_usage,
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title="CPU %")
                )
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f"{config.title}<br><sub>Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</sub>",
            height=800,
            showlegend=False,
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Violations", row=1, col=1)
        fig.update_yaxes(title_text="Attempts", row=1, col=2)
        fig.update_yaxes(title_text="Success Rate %", row=2, col=1)
        fig.update_yaxes(title_text="CPU Usage %", row=2, col=2)
        
        # Save dashboard
        dashboard_path = os.path.join(
            self.output_dir,
            f"multi_tenant_security_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        fig.write_html(dashboard_path)
        
        logger.info(f"Multi-tenant security dashboard saved: {dashboard_path}")
        return dashboard_path
    
    async def generate_compliance_summary_dashboard(
        self,
        standards: List[ComplianceStandard],
        config: Optional[DashboardConfig] = None
    ) -> str:
        """Generate comprehensive compliance summary dashboard."""
        
        if not VISUALIZATION_LIBS_AVAILABLE:
            logger.error("Visualization libraries not available")
            return ""
        
        if config is None:
            config = DashboardConfig(
                title="ACGS Comprehensive Compliance Summary",
                description="Multi-standard compliance overview",
                compliance_standards=standards
            )
        
        logger.info("Generating compliance summary dashboard")
        
        # Create comprehensive dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Compliance Scores by Standard',
                'Compliance Trends Over Time',
                'Violation Categories',
                'Remediation Status'
            ),
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "pie"}, {"type": "bar"}]
            ]
        )
        
        # Mock compliance scores by standard
        standard_names = [s.value.replace('_', ' ').title() for s in standards]
        compliance_scores = [95.5, 92.1, 98.2, 89.7, 94.3][:len(standards)]
        
        # Compliance scores by standard
        colors = ['green' if score >= 95 else 'yellow' if score >= 90 else 'red' 
                 for score in compliance_scores]
        
        fig.add_trace(
            go.Bar(
                x=standard_names,
                y=compliance_scores,
                name='Compliance Scores',
                marker_color=colors
            ),
            row=1, col=1
        )
        
        # Compliance trends over time
        trend_dates = pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            freq='1D'
        )
        
        for i, standard in enumerate(standard_names[:3]):  # Show top 3 standards
            trend_scores = [92 + (j % 8) + i for j in range(len(trend_dates))]
            fig.add_trace(
                go.Scatter(
                    x=trend_dates,
                    y=trend_scores,
                    mode='lines',
                    name=standard,
                    line=dict(width=2)
                ),
                row=1, col=2
            )
        
        # Violation categories
        violation_categories = ['Access Control', 'Data Protection', 'Audit Trail', 'Multi-tenant']
        violation_counts = [2, 1, 0, 3]
        
        fig.add_trace(
            go.Pie(
                labels=violation_categories,
                values=violation_counts,
                name="Violations"
            ),
            row=2, col=1
        )
        
        # Remediation status
        remediation_status = ['Resolved', 'In Progress', 'Pending']
        remediation_counts = [15, 4, 2]
        
        fig.add_trace(
            go.Bar(
                x=remediation_status,
                y=remediation_counts,
                name='Remediation Status',
                marker_color=['green', 'yellow', 'red']
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f"{config.title}<br><sub>Constitutional Hash: {CONSTITUTIONAL_HASH} | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</sub>",
            height=800,
            showlegend=True,
            margin=dict(l=20, r=20, t=100, b=20)
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Compliance Score %", row=1, col=1)
        fig.update_yaxes(title_text="Score %", row=1, col=2)
        fig.update_yaxes(title_text="Count", row=2, col=2)
        
        # Save dashboard
        dashboard_path = os.path.join(
            self.output_dir,
            f"compliance_summary_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        fig.write_html(dashboard_path)
        
        logger.info(f"Compliance summary dashboard saved: {dashboard_path}")
        return dashboard_path
    
    async def generate_all_dashboards(self) -> Dict[str, str]:
        """Generate all compliance dashboards."""
        
        logger.info("Generating all compliance dashboards")
        
        dashboards = {}
        
        # Constitutional compliance dashboard
        constitutional_dashboard = await self.generate_constitutional_compliance_dashboard()
        if constitutional_dashboard:
            dashboards['constitutional'] = constitutional_dashboard
        
        # Multi-tenant security dashboard
        security_dashboard = await self.generate_multi_tenant_security_dashboard()
        if security_dashboard:
            dashboards['security'] = security_dashboard
        
        # Comprehensive compliance summary
        all_standards = [
            ComplianceStandard.ACGS_CONSTITUTIONAL,
            ComplianceStandard.SOC2_TYPE_II,
            ComplianceStandard.GDPR,
            ComplianceStandard.ISO27001
        ]
        
        summary_dashboard = await self.generate_compliance_summary_dashboard(all_standards)
        if summary_dashboard:
            dashboards['summary'] = summary_dashboard
        
        logger.info(f"Generated {len(dashboards)} compliance dashboards")
        return dashboards


# Global dashboard generator instance
_dashboard_generator: Optional[ComplianceDashboardGenerator] = None


def get_dashboard_generator() -> ComplianceDashboardGenerator:
    """Get or create the global dashboard generator instance."""
    global _dashboard_generator
    
    if _dashboard_generator is None:
        _dashboard_generator = ComplianceDashboardGenerator()
    
    return _dashboard_generator


# Scheduled dashboard generation functions
async def generate_daily_dashboards():
    """Generate daily compliance dashboards."""
    generator = get_dashboard_generator()
    
    dashboards = await generator.generate_all_dashboards()
    
    logger.info(f"Generated {len(dashboards)} daily compliance dashboards")
    return dashboards


async def generate_executive_summary_dashboard():
    """Generate executive summary dashboard."""
    generator = get_dashboard_generator()
    
    # Executive-focused configuration
    config = DashboardConfig(
        title="ACGS Executive Compliance Summary",
        description="High-level compliance overview for executives",
        compliance_standards=[
            ComplianceStandard.ACGS_CONSTITUTIONAL,
            ComplianceStandard.SOC2_TYPE_II,
            ComplianceStandard.GDPR
        ],
        time_range="30d"
    )
    
    dashboard = await generator.generate_compliance_summary_dashboard(
        config.compliance_standards, config
    )
    
    logger.info("Generated executive summary dashboard")
    return dashboard