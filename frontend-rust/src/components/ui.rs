/*!
 * ACGS-2 Enhanced UI Components
 * Constitutional Hash: cdd01ef066bc6cf2
 * 
 * Comprehensive UI component library with skeleton loading, toast notifications,
 * form validation, progressive disclosure, and accessibility features.
 */

use yew::prelude::*;
// Removed unused imports: window, Element
use gloo_timers::callback::Timeout;
// Removed unused import: HashMap
use serde::{Deserialize, Serialize};

// Removed unused imports: use_app_state, AppAction

// ============================================================================
// SKELETON LOADING COMPONENTS
// ============================================================================

#[derive(Properties, PartialEq)]
pub struct SkeletonProps {
    #[prop_or_default]
    pub width: Option<String>,
    #[prop_or_default]
    pub height: Option<String>,
    #[prop_or_default]
    pub class: Classes,
    #[prop_or(false)]
    pub circle: bool,
    #[prop_or(false)]
    pub animated: bool,
}

#[function_component(Skeleton)]
pub fn skeleton(props: &SkeletonProps) -> Html {
    let mut classes = classes!("skeleton");
    if props.animated {
        classes.push("skeleton-animated");
    }
    if props.circle {
        classes.push("skeleton-circle");
    }
    classes.extend(props.class.clone());

    let style = format!(
        "{}{}",
        props.width.as_ref().map(|w| format!("width: {}; ", w)).unwrap_or_default(),
        props.height.as_ref().map(|h| format!("height: {}; ", h)).unwrap_or_default()
    );

    html! {
        <div 
            class={classes} 
            style={style}
            data-constitutional-hash={crate::CONSTITUTIONAL_HASH}
        />
    }
}

#[function_component(SkeletonCard)]
pub fn skeleton_card() -> Html {
    html! {
        <div class="skeleton-card" data-constitutional-hash={crate::CONSTITUTIONAL_HASH}>
            <div class="skeleton-card-header">
                <Skeleton width="60%" height="1.5rem" animated=true />
                <Skeleton width="20%" height="1rem" animated=true />
            </div>
            <div class="skeleton-card-content">
                <Skeleton width="100%" height="1rem" animated=true />
                <Skeleton width="80%" height="1rem" animated=true />
                <Skeleton width="90%" height="1rem" animated=true />
            </div>
            <div class="skeleton-card-footer">
                <Skeleton width="30%" height="2rem" animated=true />
            </div>
        </div>
    }
}

#[function_component(SkeletonDashboard)]
pub fn skeleton_dashboard() -> Html {
    html! {
        <div class="skeleton-dashboard" data-constitutional-hash={crate::CONSTITUTIONAL_HASH}>
            <div class="skeleton-dashboard-header">
                <Skeleton width="300px" height="2rem" animated=true />
                <Skeleton width="150px" height="1.5rem" animated=true />
            </div>
            <div class="skeleton-dashboard-grid">
                { for (0..6).map(|_| html! { <SkeletonCard /> }) }
            </div>
        </div>
    }
}

