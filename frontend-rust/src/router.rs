/*!
 * ACGS-2 Router Configuration with Lazy Loading
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Optimized for bundle size reduction through code splitting
 */

use yew::prelude::*;
use yew_router::prelude::*;

#[derive(Clone, Routable, PartialEq)]
pub enum Route {
    #[at("/")]
    Home,
    #[at("/dashboard")]
    Dashboard,
    #[at("/dashboard/:tab")]
    DashboardTab { tab: String },
    #[at("/constitutional")]
    Constitutional,
    #[at("/constitutional/:section")]
    ConstitutionalSection { section: String },
    #[at("/services")]
    Services,
    #[at("/services/:service")]
    ServiceDetail { service: String },
    #[at("/governance")]
    Governance,
    #[at("/governance/:policy")]
    GovernancePolicy { policy: String },
    #[at("/audit")]
    Audit,
    #[at("/audit/:log_id")]
    AuditDetail { log_id: String },
    #[at("/settings")]
    Settings,
    #[at("/settings/:category")]
    SettingsCategory { category: String },
    #[not_found]
    #[at("/404")]
    NotFound,
}

/// Simplified component rendering without complex lazy loading
fn render_route_component(route: &Route) -> Html {
    match route {
        Route::Dashboard => html! { <crate::components::Dashboard /> },
        Route::DashboardTab { tab } => html! { <crate::components::Dashboard active_tab={tab.clone()} /> },
        Route::Constitutional => html! { <crate::components::ConstitutionalIndicator /> },
        Route::ConstitutionalSection { section: _ } => html! { <crate::components::ConstitutionalIndicator /> },
        _ => html! {
            <div class="component-placeholder" data-constitutional-hash={crate::CONSTITUTIONAL_HASH}>
                {"Component loading..."}
            </div>
        },
    }
}

pub fn switch(routes: Route) -> Html {
    match routes {
        Route::Home => {
            // Redirect to dashboard
            html! {
                <div class="redirect-home" data-constitutional-hash={crate::CONSTITUTIONAL_HASH}>
                    {"Redirecting to Dashboard..."}
                </div>
            }
        }
        Route::Dashboard | Route::DashboardTab { .. } | Route::Constitutional | Route::ConstitutionalSection { .. } => {
            render_route_component(&routes)
        }
        Route::Services => html! { <ServicesOverview /> },
        Route::ServiceDetail { service } => html! {
            <ServiceDetailView service_name={service} />
        },
        Route::Governance => html! { <GovernanceOverview /> },
        Route::GovernancePolicy { policy } => html! {
            <PolicyDetailView policy_id={policy} />
        },
        Route::Audit => html! { <AuditOverview /> },
        Route::AuditDetail { log_id } => html! {
            <AuditDetailView log_id={log_id} />
        },
        Route::Settings => html! { <SettingsOverview /> },
        Route::SettingsCategory { category } => html! {
            <SettingsCategory category={category} />
        },
        Route::NotFound => html! { <NotFoundPage /> },
    }
}

// Services overview page
#[function_component(ServicesOverview)]
pub fn services_overview() -> Html {
    html! {
        <div class="services-overview">
            <h1>{"ACGS-2 Services"}</h1>
            <div class="services-grid">
                <ServiceCard 
                    name="Constitutional AI"
                    port="8001"
                    description="Constitutional compliance validation and monitoring"
                    status="healthy"
                />
                <ServiceCard 
                    name="Integrity Service"
                    port="8002"
                    description="Data integrity and validation"
                    status="healthy"
                />
                <ServiceCard 
                    name="Formal Verification"
                    port="8003"
                    description="Formal verification of policies and rules"
                    status="healthy"
                />
                <ServiceCard 
                    name="Governance Synthesis"
                    port="8004"
                    description="AI-powered governance policy synthesis"
                    status="healthy"
                />
                <ServiceCard 
                    name="Policy Governance"
                    port="8005"
                    description="Policy evaluation and compliance"
                    status="healthy"
                />
                <ServiceCard 
                    name="Evolutionary Computation"
                    port="8006"
                    description="Evolutionary optimization algorithms"
                    status="healthy"
                />
                <ServiceCard 
                    name="Auth Service"
                    port="8016"
                    description="Authentication and authorization"
                    status="healthy"
                />
            </div>
        </div>
    }
}

#[derive(Properties, PartialEq)]
pub struct ServiceCardProps {
    pub name: AttrValue,
    pub port: AttrValue,
    pub description: AttrValue,
    pub status: AttrValue,
}

