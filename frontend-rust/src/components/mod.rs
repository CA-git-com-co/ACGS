/*!
 * ACGS-2 UI Components
 * Constitutional Hash: cdd01ef066bc6cf2
 */

pub mod layout;
pub mod constitutional;
pub mod dashboard;
pub mod ui;
pub mod error_boundary;
pub mod navigation;
pub mod preferences;
pub mod advanced_navigation;

#[cfg(test)]
mod tests;

// Re-exports for convenience
pub use layout::Layout;
pub use constitutional::ConstitutionalIndicator;
pub use dashboard::Dashboard;
pub use ui::*;
pub use error_boundary::ErrorBoundary;
pub use navigation::Navigation;
pub use preferences::{UserPreferencesPanel, UserPreferences};
pub use advanced_navigation::AdvancedNavigation;

// Common component traits and utilities
use yew::prelude::*;
// Removed unused imports: Deserialize, Serialize

// Constitutional compliance trait for components
pub trait ConstitutionalComponent {
    fn constitutional_hash(&self) -> &'static str {
        crate::CONSTITUTIONAL_HASH
    }
    
    fn validate_constitutional_compliance(&self) -> bool {
        true // Default implementation - override for specific validation
    }
}

// Performance monitoring trait for components
pub trait PerformanceMonitored {
    fn component_name(&self) -> &'static str;
    
    fn track_render_time(&self, duration_ms: f64) {
        if duration_ms > crate::PERFORMANCE_TARGETS.p99_latency_ms as f64 {
            log::warn!("Component {} render time exceeded target: {}ms", 
                      self.component_name(), duration_ms);
        }
    }
}

// Common component properties
#[derive(Properties, PartialEq, Clone)]
pub struct CommonProps {
    #[prop_or_default]
    pub class: Classes,
    #[prop_or_default]
    pub id: Option<AttrValue>,
    #[prop_or_default]
    pub data_testid: Option<AttrValue>,
}

// Loading state component
#[derive(Properties, PartialEq)]
pub struct LoadingProps {
    #[prop_or_default]
    pub message: Option<AttrValue>,
    #[prop_or_default]
    pub size: LoadingSize,
}

#[derive(Debug, Clone, PartialEq)]
pub enum LoadingSize {
    Small,
    Medium,
    Large,
}

impl Default for LoadingSize {
    fn default() -> Self {
        Self::Medium
    }
}

#[function_component(Loading)]
pub fn loading(props: &LoadingProps) -> Html {
    let size_class = match props.size {
        LoadingSize::Small => "loading-small",
        LoadingSize::Medium => "loading-medium",
        LoadingSize::Large => "loading-large",
    };

    html! {
        <div class={classes!("loading-spinner", size_class)}>
            <div class="spinner"></div>
            { if let Some(ref message) = props.message {
                html! { <span class="loading-message">{message}</span> }
            } else {
                html! {}
            }}
        </div>
    }
}

// Error display component
#[derive(Properties, PartialEq)]
pub struct ErrorDisplayProps {
    pub error: AttrValue,
    #[prop_or_default]
    pub retry_callback: Option<Callback<()>>,
    #[prop_or_default]
    pub show_details: bool,
}

#[function_component(ErrorDisplay)]
pub fn error_display(props: &ErrorDisplayProps) -> Html {
    html! {
        <div class="error-display">
            <div class="error-icon">{"⚠️"}</div>
            <div class="error-content">
                <h3 class="error-title">{"Something went wrong"}</h3>
                <p class="error-message">{&props.error}</p>
                { if props.show_details {
                    html! {
                        <details class="error-details">
                            <summary>{"Technical Details"}</summary>
                            <pre class="error-stack">{&props.error}</pre>
                        </details>
                    }
                } else {
                    html! {}
                }}
                { if let Some(ref retry) = props.retry_callback {
                    let retry = retry.clone();
                    html! {
                        <button 
                            class="error-retry-button"
                            onclick={move |_| retry.emit(())}
                        >
                            {"Retry"}
                        </button>
                    }
                } else {
                    html! {}
                }}
            </div>
        </div>
    }
}

