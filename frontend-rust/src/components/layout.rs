/*!
 * ACGS-2 Layout Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use yew::prelude::*;

use crate::components::ConstitutionalIndicator;

#[derive(Properties, PartialEq)]
pub struct LayoutProps {
    pub children: Children,
}

#[function_component(Layout)]
pub fn layout(props: &LayoutProps) -> Html {
    html! {
        <div class="layout" data-constitutional-hash={crate::CONSTITUTIONAL_HASH}>
            <header class="layout-header">
                <div class="header-content">
                    <div class="header-brand">
                        <h1 class="brand-title">{"ACGS-2"}</h1>
                        <span class="brand-subtitle">{"Constitutional AI Governance"}</span>
                    </div>
                    <div class="header-status">
                        <ConstitutionalIndicator />
                    </div>
                </div>
            </header>

            <main class="layout-main">
                <div class="main-content">
                    { for props.children.iter() }
                </div>
            </main>

            <footer class="layout-footer">
                <div class="footer-content">
                    <span class="footer-text">
                        {"ACGS-2 Constitutional AI Governance System"}
                    </span>
                    <span class="footer-hash">
                        {"Hash: "}{&crate::CONSTITUTIONAL_HASH[..8]}
                    </span>
                </div>
            </footer>
        </div>
    }
}
