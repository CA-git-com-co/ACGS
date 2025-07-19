/*!
 * ACGS-2 Navigation Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use yew::prelude::*;

#[function_component(Navigation)]
pub fn navigation() -> Html {
    let nav_items = vec![
        ("Dashboard", "🏠"),
        ("Constitutional", "🏛️"),
        ("Services", "⚙️"),
        ("Governance", "📋"),
        ("Audit", "📊"),
        ("Settings", "⚙️"),
    ];

    html! {
        <nav class="navigation" data-constitutional-hash={crate::CONSTITUTIONAL_HASH}>
            <div class="nav-header">
                <h2 class="nav-title">{"Navigation"}</h2>
            </div>

            <ul class="nav-list">
                { for nav_items.iter().map(|(label, icon)| {
                    let label_owned = label.to_string();
                    let onclick = Callback::from(move |_| {
                        log::info!("Navigation to {} clicked", label_owned);
                    });

                    html! {
                        <li class="nav-item">
                            <button class="nav-link" onclick={onclick}>
                                <span class="nav-icon">{icon}</span>
                                <span class="nav-label">{label}</span>
                            </button>
                        </li>
                    }
                })}
            </ul>

            <div class="nav-footer">
                <div class="constitutional-badge">
                    <span class="badge-icon">{"🏛️"}</span>
                    <span class="badge-text">{"Constitutional"}</span>
                </div>
            </div>
        </nav>
    }
}
