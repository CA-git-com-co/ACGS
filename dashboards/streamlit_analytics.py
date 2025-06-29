#!/usr/bin/env python3
"""
ACGS Real-Time Analytics Dashboard

Streamlit-based dashboard for real-time monitoring of ACGS platform:
- Live system performance metrics
- Data quality monitoring
- Constitutional compliance status
- Model drift detection alerts
- Service health monitoring

Constitutional Hash: cdd01ef066bc6cf2
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import time
import sys
import os

# Add ACGS modules to path
sys.path.append('../services/core/acgs-pgp-v8')

# Configure Streamlit page
st.set_page_config(
    page_title="ACGS Analytics Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constitutional hash validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# ACGS Services Configuration
ACGS_SERVICES = {
    'auth': {'port': 8000, 'name': 'Authentication Service', 'critical': True},
    'ac': {'port': 8001, 'name': 'Constitutional AI Service', 'critical': True},
    'integrity': {'port': 8002, 'name': 'Integrity Service', 'critical': True},
    'fv': {'port': 8003, 'name': 'Formal Verification Service', 'critical': False},
    'gs': {'port': 8004, 'name': 'Governance Synthesis Service', 'critical': False},
    'pgc': {'port': 8005, 'name': 'Policy Governance Service', 'critical': True},
    'ec': {'port': 8006, 'name': 'Evolutionary Computation Service', 'critical': False}
}

# Performance targets
PERFORMANCE_TARGETS = {
    'response_time_ms': 500,
    'availability_percent': 99.5,
    'quality_score': 0.8,
    'compliance_score': 0.95
}

@st.cache_data(ttl=30)  # Cache for 30 seconds
def generate_sample_metrics():
    """Generate sample metrics for dashboard demonstration."""
    current_time = datetime.now()
    
    # Generate service health data
    service_health = {}
    for service_id, config in ACGS_SERVICES.items():
        base_response_time = np.random.lognormal(5.5, 0.3)  # ~250ms average
        if not config['critical']:
            base_response_time *= 1.2  # Non-critical services slightly slower
        
        service_health[service_id] = {
            'name': config['name'],
            'status': 'healthy' if np.random.random() > 0.05 else 'degraded',
            'response_time_ms': base_response_time,
            'availability_percent': np.random.normal(99.7, 0.5),
            'error_rate_percent': np.random.exponential(0.5),
            'last_updated': current_time.isoformat()
        }
    
    # Generate quality metrics
    quality_metrics = {
        'overall_score': np.random.beta(8, 2),
        'missing_value_rate': np.random.exponential(0.02),
        'outlier_rate': np.random.exponential(0.03),
        'freshness_score': np.random.beta(9, 1),
        'last_assessment': current_time.isoformat()
    }
    
    # Generate compliance metrics
    compliance_metrics = {
        'overall_score': np.random.beta(19, 1),  # High compliance expected
        'transparency_score': np.random.beta(9, 1),
        'accountability_score': np.random.beta(8, 2),
        'fairness_score': np.random.beta(7, 3),
        'privacy_score': np.random.beta(9, 1),
        'safety_score': np.random.beta(10, 1),
        'violations_count': np.random.poisson(0.5),
        'last_check': current_time.isoformat()
    }
    
    # Generate drift metrics
    drift_metrics = {
        'models_monitored': 5,
        'models_with_drift': np.random.poisson(0.3),
        'retraining_required': np.random.poisson(0.1),
        'last_drift_check': current_time.isoformat()
    }
    
    return {
        'service_health': service_health,
        'quality_metrics': quality_metrics,
        'compliance_metrics': compliance_metrics,
        'drift_metrics': drift_metrics,
        'timestamp': current_time.isoformat()
    }

def create_service_health_chart(service_health):
    """Create service health status chart."""
    services = list(service_health.keys())
    response_times = [service_health[s]['response_time_ms'] for s in services]
    statuses = [service_health[s]['status'] for s in services]
    
    colors = ['green' if status == 'healthy' else 'red' for status in statuses]
    
    fig = go.Figure(data=go.Bar(
        x=services,
        y=response_times,
        marker_color=colors,
        text=[f"{rt:.0f}ms" for rt in response_times],
        textposition='auto'
    ))
    
    fig.add_hline(
        y=PERFORMANCE_TARGETS['response_time_ms'],
        line_dash="dash",
        line_color="red",
        annotation_text="Target: 500ms"
    )
    
    fig.update_layout(
        title="Service Response Times",
        xaxis_title="Service",
        yaxis_title="Response Time (ms)",
        height=400
    )
    
    return fig

def create_quality_gauge(quality_score, title="Data Quality Score"):
    """Create quality score gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=quality_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': PERFORMANCE_TARGETS['quality_score']},
        gauge={
            'axis': {'range': [None, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 0.6], 'color': "lightgray"},
                {'range': [0.6, 0.8], 'color': "yellow"},
                {'range': [0.8, 1], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': PERFORMANCE_TARGETS['quality_score']
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_compliance_radar(compliance_metrics):
    """Create constitutional compliance radar chart."""
    principles = ['transparency', 'accountability', 'fairness', 'privacy', 'safety']
    scores = [compliance_metrics[f'{p}_score'] for p in principles]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=principles,
        fill='toself',
        name='Current Compliance'
    ))
    
    # Add target line
    target_scores = [PERFORMANCE_TARGETS['compliance_score']] * len(principles)
    fig.add_trace(go.Scatterpolar(
        r=target_scores,
        theta=principles,
        fill='toself',
        name='Target Compliance',
        line_color='red',
        fillcolor='rgba(255,0,0,0.1)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Constitutional Compliance",
        height=400
    )
    
    return fig

def create_system_overview_metrics(metrics):
    """Create system overview metrics."""
    service_health = metrics['service_health']
    quality_metrics = metrics['quality_metrics']
    compliance_metrics = metrics['compliance_metrics']
    drift_metrics = metrics['drift_metrics']
    
    # Calculate system-wide metrics
    healthy_services = sum(1 for s in service_health.values() if s['status'] == 'healthy')
    total_services = len(service_health)
    avg_response_time = np.mean([s['response_time_ms'] for s in service_health.values()])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="System Availability",
            value=f"{(healthy_services/total_services)*100:.1f}%",
            delta=f"{healthy_services}/{total_services} services healthy"
        )
    
    with col2:
        st.metric(
            label="Avg Response Time",
            value=f"{avg_response_time:.0f}ms",
            delta=f"Target: {PERFORMANCE_TARGETS['response_time_ms']}ms",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Data Quality Score",
            value=f"{quality_metrics['overall_score']:.3f}",
            delta=f"Target: {PERFORMANCE_TARGETS['quality_score']:.1f}",
            delta_color="normal" if quality_metrics['overall_score'] >= PERFORMANCE_TARGETS['quality_score'] else "inverse"
        )
    
    with col4:
        st.metric(
            label="Compliance Score",
            value=f"{compliance_metrics['overall_score']:.3f}",
            delta=f"Target: {PERFORMANCE_TARGETS['compliance_score']:.2f}",
            delta_color="normal" if compliance_metrics['overall_score'] >= PERFORMANCE_TARGETS['compliance_score'] else "inverse"
        )