#[function_component(ServiceCard)]
pub fn service_card(props: &ServiceCardProps) -> Html {
    let service_name = props.name.to_string().to_lowercase().replace(" ", "_");

    let onclick = {
        let service_name = service_name.clone();
        Callback::from(move |_| {
            log::info!("Navigating to service: {}", service_name);
        })
    };

    let status_class = match props.status.as_str() {
        "healthy" => "status-healthy",
        "warning" => "status-warning",
        "error" => "status-error",
        _ => "status-unknown",
    };

    html! {
        <div class="service-card" onclick={onclick}>
            <div class="service-header">
                <h3 class="service-name">{&props.name}</h3>
                <span class={classes!("service-status", status_class)}>
                    {&props.status}
                </span>
            </div>
            <p class="service-description">{&props.description}</p>
            <div class="service-footer">
                <span class="service-port">{"Port: "}{&props.port}</span>
            </div>
        </div>
    }
}

// Service detail view
#[derive(Properties, PartialEq)]
pub struct ServiceDetailViewProps {
    pub service_name: AttrValue,
}

#[function_component(ServiceDetailView)]
pub fn service_detail_view(props: &ServiceDetailViewProps) -> Html {
    html! {
        <div class="service-detail">
            <h1>{format!("{} Service", props.service_name)}</h1>
            <div class="service-metrics">
                <div class="metric-card">
                    <h3>{"Health Status"}</h3>
                    <div class="metric-value status-healthy">{"Healthy"}</div>
                </div>
                <div class="metric-card">
                    <h3>{"Response Time"}</h3>
                    <div class="metric-value">{"2.3ms"}</div>
                </div>
                <div class="metric-card">
                    <h3>{"Requests/sec"}</h3>
                    <div class="metric-value">{"156"}</div>
                </div>
                <div class="metric-card">
                    <h3>{"Constitutional Compliance"}</h3>
                    <div class="metric-value status-healthy">{"100%"}</div>
                </div>
            </div>
        </div>
    }
}

// Governance overview
#[function_component(GovernanceOverview)]
pub fn governance_overview() -> Html {
    html! {
        <div class="governance-overview">
            <h1>{"Governance Dashboard"}</h1>
            <p>{"Policy management and governance workflows"}</p>
        </div>
    }
}

// Policy detail view
#[derive(Properties, PartialEq)]
pub struct PolicyDetailViewProps {
    pub policy_id: AttrValue,
}

#[function_component(PolicyDetailView)]
pub fn policy_detail_view(props: &PolicyDetailViewProps) -> Html {
    html! {
        <div class="policy-detail">
            <h1>{format!("Policy: {}", props.policy_id)}</h1>
            <p>{"Policy details and compliance information"}</p>
        </div>
    }
}

// Audit overview
#[function_component(AuditOverview)]
pub fn audit_overview() -> Html {
    html! {
        <div class="audit-overview">
            <h1>{"Audit Dashboard"}</h1>
            <p>{"Constitutional compliance audit logs and reports"}</p>
        </div>
    }
}

// Audit detail view
#[derive(Properties, PartialEq)]
pub struct AuditDetailViewProps {
    pub log_id: AttrValue,
}

#[function_component(AuditDetailView)]
pub fn audit_detail_view(props: &AuditDetailViewProps) -> Html {
    html! {
        <div class="audit-detail">
            <h1>{format!("Audit Log: {}", props.log_id)}</h1>
            <p>{"Detailed audit log information"}</p>
        </div>
    }
}

// Settings overview
#[function_component(SettingsOverview)]
pub fn settings_overview() -> Html {
    html! {
        <div class="settings-overview">
            <h1>{"Settings"}</h1>
            <p>{"Application configuration and preferences"}</p>
        </div>
    }
}

// Settings category
#[derive(Properties, PartialEq)]
pub struct SettingsCategoryProps {
    pub category: AttrValue,
}

#[function_component(SettingsCategory)]
pub fn settings_category(props: &SettingsCategoryProps) -> Html {
    html! {
        <div class="settings-category">
            <h1>{format!("Settings: {}", props.category)}</h1>
            <p>{"Category-specific settings"}</p>
        </div>
    }
}

// 404 page
#[function_component(NotFoundPage)]
pub fn not_found_page() -> Html {
    let go_home = {
        Callback::from(move |_| {
            log::info!("Navigating to dashboard from 404 page");
        })
    };

    html! {
        <div class="not-found-page">
            <h1>{"404 - Page Not Found"}</h1>
            <p>{"The requested page could not be found."}</p>
            <button onclick={go_home} class="btn btn-primary">
                {"Go to Dashboard"}
            </button>
        </div>
    }
}