// Toast notification component
#[derive(Properties, PartialEq, Clone)]
pub struct ToastProps {
    pub message: AttrValue,
    pub toast_type: ToastType,
    #[prop_or_default]
    pub duration_ms: Option<u32>,
    #[prop_or_default]
    pub on_close: Option<Callback<()>>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ToastType {
    Info,
    Success,
    Warning,
    Error,
    Constitutional,
}

#[function_component(Toast)]
pub fn toast(props: &ToastProps) -> Html {
    let visible = use_state(|| true);
    
    // Auto-hide after duration (simplified - no timer)
    // In a real implementation, you'd use web_sys::window().set_timeout_with_callback_and_timeout_and_arguments_0

    // Handle close
    let on_close = {
        let visible = visible.clone();
        let callback = props.on_close.clone();
        Callback::from(move |_| {
            visible.set(false);
            if let Some(ref cb) = callback {
                cb.emit(());
            }
        })
    };

    let type_class = match props.toast_type {
        ToastType::Info => "toast-info",
        ToastType::Success => "toast-success",
        ToastType::Warning => "toast-warning",
        ToastType::Error => "toast-error",
        ToastType::Constitutional => "toast-constitutional",
    };

    let icon = match props.toast_type {
        ToastType::Info => "ℹ️",
        ToastType::Success => "✅",
        ToastType::Warning => "⚠️",
        ToastType::Error => "❌",
        ToastType::Constitutional => "🏛️",
    };

    if *visible {
        html! {
            <div class={classes!("toast", type_class)}>
                <div class="toast-icon">{icon}</div>
                <div class="toast-message">{&props.message}</div>
                <button class="toast-close" onclick={on_close}>{"×"}</button>
            </div>
        }
    } else {
        html! {}
    }
}

// Button component with constitutional compliance
#[derive(Properties, PartialEq)]
pub struct ButtonProps {
    #[prop_or_default]
    pub children: Children,
    #[prop_or_default]
    pub onclick: Option<Callback<MouseEvent>>,
    #[prop_or_default]
    pub button_type: ButtonType,
    #[prop_or_default]
    pub size: ButtonSize,
    #[prop_or_default]
    pub disabled: bool,
    #[prop_or_default]
    pub loading: bool,
    #[prop_or_default]
    pub constitutional: bool,
    #[prop_or_default]
    pub class: Classes,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ButtonType {
    Primary,
    Secondary,
    Outline,
    Ghost,
    Constitutional,
    Danger,
}

impl Default for ButtonType {
    fn default() -> Self {
        Self::Primary
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum ButtonSize {
    Small,
    Medium,
    Large,
}

impl Default for ButtonSize {
    fn default() -> Self {
        Self::Medium
    }
}

#[function_component(Button)]
pub fn button(props: &ButtonProps) -> Html {
    let button_type = if props.constitutional {
        ButtonType::Constitutional
    } else {
        props.button_type.clone()
    };

    let type_class = match button_type {
        ButtonType::Primary => "btn-primary",
        ButtonType::Secondary => "btn-secondary",
        ButtonType::Outline => "btn-outline",
        ButtonType::Ghost => "btn-ghost",
        ButtonType::Constitutional => "btn-constitutional",
        ButtonType::Danger => "btn-danger",
    };

    let size_class = match props.size {
        ButtonSize::Small => "btn-small",
        ButtonSize::Medium => "btn-medium",
        ButtonSize::Large => "btn-large",
    };

    let classes = classes!(
        "btn",
        type_class,
        size_class,
        props.class.clone(),
        props.disabled.then_some("btn-disabled"),
        props.loading.then_some("btn-loading")
    );

    html! {
        <button
            class={classes}
            onclick={props.onclick.clone()}
            disabled={props.disabled || props.loading}
            data-constitutional-hash={crate::CONSTITUTIONAL_HASH}
        >
            { if props.loading {
                html! { <span class="btn-spinner"></span> }
            } else {
                html! {}
            }}
            { for props.children.iter() }
        </button>
    }
}