// ============================================================================
// TOAST NOTIFICATION SYSTEM
// ============================================================================

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum ToastType {
    Success,
    Error,
    Warning,
    Info,
    Constitutional,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ToastMessage {
    pub id: String,
    pub title: String,
    pub message: String,
    pub toast_type: ToastType,
    pub duration: Option<u32>, // Duration in milliseconds
    pub dismissible: bool,
    pub constitutional_hash: String,
}

impl ToastMessage {
    pub fn new(title: &str, message: &str, toast_type: ToastType) -> Self {
        Self {
            id: format!("{}-{}", chrono::Utc::now().timestamp_millis(), (js_sys::Math::random() * 1000000.0) as u32),
            title: title.to_string(),
            message: message.to_string(),
            toast_type,
            duration: Some(5000), // 5 seconds default
            dismissible: true,
            constitutional_hash: crate::CONSTITUTIONAL_HASH.to_string(),
        }
    }

    pub fn constitutional(title: &str, message: &str) -> Self {
        Self::new(title, message, ToastType::Constitutional)
    }

    pub fn success(title: &str, message: &str) -> Self {
        Self::new(title, message, ToastType::Success)
    }

    pub fn error(title: &str, message: &str) -> Self {
        Self::new(title, message, ToastType::Error)
    }

    pub fn warning(title: &str, message: &str) -> Self {
        Self::new(title, message, ToastType::Warning)
    }

    pub fn info(title: &str, message: &str) -> Self {
        Self::new(title, message, ToastType::Info)
    }
}

#[derive(Properties, PartialEq)]
pub struct ToastProps {
    pub toast: ToastMessage,
    pub on_dismiss: Callback<String>,
}

#[function_component(Toast)]
pub fn toast(props: &ToastProps) -> Html {
    let toast = &props.toast;
    let on_dismiss = props.on_dismiss.clone();
    let toast_id = toast.id.clone();

    // Auto-dismiss timer
    use_effect_with(toast.clone(), {
        let on_dismiss = on_dismiss.clone();
        let toast_id = toast_id.clone();
        move |toast| {
            if let Some(duration) = toast.duration {
                let timeout = Timeout::new(duration, move || {
                    on_dismiss.emit(toast_id.clone());
                });
                timeout.forget();
            }
        }
    });

    let toast_class = match toast.toast_type {
        ToastType::Success => "toast toast-success",
        ToastType::Error => "toast toast-error",
        ToastType::Warning => "toast toast-warning",
        ToastType::Info => "toast toast-info",
        ToastType::Constitutional => "toast toast-constitutional",
    };

    let icon = match toast.toast_type {
        ToastType::Success => "✅",
        ToastType::Error => "❌",
        ToastType::Warning => "⚠️",
        ToastType::Info => "ℹ️",
        ToastType::Constitutional => "🏛️",
    };

    let dismiss_click = {
        let on_dismiss = on_dismiss.clone();
        let toast_id = toast.id.clone();
        Callback::from(move |_| {
            on_dismiss.emit(toast_id.clone());
        })
    };

    html! {
        <div
            class={toast_class}
            data-constitutional-hash={toast.constitutional_hash.clone()}
            role="alert"
            aria-live="polite"
        >
            <div class="toast-icon">{icon}</div>
            <div class="toast-content">
                <div class="toast-title">{&toast.title}</div>
                <div class="toast-message">{&toast.message}</div>
            </div>
            if toast.dismissible {
                <button 
                    class="toast-dismiss"
                    onclick={dismiss_click}
                    aria-label="Dismiss notification"
                >
                    {"×"}
                </button>
            }
        </div>
    }
}

#[function_component(ToastContainer)]
pub fn toast_container() -> Html {
    let toasts = use_state(|| Vec::<ToastMessage>::new());

    let on_dismiss = {
        let toasts = toasts.clone();
        Callback::from(move |toast_id: String| {
            let mut current_toasts = (*toasts).clone();
            current_toasts.retain(|t| t.id != toast_id);
            toasts.set(current_toasts);
        })
    };

    html! {
        <div 
            class="toast-container"
            data-constitutional-hash={crate::CONSTITUTIONAL_HASH}
            aria-live="polite"
            aria-label="Notifications"
        >
            { for toasts.iter().map(|toast| {
                html! {
                    <Toast 
                        key={toast.id.clone()}
                        toast={toast.clone()} 
                        on_dismiss={on_dismiss.clone()} 
                    />
                }
            })}
        </div>
    }
}

// ============================================================================
// LOADING STATES
// ============================================================================

#[derive(Properties, PartialEq)]
pub struct LoadingSpinnerProps {
    #[prop_or_default]
    pub size: Option<String>,
    #[prop_or_default]
    pub color: Option<String>,
    #[prop_or_default]
    pub class: Classes,
}

#[function_component(LoadingSpinner)]
pub fn loading_spinner(props: &LoadingSpinnerProps) -> Html {
    let mut classes = classes!("loading-spinner");
    classes.extend(props.class.clone());

    let style = format!(
        "{}{}",
        props.size.as_ref().map(|s| format!("width: {}; height: {}; ", s, s)).unwrap_or_default(),
        props.color.as_ref().map(|c| format!("border-top-color: {}; ", c)).unwrap_or_default()
    );

    html! {
        <div 
            class={classes}
            style={style}
            data-constitutional-hash={crate::CONSTITUTIONAL_HASH}
            role="status"
            aria-label="Loading"
        >
            <div class="spinner" />
        </div>
    }
}

// ============================================================================
// FORM VALIDATION COMPONENTS
// ============================================================================

#[derive(Clone)]
pub struct ValidationRule {
    pub name: String,
    pub message: String,
    pub validator: fn(&str) -> bool,
}

impl PartialEq for ValidationRule {
    fn eq(&self, other: &Self) -> bool {
        self.name == other.name && self.message == other.message
    }
}

impl ValidationRule {
    pub fn required() -> Self {
        Self {
            name: "required".to_string(),
            message: "This field is required".to_string(),
            validator: |value| !value.trim().is_empty(),
        }
    }

    pub fn email() -> Self {
        Self {
            name: "email".to_string(),
            message: "Must be a valid email address".to_string(),
            validator: |value| {
                // Simple email validation without regex dependency
                value.contains('@') &&
                value.contains('.') &&
                value.len() > 5 &&
                !value.starts_with('@') &&
                !value.ends_with('@') &&
                !value.starts_with('.') &&
                !value.ends_with('.')
            },
        }
    }

    pub fn constitutional_hash() -> Self {
        Self {
            name: "constitutional_hash".to_string(),
            message: "Must be a valid constitutional hash".to_string(),
            validator: |value| {
                value.len() == 16 && value.chars().all(|c| c.is_ascii_hexdigit())
            },
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct ValidationResult {
    pub valid: bool,
    pub errors: Vec<String>,
}

impl ValidationResult {
    pub fn valid() -> Self {
        Self {
            valid: true,
            errors: Vec::new(),
        }
    }

    pub fn invalid(errors: Vec<String>) -> Self {
        Self {
            valid: false,
            errors,
        }
    }
}

#[derive(Properties, PartialEq)]
pub struct ValidatedInputProps {
    #[prop_or_default]
    pub value: String,
    #[prop_or_default]
    pub placeholder: String,
    #[prop_or_default]
    pub label: String,
    #[prop_or_default]
    pub input_type: String,
    #[prop_or_default]
    pub rules: Vec<ValidationRule>,
    #[prop_or_default]
    pub on_change: Option<Callback<String>>,
    #[prop_or_default]
    pub on_validation: Option<Callback<ValidationResult>>,
    #[prop_or(false)]
    pub disabled: bool,
    #[prop_or(false)]
    pub required: bool,
    #[prop_or_default]
    pub class: Classes,
    #[prop_or_default]
    pub input_ref: Option<NodeRef>,
}

#[function_component(ValidatedInput)]
pub fn validated_input(props: &ValidatedInputProps) -> Html {
    let validation_result = use_state(|| ValidationResult::valid());
    let is_touched = use_state(|| false);
    let is_focused = use_state(|| false);

    let validate_value = {
        let rules = props.rules.clone();
        let validation_result = validation_result.clone();
        let on_validation = props.on_validation.clone();

        move |value: &str| {
            let mut errors = Vec::new();

            for rule in &rules {
                if !(rule.validator)(value) {
                    errors.push(rule.message.clone());
                }
            }

            let result = if errors.is_empty() {
                ValidationResult::valid()
            } else {
                ValidationResult::invalid(errors)
            };

            validation_result.set(result.clone());

            if let Some(callback) = &on_validation {
                callback.emit(result);
            }
        }
    };

    let on_input = {
        let validate_value = validate_value.clone();
        let on_change = props.on_change.clone();
        let is_touched = is_touched.clone();

        Callback::from(move |e: InputEvent| {
            let input: web_sys::HtmlInputElement = e.target_unchecked_into();
            let value = input.value();

            is_touched.set(true);
            validate_value(&value);

            if let Some(callback) = &on_change {
                callback.emit(value);
            }
        })
    };

    let on_focus = {
        let is_focused = is_focused.clone();
        Callback::from(move |_| {
            is_focused.set(true);
        })
    };

    let on_blur = {
        let is_focused = is_focused.clone();
        let is_touched = is_touched.clone();
        let validate_value = validate_value.clone();
        let value = props.value.clone();

        Callback::from(move |_| {
            is_focused.set(false);
            is_touched.set(true);
            validate_value(&value);
        })
    };

    let input_class = {
        let mut classes = classes!("form-input");
        if *is_focused {
            classes.push("form-input-focused");
        }
        if *is_touched && !validation_result.valid {
            classes.push("form-input-error");
        }
        if *is_touched && validation_result.valid {
            classes.push("form-input-success");
        }
        classes.extend(props.class.clone());
        classes
    };

    html! {
        <div
            class="form-field"
            data-constitutional-hash={crate::CONSTITUTIONAL_HASH}
        >
            if !props.label.is_empty() {
                <label class="form-label">
                    {&props.label}
                    if props.required {
                        <span class="form-required">{"*"}</span>
                    }
                </label>
            }

            <div class="form-input-container">
                {
                    if let Some(input_ref) = &props.input_ref {
                        html! {
                            <input
                                ref={input_ref.clone()}
                                type={props.input_type.clone()}
                                class={input_class.clone()}
                                value={props.value.clone()}
                                placeholder={props.placeholder.clone()}
                                disabled={props.disabled}
                                required={props.required}
                                oninput={on_input.clone()}
                                onfocus={on_focus.clone()}
                                onblur={on_blur.clone()}
                                aria-invalid={(!validation_result.valid && *is_touched).to_string()}
                                aria-describedby={if !validation_result.errors.is_empty() { "validation-errors" } else { "" }}
                            />
                        }
                    } else {
                        html! {
                            <input
                                type={props.input_type.clone()}
                                class={input_class.clone()}
                                value={props.value.clone()}
                                placeholder={props.placeholder.clone()}
                                disabled={props.disabled}
                                required={props.required}
                                oninput={on_input.clone()}
                                onfocus={on_focus.clone()}
                                onblur={on_blur.clone()}
                                aria-invalid={(!validation_result.valid && *is_touched).to_string()}
                                aria-describedby={if !validation_result.errors.is_empty() { "validation-errors" } else { "" }}
                            />
                        }
                    }
                }

                if *is_touched {
                    <div class="form-validation-icon">
                        if validation_result.valid {
                            <span class="validation-success">{"✓"}</span>
                        } else {
                            <span class="validation-error">{"⚠"}</span>
                        }
                    </div>
                }
            </div>

            if *is_touched && !validation_result.errors.is_empty() {
                <div class="form-validation-errors" id="validation-errors" role="alert">
                    { for validation_result.errors.iter().map(|error| {
                        html! { <div class="validation-error-message">{error}</div> }
                    })}
                </div>
            }
        </div>
    }
}

#[derive(Properties, PartialEq)]
pub struct LoadingOverlayProps {
    #[prop_or_default]
    pub children: Children,
    #[prop_or(false)]
    pub loading: bool,
    #[prop_or_default]
    pub message: Option<String>,
}

#[function_component(LoadingOverlay)]
pub fn loading_overlay(props: &LoadingOverlayProps) -> Html {
    html! {
        <div 
            class="loading-overlay-container"
            data-constitutional-hash={crate::CONSTITUTIONAL_HASH}
        >
            { for props.children.iter() }
            if props.loading {
                <div class="loading-overlay">
                    <div class="loading-overlay-content">
                        <LoadingSpinner size="2rem" />
                        if let Some(message) = &props.message {
                            <div class="loading-message">{message}</div>
                        }
                    </div>
                </div>
            }
        </div>
    }
}
