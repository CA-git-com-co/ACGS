/*!
 * ACGS-2 Constitutional Components
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use yew::prelude::*;



#[function_component(ConstitutionalIndicator)]
pub fn constitutional_indicator() -> Html {
    // Mock compliance data for now
    let compliant = true;
    let score = 98.7;

    let status_class = if compliant {
        "constitutional-indicator compliant"
    } else {
        "constitutional-indicator non-compliant"
    };

    let status_text = if compliant {
        "Compliant"
    } else {
        "Violation"
    };

    let status_icon = if compliant {
        "✅"
    } else {
        "❌"
    };

    html! {
        <div class={status_class}>
            <span class="indicator-icon">{status_icon}</span>
            <span class="indicator-text">{status_text}</span>
            <span class="indicator-score">{format!("{:.1}%", score)}</span>
            <span class="indicator-hash">{&crate::CONSTITUTIONAL_HASH[..8]}</span>
        </div>
    }
}


