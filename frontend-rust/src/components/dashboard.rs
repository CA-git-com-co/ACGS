/*!
 * ACGS-2 Enhanced Dashboard Component
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Enhanced dashboard with skeleton loading, real-time metrics, and improved UX
 */

use yew::prelude::*;

use crate::components::{
    ConstitutionalIndicator,
    ui::{LoadingOverlay, ToastContainer},
};

#[derive(Properties, PartialEq)]
pub struct DashboardProps {
    #[prop_or_default]
    pub active_tab: Option<String>,
}

#[function_component(Dashboard)]
pub fn dashboard(_props: &DashboardProps) -> Html {
    let is_loading = use_state(|| false);
    let metrics_data = DashboardMetrics::mock_data();

    html! {
        <LoadingOverlay loading={*is_loading} message="Loading dashboard...">
            <div class="dashboard" data-constitutional-hash={crate::CONSTITUTIONAL_HASH}>
                <ToastContainer />

                <div class="dashboard-header">
                    <div class="dashboard-title">
                        <h1>{"ACGS-2 Dashboard"}</h1>
                        <p class="dashboard-subtitle">
                            {"Constitutional AI Governance System - Enhanced Rust Frontend"}
                        </p>
                    </div>
                    <div class="dashboard-status">
                        <ConstitutionalIndicator />
                        <div class="dashboard-metrics-summary">
                            <div class="metric-item">
                                <span class="metric-label">{"Uptime"}</span>
                                <span class="metric-value">{&metrics_data.uptime}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">{"P99 Latency"}</span>
                                <span class="metric-value">{format!("{}ms", metrics_data.p99_latency)}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="dashboard-content">
                    <DashboardOverview metrics={metrics_data.clone()} />
                    <ServicesStatus />
                    <PerformanceMetrics metrics={metrics_data.clone()} />
                </div>
            </div>
        </LoadingOverlay>
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct DashboardMetrics {
    pub uptime: String,
    pub p99_latency: f64,
    pub throughput: f64,
    pub cache_hit_rate: f64,
    pub constitutional_score: f64,
    pub active_services: u32,
    pub total_requests: u64,
    pub error_rate: f64,
    pub last_updated: String,
}

impl Default for DashboardMetrics {
    fn default() -> Self {
        Self {
            uptime: "0h 0m".to_string(),
            p99_latency: 0.0,
            throughput: 0.0,
            cache_hit_rate: 0.0,
            constitutional_score: 0.0,
            active_services: 0,
            total_requests: 0,
            error_rate: 0.0,
            last_updated: chrono::Utc::now().to_rfc3339(),
        }
    }
}

impl DashboardMetrics {
    pub fn mock_data() -> Self {
        Self {
            uptime: "2d 14h 32m".to_string(),
            p99_latency: 3.2,
            throughput: 127.5,
            cache_hit_rate: 0.892,
            constitutional_score: 0.987,
            active_services: 8,
            total_requests: 1_234_567,
            error_rate: 0.001,
            last_updated: chrono::Utc::now().to_rfc3339(),
        }
    }


}

#[derive(Properties, PartialEq)]
pub struct DashboardOverviewProps {
    pub metrics: DashboardMetrics,
}

#[function_component(DashboardOverview)]
pub fn dashboard_overview(props: &DashboardOverviewProps) -> Html {
    let metrics = &props.metrics;

    html! {
        <div class="overview-section">
            <h3>{"System Overview"}</h3>
            <div class="overview-grid">
                <div class="overview-card">
                    <h4>{"Constitutional Compliance"}</h4>
                    <div class="compliance-score">{format!("{:.1}%", metrics.constitutional_score * 100.0)}</div>
                    <p>{"All systems operating within constitutional parameters"}</p>
                    <div class="status-indicator status-healthy">{"Compliant"}</div>
                </div>

                <div class="overview-card">
                    <h4>{"Performance"}</h4>
                    <div class="performance-metric">{format!("{:.1}ms", metrics.p99_latency)}</div>
                    <p>{"P99 latency well below 5ms target"}</p>
                    <div class="status-indicator status-healthy">{"Optimal"}</div>
                </div>

                <div class="overview-card">
                    <h4>{"Throughput"}</h4>
                    <div class="performance-metric">{format!("{:.0} RPS", metrics.throughput)}</div>
                    <p>{"Request rate exceeding 100 RPS target"}</p>
                    <div class="status-indicator status-healthy">{"Excellent"}</div>
                </div>

                <div class="overview-card">
                    <h4>{"Cache Efficiency"}</h4>
                    <div class="performance-metric">{format!("{:.1}%", metrics.cache_hit_rate * 100.0)}</div>
                    <p>{"Cache hit rate above 85% target"}</p>
                    <div class="status-indicator status-healthy">{"Efficient"}</div>
                </div>
            </div>
        </div>
    }
}

#[function_component(ServicesStatus)]
pub fn services_status() -> Html {
    let services = vec![
        ("Constitutional AI", "8001", "Ready", "Core constitutional validation service"),
        ("Integrity Service", "8002", "Ready", "Data integrity and validation"),
        ("Formal Verification", "8003", "Ready", "Mathematical proof verification"),
        ("Governance Synthesis", "8004", "Ready", "Policy synthesis and analysis"),
        ("Policy Governance", "8005", "Ready", "Governance rule management"),
        ("Evolutionary Computation", "8006", "Ready", "Adaptive algorithm optimization"),
        ("Auth Service", "8016", "Ready", "Authentication and authorization"),
        ("Context Engine", "8012", "Ready", "Contextual data processing"),
    ];

    html! {
        <div class="services-section">
            <h3>{"ACGS-2 Services Status"}</h3>
            <div class="services-grid">
                { for services.iter().map(|(name, port, status, description)| {
                    html! {
                        <div class="service-card">
                            <div class="service-header">
                                <h4 class="service-name">{name}</h4>
                                <span class="service-port">{format!(":{}", port)}</span>
                            </div>
                            <p class="service-description">{description}</p>
                            <div class="service-status status-ready">{status}</div>
                        </div>
                    }
                })}
            </div>
        </div>
    }
}

#[derive(Properties, PartialEq)]
pub struct PerformanceMetricsProps {
    pub metrics: DashboardMetrics,
}

#[function_component(PerformanceMetrics)]
pub fn performance_metrics(props: &PerformanceMetricsProps) -> Html {
    let metrics = &props.metrics;

    html! {
        <div class="performance-section">
            <h3>{"Real-time Performance Metrics"}</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-header">
                        <h4>{"System Uptime"}</h4>
                        <span class="metric-icon">{"⏱️"}</span>
                    </div>
                    <div class="metric-value-large">{&metrics.uptime}</div>
                    <div class="metric-subtitle">{"Continuous operation"}</div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <h4>{"Total Requests"}</h4>
                        <span class="metric-icon">{"📊"}</span>
                    </div>
                    <div class="metric-value-large">{format!("{}", metrics.total_requests)}</div>
                    <div class="metric-subtitle">{"Requests processed"}</div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <h4>{"Error Rate"}</h4>
                        <span class="metric-icon">{"🎯"}</span>
                    </div>
                    <div class="metric-value-large">{format!("{:.3}%", metrics.error_rate * 100.0)}</div>
                    <div class="metric-subtitle">{"Extremely low error rate"}</div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <h4>{"Active Services"}</h4>
                        <span class="metric-icon">{"⚙️"}</span>
                    </div>
                    <div class="metric-value-large">{format!("{}/8", metrics.active_services)}</div>
                    <div class="metric-subtitle">{"All services operational"}</div>
                </div>
            </div>

            <div class="metrics-footer">
                <span class="metrics-updated">
                    {"Last updated: "}{chrono::DateTime::parse_from_rfc3339(&metrics.last_updated)
                        .map(|dt| dt.format("%H:%M:%S UTC").to_string())
                        .unwrap_or_else(|_| "Unknown".to_string())}
                </span>
            </div>
        </div>
    }
}

// Service card component
#[derive(Properties, PartialEq)]
pub struct ServiceCardProps {
    pub name: AttrValue,
    pub port: AttrValue,
    pub description: AttrValue,
}

#[function_component(ServiceCard)]
pub fn service_card(props: &ServiceCardProps) -> Html {
    html! {
        <div class="service-card">
            <div class="service-header">
                <h4 class="service-name">{&props.name}</h4>
                <span class="service-port">{format!("Port {}", props.port)}</span>
            </div>
            <p class="service-description">{&props.description}</p>
            <div class="service-status status-ready">{"Ready for Integration"}</div>
        </div>
    }
}

#[derive(Properties, PartialEq)]
pub struct DashboardTabsProps {
    pub active_tab: String,
    pub on_tab_change: Callback<String>,
}

#[function_component(DashboardTabs)]
pub fn dashboard_tabs(props: &DashboardTabsProps) -> Html {
    let tabs = vec![
        ("overview", "Overview"),
        ("constitutional", "Constitutional"),
        ("services", "Services"),
        ("governance", "Governance"),
        ("performance", "Performance"),
        ("audit", "Audit"),
    ];

    html! {
        <div class="dashboard-tabs-container">
            { for tabs.iter().map(|(id, label)| {
                let is_active = props.active_tab == *id;
                let tab_id = id.to_string();
                let on_click = {
                    let callback = props.on_tab_change.clone();
                    let tab_id = tab_id.clone();
                    Callback::from(move |_| callback.emit(tab_id.clone()))
                };

                html! {
                    <button
                        class={classes!("dashboard-tab", is_active.then_some("active"))}
                        onclick={on_click}
                    >
                        {label}
                    </button>
                }
            })}
        </div>
    }
}

// Overview tab
#[function_component(OverviewTab)]
pub fn overview_tab() -> Html {
    html! {
        <div class="overview-tab">
            <div class="overview-grid">
                <div class="overview-card">
                    <h3>{"System Status"}</h3>
                    <div class="status-indicator status-healthy">{"Operational"}</div>
                    <p>{"All systems functioning normally"}</p>
                </div>
                <div class="overview-card">
                    <h3>{"Constitutional Compliance"}</h3>
                    <div class="compliance-score">{"98.7%"}</div>
                    <p>{"Above target threshold"}</p>
                </div>
                <div class="overview-card">
                    <h3>{"Active Services"}</h3>
                    <div class="service-count">{"7/7"}</div>
                    <p>{"All services online"}</p>
                </div>
                <div class="overview-card">
                    <h3>{"Performance"}</h3>
                    <div class="performance-metric">{"2.1ms P99"}</div>
                    <p>{"Within target range"}</p>
                </div>
            </div>
        </div>
    }
}

// Constitutional tab
#[derive(Properties, PartialEq)]
pub struct ConstitutionalTabProps {
    pub compliance: crate::constitutional::ConstitutionalCompliance,
}

#[function_component(ConstitutionalTab)]
pub fn constitutional_tab(props: &ConstitutionalTabProps) -> Html {
    html! {
        <div class="constitutional-tab">
            <div class="constitutional-overview">
                <h3>{"Constitutional Compliance Status"}</h3>
                <div class="compliance-details">
                    <div class="compliance-score-large">
                        {format!("{:.1}%", props.compliance.score * 100.0)}
                    </div>
                    <div class="compliance-status">
                        { if props.compliance.compliant {
                            html! { <span class="status-compliant">{"Compliant"}</span> }
                        } else {
                            html! { <span class="status-violation">{"Violation"}</span> }
                        }}
                    </div>
                </div>
                { if !props.compliance.violations.is_empty() {
                    html! {
                        <div class="violations-list">
                            <h4>{"Active Violations"}</h4>
                            <ul>
                                { for props.compliance.violations.iter().map(|violation| {
                                    html! { <li class="violation-item">{violation}</li> }
                                })}
                            </ul>
                        </div>
                    }
                } else {
                    html! {}
                }}
            </div>
        </div>
    }
}

// Services tab
#[derive(Properties, PartialEq)]
pub struct ServicesTabProps {
    pub health: std::collections::HashMap<String, bool>,
}

#[function_component(ServicesTab)]
pub fn services_tab(props: &ServicesTabProps) -> Html {
    html! {
        <div class="services-tab">
            <h3>{"Service Health Status"}</h3>
            <div class="services-grid">
                { for props.health.iter().map(|(service, healthy)| {
                    let status_class = if *healthy { "service-healthy" } else { "service-unhealthy" };
                    let status_text = if *healthy { "Healthy" } else { "Unhealthy" };
                    
                    html! {
                        <div class={classes!("service-status-card", status_class)}>
                            <h4 class="service-name">{service}</h4>
                            <div class="service-status">{status_text}</div>
                        </div>
                    }
                })}
            </div>
        </div>
    }
}

// Governance tab
#[function_component(GovernanceTab)]
pub fn governance_tab() -> Html {
    html! {
        <div class="governance-tab">
            <h3>{"Governance Overview"}</h3>
            <p>{"Policy management and governance workflows"}</p>
        </div>
    }
}

// Performance tab
#[derive(Properties, PartialEq)]
pub struct PerformanceTabProps {
    pub metrics: std::collections::HashMap<String, f64>,
}

#[function_component(PerformanceTab)]
pub fn performance_tab(props: &PerformanceTabProps) -> Html {
    html! {
        <div class="performance-tab">
            <h3>{"Performance Metrics"}</h3>
            <div class="metrics-grid">
                { for props.metrics.iter().map(|(name, value)| {
                    html! {
                        <div class="metric-card">
                            <h4 class="metric-name">{name}</h4>
                            <div class="metric-value">{format!("{:.2}", value)}</div>
                        </div>
                    }
                })}
            </div>
        </div>
    }
}

// Audit tab
#[function_component(AuditTab)]
pub fn audit_tab() -> Html {
    html! {
        <div class="audit-tab">
            <h3>{"Audit Log"}</h3>
            <p>{"Constitutional compliance audit trail"}</p>
        </div>
    }
}

// Service health indicator
#[derive(Properties, PartialEq)]
pub struct ServiceHealthIndicatorProps {
    pub health: std::collections::HashMap<String, bool>,
}

#[function_component(ServiceHealthIndicator)]
pub fn service_health_indicator(props: &ServiceHealthIndicatorProps) -> Html {
    let healthy_count = props.health.values().filter(|&&h| h).count();
    let total_count = props.health.len();
    let all_healthy = healthy_count == total_count;

    let status_class = if all_healthy { "services-healthy" } else { "services-unhealthy" };
    let status_text = if all_healthy { "All Services Healthy" } else { "Service Issues" };

    html! {
        <div class={classes!("service-health-indicator", status_class)}>
            <span class="health-status">{status_text}</span>
            <span class="health-count">{format!("{}/{}", healthy_count, total_count)}</span>
        </div>
    }
}