def main():
    """Main dashboard function."""
    
    # Dashboard header
    st.title("🤖 ACGS Real-Time Analytics Dashboard")
    st.markdown(f"**Constitutional Hash**: `{CONSTITUTIONAL_HASH}`")
    
    # Sidebar configuration
    st.sidebar.title("Dashboard Configuration")
    
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)
    
    # Service filter
    selected_services = st.sidebar.multiselect(
        "Select Services to Monitor",
        options=list(ACGS_SERVICES.keys()),
        default=list(ACGS_SERVICES.keys()),
        format_func=lambda x: ACGS_SERVICES[x]['name']
    )
    
    # Alert thresholds
    st.sidebar.subheader("Alert Thresholds")
    response_time_threshold = st.sidebar.slider("Response Time (ms)", 100, 1000, 500)
    quality_threshold = st.sidebar.slider("Quality Score", 0.5, 1.0, 0.8)
    compliance_threshold = st.sidebar.slider("Compliance Score", 0.8, 1.0, 0.95)
    
    # Auto-refresh logic
    if auto_refresh:
        placeholder = st.empty()
        
        while True:
            with placeholder.container():
                # Generate current metrics
                metrics = generate_sample_metrics()
                
                # System overview
                st.subheader("📊 System Overview")
                create_system_overview_metrics(metrics)
                
                # Service health section
                st.subheader("🏥 Service Health Status")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Filter services based on selection
                    filtered_health = {k: v for k, v in metrics['service_health'].items() 
                                     if k in selected_services}
                    
                    if filtered_health:
                        service_chart = create_service_health_chart(filtered_health)
                        st.plotly_chart(service_chart, use_container_width=True)
                    else:
                        st.warning("No services selected for monitoring")
                
                with col2:
                    st.subheader("Service Status")
                    for service_id in selected_services:
                        if service_id in metrics['service_health']:
                            service = metrics['service_health'][service_id]
                            status_icon = "✅" if service['status'] == 'healthy' else "❌"
                            st.write(f"{status_icon} **{service['name']}**")
                            st.write(f"   Response: {service['response_time_ms']:.0f}ms")
                            st.write(f"   Availability: {service['availability_percent']:.1f}%")
                
                # Quality and compliance section
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Data Quality Monitoring")
                    quality_gauge = create_quality_gauge(
                        metrics['quality_metrics']['overall_score'],
                        "Data Quality Score"
                    )
                    st.plotly_chart(quality_gauge, use_container_width=True)
                    
                    # Quality details
                    st.write("**Quality Metrics:**")
                    st.write(f"- Missing Values: {metrics['quality_metrics']['missing_value_rate']:.1%}")
                    st.write(f"- Outlier Rate: {metrics['quality_metrics']['outlier_rate']:.1%}")
                    st.write(f"- Freshness Score: {metrics['quality_metrics']['freshness_score']:.3f}")
                
                with col2:
                    st.subheader("⚖️ Constitutional Compliance")
                    compliance_radar = create_compliance_radar(metrics['compliance_metrics'])
                    st.plotly_chart(compliance_radar, use_container_width=True)
                    
                    # Compliance details
                    st.write("**Compliance Status:**")
                    if metrics['compliance_metrics']['violations_count'] > 0:
                        st.error(f"🚨 {metrics['compliance_metrics']['violations_count']} violations detected")
                    else:
                        st.success("✅ No compliance violations")
                
                # Model drift section
                st.subheader("🔄 Model Drift Monitoring")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Models Monitored",
                        metrics['drift_metrics']['models_monitored']
                    )
                
                with col2:
                    drift_count = metrics['drift_metrics']['models_with_drift']
                    st.metric(
                        "Models with Drift",
                        drift_count,
                        delta_color="inverse" if drift_count > 0 else "normal"
                    )
                
                with col3:
                    retraining_count = metrics['drift_metrics']['retraining_required']
                    st.metric(
                        "Retraining Required",
                        retraining_count,
                        delta_color="inverse" if retraining_count > 0 else "normal"
                    )
                
                # Alerts section
                st.subheader("🚨 Active Alerts")
                
                alerts = []
                
                # Check for service alerts
                for service_id, service in metrics['service_health'].items():
                    if service['response_time_ms'] > response_time_threshold:
                        alerts.append(f"⚠️ High response time: {service['name']} ({service['response_time_ms']:.0f}ms)")
                    if service['status'] != 'healthy':
                        alerts.append(f"❌ Service unhealthy: {service['name']}")
                
                # Check for quality alerts
                if metrics['quality_metrics']['overall_score'] < quality_threshold:
                    alerts.append(f"📉 Low data quality: {metrics['quality_metrics']['overall_score']:.3f}")
                
                # Check for compliance alerts
                if metrics['compliance_metrics']['overall_score'] < compliance_threshold:
                    alerts.append(f"⚖️ Compliance issue: {metrics['compliance_metrics']['overall_score']:.3f}")
                
                if metrics['compliance_metrics']['violations_count'] > 0:
                    alerts.append(f"🚨 Constitutional violations: {metrics['compliance_metrics']['violations_count']}")
                
                # Check for drift alerts
                if metrics['drift_metrics']['retraining_required'] > 0:
                    alerts.append(f"🔄 Model retraining required: {metrics['drift_metrics']['retraining_required']} models")
                
                if alerts:
                    for alert in alerts:
                        st.error(alert)
                else:
                    st.success("✅ No active alerts")
                
                # Footer
                st.markdown("---")
                st.markdown(f"**Last Updated**: {metrics['timestamp']}")
                st.markdown(f"**Dashboard Version**: ACGS-PGP v8")
                st.markdown(f"**Constitutional Hash**: `{CONSTITUTIONAL_HASH}`")
            
            # Wait before next refresh
            time.sleep(refresh_interval)
    
    else:
        # Static mode - single load
        metrics = generate_sample_metrics()
        create_system_overview_metrics(metrics)
        
        # Add manual refresh button
        if st.button("🔄 Refresh Data"):
            st.experimental_rerun()

if __name__ == "__main__":
    main()
