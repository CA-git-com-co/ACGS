/*!
 * ACGS-2 User Preferences Component
 * Constitutional Hash: cdd01ef066bc6cf2
 * 
 * Comprehensive user preference management with theme, language, and layout options
 */

use yew::prelude::*;
// Removed unused import: Storage
use serde::{Deserialize, Serialize};

use crate::components::ui::{ValidatedInput, ValidationRule};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct UserPreferences {
    pub theme: Theme,
    pub language: String,
    pub notifications_enabled: bool,
    pub auto_save: bool,
    pub performance_monitoring: bool,
    pub layout_density: LayoutDensity,
    pub constitutional_alerts: bool,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Theme {
    Light,
    Dark,
    System,
    Constitutional,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum LayoutDensity {
    Compact,
    Comfortable,
    Spacious,
}

impl Default for UserPreferences {
    fn default() -> Self {
        Self {
            theme: Theme::System,
            language: "en".to_string(),
            notifications_enabled: true,
            auto_save: true,
            performance_monitoring: true,
            layout_density: LayoutDensity::Comfortable,
            constitutional_alerts: true,
        }
    }
}

impl UserPreferences {
    pub fn load_from_storage() -> Self {
        if let Some(storage) = web_sys::window().and_then(|w| w.local_storage().ok().flatten()) {
            if let Ok(Some(prefs_json)) = storage.get_item("acgs_user_preferences") {
                if let Ok(prefs) = serde_json::from_str::<UserPreferences>(&prefs_json) {
                    return prefs;
                }
            }
        }
        Self::default()
    }

    pub fn save_to_storage(&self) {
        if let Some(storage) = web_sys::window().and_then(|w| w.local_storage().ok().flatten()) {
            if let Ok(prefs_json) = serde_json::to_string(self) {
                let _ = storage.set_item("acgs_user_preferences", &prefs_json);
            }
        }
    }
}

#[derive(Properties, PartialEq)]
pub struct UserPreferencesProps {
    #[prop_or_default]
    pub on_change: Option<Callback<UserPreferences>>,
}

#[function_component(UserPreferencesPanel)]
pub fn user_preferences_panel(props: &UserPreferencesProps) -> Html {
    let preferences = use_state(|| UserPreferences::load_from_storage());

    let update_preferences = {
        let preferences = preferences.clone();
        let on_change = props.on_change.clone();
        
        Callback::from(move |new_prefs: UserPreferences| {
            new_prefs.save_to_storage();
            preferences.set(new_prefs.clone());
            
            if let Some(callback) = &on_change {
                callback.emit(new_prefs);
            }
        })
    };

    let on_theme_change = {
        let preferences = preferences.clone();
        let update_preferences = update_preferences.clone();
        
        Callback::from(move |event: Event| {
            let target: web_sys::HtmlSelectElement = event.target_unchecked_into();
            let theme = match target.value().as_str() {
                "light" => Theme::Light,
                "dark" => Theme::Dark,
                "constitutional" => Theme::Constitutional,
                _ => Theme::System,
            };
            
            let mut new_prefs = (*preferences).clone();
            new_prefs.theme = theme;
            update_preferences.emit(new_prefs);
        })
    };

    let on_language_change = {
        let preferences = preferences.clone();
        let update_preferences = update_preferences.clone();
        
        Callback::from(move |language: String| {
            let mut new_prefs = (*preferences).clone();
            new_prefs.language = language;
            update_preferences.emit(new_prefs);
        })
    };

    let on_toggle_notifications = {
        let preferences = preferences.clone();
        let update_preferences = update_preferences.clone();
        
        Callback::from(move |_| {
            let mut new_prefs = (*preferences).clone();
            new_prefs.notifications_enabled = !new_prefs.notifications_enabled;
            update_preferences.emit(new_prefs);
        })
    };

    let on_toggle_auto_save = {
        let preferences = preferences.clone();
        let update_preferences = update_preferences.clone();
        
        Callback::from(move |_| {
            let mut new_prefs = (*preferences).clone();
            new_prefs.auto_save = !new_prefs.auto_save;
            update_preferences.emit(new_prefs);
        })
    };

    let on_toggle_performance_monitoring = {
        let preferences = preferences.clone();
        let update_preferences = update_preferences.clone();
        
        Callback::from(move |_| {
            let mut new_prefs = (*preferences).clone();
            new_prefs.performance_monitoring = !new_prefs.performance_monitoring;
            update_preferences.emit(new_prefs);
        })
    };

    let on_toggle_constitutional_alerts = {
        let preferences = preferences.clone();
        let update_preferences = update_preferences.clone();
        
        Callback::from(move |_| {
            let mut new_prefs = (*preferences).clone();
            new_prefs.constitutional_alerts = !new_prefs.constitutional_alerts;
            update_preferences.emit(new_prefs);
        })
    };

    html! {
        <div class="user-preferences-panel" data-constitutional-hash={crate::CONSTITUTIONAL_HASH}>
            <div class="preferences-header">
                <h2>{"User Preferences"}</h2>
                <p class="preferences-subtitle">{"Customize your ACGS-2 experience"}</p>
            </div>

            <div class="preferences-content">
                <div class="preference-section">
                    <h3>{"Appearance"}</h3>
                    
                    <div class="preference-item">
                        <label class="preference-label">{"Theme"}</label>
                        <select 
                            class="preference-select"
                            onchange={on_theme_change}
                            value={match preferences.theme {
                                Theme::Light => "light",
                                Theme::Dark => "dark",
                                Theme::Constitutional => "constitutional",
                                Theme::System => "system",
                            }}
                        >
                            <option value="system">{"System Default"}</option>
                            <option value="light">{"Light"}</option>
                            <option value="dark">{"Dark"}</option>
                            <option value="constitutional">{"Constitutional"}</option>
                        </select>
                    </div>

                    <div class="preference-item">
                        <ValidatedInput
                            label="Language"
                            value={preferences.language.clone()}
                            placeholder="Language code (e.g., en, es, fr)"
                            rules={vec![
                                ValidationRule::required(),
                            ]}
                            on_change={Some(on_language_change)}
                        />
                    </div>
                </div>

                <div class="preference-section">
                    <h3>{"Notifications"}</h3>
                    
                    <div class="preference-item">
                        <label class="preference-checkbox">
                            <input 
                                type="checkbox" 
                                checked={preferences.notifications_enabled}
                                onchange={on_toggle_notifications}
                            />
                            <span class="checkbox-label">{"Enable notifications"}</span>
                        </label>
                    </div>

                    <div class="preference-item">
                        <label class="preference-checkbox">
                            <input 
                                type="checkbox" 
                                checked={preferences.constitutional_alerts}
                                onchange={on_toggle_constitutional_alerts}
                            />
                            <span class="checkbox-label">{"Constitutional compliance alerts"}</span>
                        </label>
                    </div>
                </div>

                <div class="preference-section">
                    <h3>{"System"}</h3>
                    
                    <div class="preference-item">
                        <label class="preference-checkbox">
                            <input 
                                type="checkbox" 
                                checked={preferences.auto_save}
                                onchange={on_toggle_auto_save}
                            />
                            <span class="checkbox-label">{"Auto-save preferences"}</span>
                        </label>
                    </div>

                    <div class="preference-item">
                        <label class="preference-checkbox">
                            <input 
                                type="checkbox" 
                                checked={preferences.performance_monitoring}
                                onchange={on_toggle_performance_monitoring}
                            />
                            <span class="checkbox-label">{"Performance monitoring"}</span>
                        </label>
                    </div>
                </div>

                <div class="preference-section">
                    <h3>{"Constitutional Compliance"}</h3>
                    <div class="constitutional-info">
                        <div class="constitutional-hash">
                            <strong>{"Hash: "}</strong>
                            <code>{crate::CONSTITUTIONAL_HASH}</code>
                        </div>
                        <div class="constitutional-status">
                            <span class="status-indicator status-compliant">{"✓ Compliant"}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="preferences-footer">
                <button class="btn btn-secondary" onclick={Callback::from(|_| {
                    if let Some(storage) = web_sys::window().and_then(|w| w.local_storage().ok().flatten()) {
                        let _ = storage.remove_item("acgs_user_preferences");
                        web_sys::window().unwrap().location().reload().unwrap();
                    }
                })}>
                    {"Reset to Defaults"}
                </button>
            </div>
        </div>
    }
}
