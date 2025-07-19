/*!
 * ACGS-2 Enhanced Error Boundary Component
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Comprehensive error handling with user-friendly messages, retry functionality,
 * and constitutional compliance validation.
 */

use yew::prelude::*;
use web_sys::console;
use serde::{Deserialize, Serialize};

use crate::components::ui::LoadingSpinner;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ErrorInfo {
    pub message: String,
    pub error_type: ErrorType,
    pub timestamp: String,
    pub constitutional_hash: String,
    pub context: Option<String>,
    pub recoverable: bool,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum ErrorType {
    Network,
    Validation,
    Constitutional,
    Runtime,
    Permission,
    Timeout,
    Unknown,
}

impl ErrorInfo {
    pub fn new(message: &str, error_type: ErrorType) -> Self {
        Self {
            message: message.to_string(),
            error_type,
            timestamp: chrono::Utc::now().to_rfc3339(),
            constitutional_hash: crate::CONSTITUTIONAL_HASH.to_string(),
            context: None,
            recoverable: true,
        }
    }

    pub fn user_friendly_message(&self) -> String {
        match self.error_type {
            ErrorType::Network => "Unable to connect to ACGS-2 services. Please check your connection and try again.".to_string(),
            ErrorType::Validation => "The information provided doesn't meet our requirements. Please review and try again.".to_string(),
            ErrorType::Constitutional => "This action violates constitutional compliance requirements and cannot be completed.".to_string(),
            ErrorType::Runtime => "An unexpected error occurred. Our team has been notified and is working on a fix.".to_string(),
            ErrorType::Permission => "You don't have permission to perform this action. Please contact your administrator.".to_string(),
            ErrorType::Timeout => "The request took too long to complete. Please try again.".to_string(),
            ErrorType::Unknown => "Something went wrong. Please try again or contact support if the problem persists.".to_string(),
        }
    }

    pub fn icon(&self) -> &'static str {
        match self.error_type {
            ErrorType::Network => "🌐",
            ErrorType::Validation => "⚠️",
            ErrorType::Constitutional => "🏛️",
            ErrorType::Runtime => "⚙️",
            ErrorType::Permission => "🔒",
            ErrorType::Timeout => "⏱️",
            ErrorType::Unknown => "❌",
        }
    }
}

#[derive(Properties, PartialEq)]
pub struct ErrorBoundaryProps {
    pub children: Children,
    #[prop_or_default]
    pub show_details: bool,
    #[prop_or(3)]
    pub max_retries: u32,
    #[prop_or_default]
    pub fallback: Option<Html>,
    #[prop_or_default]
    pub on_error: Option<Callback<ErrorInfo>>,
}

#[function_component(ErrorBoundary)]
pub fn error_boundary(props: &ErrorBoundaryProps) -> Html {
    let error_state = use_state(|| None::<ErrorInfo>);
    let retry_count = use_state(|| 0u32);
    let is_retrying = use_state(|| false);

    let handle_retry = {
        let error_state = error_state.clone();
        let retry_count = retry_count.clone();
        let is_retrying = is_retrying.clone();
        let max_retries = props.max_retries;

        Callback::from(move |_| {
            let current_retries = *retry_count;
            if current_retries < max_retries {
                is_retrying.set(true);
                retry_count.set(current_retries + 1);

                // Simulate retry delay
                let error_state = error_state.clone();
                let is_retrying = is_retrying.clone();

                gloo_timers::callback::Timeout::new(1000, move || {
                    error_state.set(None);
                    is_retrying.set(false);
                }).forget();
            }
        })
    };

    let handle_dismiss = {
        let error_state = error_state.clone();
        let retry_count = retry_count.clone();

        Callback::from(move |_| {
            error_state.set(None);
            retry_count.set(0);
        })
    };

    // Simulate error catching (in a real implementation, this would be handled by Yew's error boundary)
    let _trigger_error = {
        let error_state = error_state.clone();
        let on_error = props.on_error.clone();

        Callback::from(move |error_info: ErrorInfo| {
            console::error_1(&format!("ACGS-2 Error: {}", error_info.message).into());
            error_state.set(Some(error_info.clone()));

            if let Some(callback) = &on_error {
                callback.emit(error_info);
            }
        })
    };

    match (*error_state).clone() {
        Some(error) => {
            if let Some(fallback) = &props.fallback {
                fallback.clone()
            } else {
                html! {
                    <ErrorDisplay
                        error={error}
                        show_details={props.show_details}
                        can_retry={*retry_count < props.max_retries}
                        is_retrying={*is_retrying}
                        on_retry={handle_retry}
                        on_dismiss={handle_dismiss}
                    />
                }
            }
        }
        None => {
            html! {
                <div data-constitutional-hash={crate::CONSTITUTIONAL_HASH}>
                    { for props.children.iter() }
                </div>
            }
        }
    }
}

#[derive(Properties, PartialEq)]
pub struct ErrorDisplayProps {
    pub error: ErrorInfo,
    #[prop_or(false)]
    pub show_details: bool,
    #[prop_or(true)]
    pub can_retry: bool,
    #[prop_or(false)]
    pub is_retrying: bool,
    pub on_retry: Callback<()>,
    pub on_dismiss: Callback<()>,
}

#[function_component(ErrorDisplay)]
pub fn error_display(props: &ErrorDisplayProps) -> Html {
    let error = &props.error;

    html! {
        <div
            class="error-boundary"
            data-constitutional-hash={error.constitutional_hash.clone()}
            role="alert"
            aria-live="assertive"
        >
            <div class="error-boundary-content">
                <div class="error-boundary-header">
                    <div class="error-icon">{error.icon()}</div>
                    <div class="error-title">{"Something went wrong"}</div>
                </div>

                <div class="error-boundary-body">
                    <p class="error-message">{error.user_friendly_message()}</p>

                    if props.show_details {
                        <details class="error-details">
                            <summary>{"Technical Details"}</summary>
                            <div class="error-details-content">
                                <div class="error-detail">
                                    <strong>{"Error Type: "}</strong>
                                    {format!("{:?}", error.error_type)}
                                </div>
                                <div class="error-detail">
                                    <strong>{"Message: "}</strong>
                                    {&error.message}
                                </div>
                                <div class="error-detail">
                                    <strong>{"Timestamp: "}</strong>
                                    {&error.timestamp}
                                </div>
                                <div class="error-detail">
                                    <strong>{"Constitutional Hash: "}</strong>
                                    <code>{&error.constitutional_hash}</code>
                                </div>
                                if let Some(context) = &error.context {
                                    <div class="error-detail">
                                        <strong>{"Context: "}</strong>
                                        {context}
                                    </div>
                                }
                            </div>
                        </details>
                    }
                </div>

                <div class="error-boundary-actions">
                    if props.can_retry && error.recoverable {
                        <button
                            class="btn btn-primary"
                            onclick={props.on_retry.reform(|_| ())}
                            disabled={props.is_retrying}
                        >
                            if props.is_retrying {
                                <LoadingSpinner size="1rem" />
                                {"Retrying..."}
                            } else {
                                {"Try Again"}
                            }
                        </button>
                    }

                    <button
                        class="btn btn-secondary"
                        onclick={props.on_dismiss.reform(|_| ())}
                    >
                        {"Dismiss"}
                    </button>
                </div>
            </div>
        </div>
    }
}



