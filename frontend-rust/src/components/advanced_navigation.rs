/*!
 * ACGS-2 Advanced Navigation Component
 * Constitutional Hash: cdd01ef066bc6cf2
 * 
 * Enhanced navigation with breadcrumbs, search, and keyboard shortcuts
 */

use yew::prelude::*;
use web_sys::{HtmlInputElement, KeyboardEvent};

use crate::components::ui::ValidatedInput;

#[derive(Debug, Clone, PartialEq)]
pub struct NavigationItem {
    pub id: String,
    pub label: String,
    pub icon: String,
    pub path: String,
    pub description: String,
    pub keywords: Vec<String>,
    pub constitutional_level: ConstitutionalLevel,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ConstitutionalLevel {
    Core,
    Standard,
    Administrative,
}

impl NavigationItem {
    pub fn matches_search(&self, query: &str) -> bool {
        let query_lower = query.to_lowercase();
        self.label.to_lowercase().contains(&query_lower) ||
        self.description.to_lowercase().contains(&query_lower) ||
        self.keywords.iter().any(|k| k.to_lowercase().contains(&query_lower))
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct BreadcrumbItem {
    pub label: String,
    pub path: String,
    pub icon: Option<String>,
}

#[derive(Properties, PartialEq)]
pub struct AdvancedNavigationProps {
    #[prop_or_default]
    pub current_path: String,
    #[prop_or_default]
    pub breadcrumbs: Vec<BreadcrumbItem>,
    #[prop_or_default]
    pub on_navigate: Option<Callback<String>>,
    #[prop_or(false)]
    pub show_search: bool,
    #[prop_or(false)]
    pub show_shortcuts: bool,
}

#[function_component(AdvancedNavigation)]
pub fn advanced_navigation(props: &AdvancedNavigationProps) -> Html {
    let search_query = use_state(|| String::new());
    let search_results = use_state(|| Vec::<NavigationItem>::new());
    let show_search_results = use_state(|| false);
    let search_input_ref = use_node_ref();

    // Navigation items
    let nav_items = vec![
        NavigationItem {
            id: "dashboard".to_string(),
            label: "Dashboard".to_string(),
            icon: "🏠".to_string(),
            path: "/dashboard".to_string(),
            description: "Main dashboard with system overview".to_string(),
            keywords: vec!["home", "overview", "main", "status"].iter().map(|s| s.to_string()).collect(),
            constitutional_level: ConstitutionalLevel::Core,
        },
        NavigationItem {
            id: "constitutional".to_string(),
            label: "Constitutional".to_string(),
            icon: "🏛️".to_string(),
            path: "/constitutional".to_string(),
            description: "Constitutional compliance and governance".to_string(),
            keywords: vec!["compliance", "governance", "rules", "constitution"].iter().map(|s| s.to_string()).collect(),
            constitutional_level: ConstitutionalLevel::Core,
        },
        NavigationItem {
            id: "services".to_string(),
            label: "Services".to_string(),
            icon: "⚙️".to_string(),
            path: "/services".to_string(),
            description: "ACGS-2 service management and monitoring".to_string(),
            keywords: vec!["services", "monitoring", "health", "status"].iter().map(|s| s.to_string()).collect(),
            constitutional_level: ConstitutionalLevel::Standard,
        },
        NavigationItem {
            id: "governance".to_string(),
            label: "Governance".to_string(),
            icon: "📋".to_string(),
            path: "/governance".to_string(),
            description: "Policy governance and rule management".to_string(),
            keywords: vec!["policy", "rules", "management", "governance"].iter().map(|s| s.to_string()).collect(),
            constitutional_level: ConstitutionalLevel::Core,
        },
        NavigationItem {
            id: "audit".to_string(),
            label: "Audit".to_string(),
            icon: "📊".to_string(),
            path: "/audit".to_string(),
            description: "Audit logs and compliance tracking".to_string(),
            keywords: vec!["audit", "logs", "tracking", "history"].iter().map(|s| s.to_string()).collect(),
            constitutional_level: ConstitutionalLevel::Standard,
        },
        NavigationItem {
            id: "settings".to_string(),
            label: "Settings".to_string(),
            icon: "⚙️".to_string(),
            path: "/settings".to_string(),
            description: "System settings and user preferences".to_string(),
            keywords: vec!["settings", "preferences", "configuration", "options"].iter().map(|s| s.to_string()).collect(),
            constitutional_level: ConstitutionalLevel::Administrative,
        },
    ];

    // Search functionality
    let on_search_input = {
        let search_query = search_query.clone();
        let search_results = search_results.clone();
        let show_search_results = show_search_results.clone();
        let nav_items = nav_items.clone();
        
        Callback::from(move |query: String| {
            search_query.set(query.clone());
            
            if query.trim().is_empty() {
                show_search_results.set(false);
                search_results.set(Vec::new());
            } else {
                let results: Vec<NavigationItem> = nav_items
                    .iter()
                    .filter(|item| item.matches_search(&query))
                    .cloned()
                    .collect();
                
                search_results.set(results);
                show_search_results.set(true);
            }
        })
    };

    // Keyboard shortcuts
    let on_keydown = {
        let search_input_ref = search_input_ref.clone();
        
        Callback::from(move |e: KeyboardEvent| {
            // Ctrl+K or Cmd+K to focus search
            if (e.ctrl_key() || e.meta_key()) && e.key() == "k" {
                e.prevent_default();
                if let Some(input) = search_input_ref.cast::<HtmlInputElement>() {
                    let _ = input.focus();
                }
            }
            
            // Escape to close search results
            if e.key() == "Escape" {
                // Handle escape logic here
            }
        })
    };

    // Navigation handler
    let on_navigate_item = {
        let on_navigate = props.on_navigate.clone();
        let show_search_results = show_search_results.clone();
        let search_query = search_query.clone();
        
        Callback::from(move |path: String| {
            show_search_results.set(false);
            search_query.set(String::new());
            
            if let Some(callback) = &on_navigate {
                callback.emit(path);
            }
        })
    };

    html! {
        <div 
            class="advanced-navigation" 
            data-constitutional-hash={crate::CONSTITUTIONAL_HASH}
            onkeydown={on_keydown}
        >
            // Breadcrumbs
            if !props.breadcrumbs.is_empty() {
                <nav class="breadcrumbs" aria-label="Breadcrumb">
                    <ol class="breadcrumb-list">
                        { for props.breadcrumbs.iter().enumerate().map(|(index, item)| {
                            let is_last = index == props.breadcrumbs.len() - 1;
                            let path = item.path.clone();
                            let on_navigate = on_navigate_item.clone();
                            
                            html! {
                                <li class="breadcrumb-item">
                                    if is_last {
                                        <span class="breadcrumb-current">
                                            if let Some(icon) = &item.icon {
                                                <span class="breadcrumb-icon">{icon}</span>
                                            }
                                            {&item.label}
                                        </span>
                                    } else {
                                        <button 
                                            class="breadcrumb-link"
                                            onclick={Callback::from(move |_| on_navigate.emit(path.clone()))}
                                        >
                                            if let Some(icon) = &item.icon {
                                                <span class="breadcrumb-icon">{icon}</span>
                                            }
                                            {&item.label}
                                        </button>
                                        <span class="breadcrumb-separator">{"/"}</span>
                                    }
                                </li>
                            }
                        })}
                    </ol>
                </nav>
            }

            // Search bar
            if props.show_search {
                <div class="navigation-search">
                    <div class="search-container">
                        <ValidatedInput
                            input_ref={search_input_ref}
                            placeholder="Search navigation... (Ctrl+K)"
                            value={(*search_query).clone()}
                            on_change={Some(on_search_input)}
                            class={classes!("search-input")}
                        />
                        
                        if *show_search_results && !search_results.is_empty() {
                            <div class="search-results">
                                { for search_results.iter().map(|item| {
                                    let path = item.path.clone();
                                    let on_navigate = on_navigate_item.clone();
                                    let constitutional_class = match item.constitutional_level {
                                        ConstitutionalLevel::Core => "constitutional-core",
                                        ConstitutionalLevel::Standard => "constitutional-standard",
                                        ConstitutionalLevel::Administrative => "constitutional-admin",
                                    };
                                    
                                    html! {
                                        <button 
                                            class={classes!("search-result-item", constitutional_class)}
                                            onclick={Callback::from(move |_| on_navigate.emit(path.clone()))}
                                        >
                                            <div class="search-result-icon">{&item.icon}</div>
                                            <div class="search-result-content">
                                                <div class="search-result-title">{&item.label}</div>
                                                <div class="search-result-description">{&item.description}</div>
                                            </div>
                                            <div class="search-result-badge">
                                                {match item.constitutional_level {
                                                    ConstitutionalLevel::Core => "Core",
                                                    ConstitutionalLevel::Standard => "Standard",
                                                    ConstitutionalLevel::Administrative => "Admin",
                                                }}
                                            </div>
                                        </button>
                                    }
                                })}
                            </div>
                        }
                    </div>
                </div>
            }

            // Keyboard shortcuts help
            if props.show_shortcuts {
                <div class="keyboard-shortcuts">
                    <div class="shortcuts-title">{"Keyboard Shortcuts"}</div>
                    <div class="shortcuts-list">
                        <div class="shortcut-item">
                            <kbd>{"Ctrl"}</kbd>{" + "}<kbd>{"K"}</kbd>
                            <span>{"Focus search"}</span>
                        </div>
                        <div class="shortcut-item">
                            <kbd>{"Esc"}</kbd>
                            <span>{"Close search"}</span>
                        </div>
                    </div>
                </div>
            }
        </div>
    }
}
