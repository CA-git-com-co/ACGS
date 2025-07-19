/*!
 * Main Application Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use yew::prelude::*;

use crate::components::{Layout, Dashboard};
use crate::state::StateProvider;
use crate::cache_manager::CacheManager;

#[function_component(App)]
pub fn app() -> Html {
    // Initialize logging and cache manager
    use_effect_with((), |_| {
        log::info!("ACGS-2 Rust Frontend initialized");
        log::info!("Constitutional Hash: {}", crate::CONSTITUTIONAL_HASH);

        // Initialize advanced caching
        wasm_bindgen_futures::spawn_local(async {
            let cache_manager = CacheManager::new();

            if let Err(e) = cache_manager.register_service_worker().await {
                log::error!("Failed to register service worker: {:?}", e);
            } else {
                log::info!("✅ Advanced service worker registered");

                // Monitor cache performance
                if let Err(e) = cache_manager.monitor_performance().await {
                    log::error!("Failed to monitor cache performance: {:?}", e);
                }
            }
        });
    });

    html! {
        <StateProvider>
            <div class="app" data-constitutional-hash={crate::CONSTITUTIONAL_HASH}>
                <Layout>
                    <Dashboard />
                </Layout>
            </div>
        </StateProvider>
    }
}



