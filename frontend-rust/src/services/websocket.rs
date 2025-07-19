/*!
 * ACGS-2 WebSocket Client
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;
use web_sys::{WebSocket, MessageEvent, CloseEvent, ErrorEvent};
use yew::prelude::*;

use crate::{ACGSError, Result, CONSTITUTIONAL_HASH};

#[derive(Debug, Clone)]
pub struct WebSocketClient {
    pub url: String,
    pub socket: Option<WebSocket>,
    pub connected: bool,
    pub message_handlers: HashMap<String, Callback<serde_json::Value>>,
}

impl WebSocketClient {
    pub async fn new(url: &str) -> Result<Self> {
        let mut client = Self {
            url: url.to_string(),
            socket: None,
            connected: false,
            message_handlers: HashMap::new(),
        };
        
        client.connect().await?;
        Ok(client)
    }
    
    pub async fn connect(&mut self) -> Result<()> {
        let socket = WebSocket::new(&self.url)
            .map_err(|e| ACGSError::NetworkError(format!("Failed to create WebSocket: {:?}", e)))?;
        
        // Set up event handlers
        self.setup_event_handlers(&socket)?;
        
        self.socket = Some(socket);
        
        // Wait for connection to open
        // Note: In a real implementation, you'd want to use a proper async mechanism
        // For now, we'll assume the connection is established
        self.connected = true;
        
        log::info!("WebSocket connected to {}", self.url);
        Ok(())
    }
    
    fn setup_event_handlers(&self, socket: &WebSocket) -> Result<()> {
        // On open
        let onopen_callback = Closure::wrap(Box::new(move |_| {
            log::info!("WebSocket connection opened");
        }) as Box<dyn FnMut(JsValue)>);
        socket.set_onopen(Some(onopen_callback.as_ref().unchecked_ref()));
        onopen_callback.forget();
        
        // On message
        let onmessage_callback = Closure::wrap(Box::new(move |e: MessageEvent| {
            if let Ok(text) = e.data().dyn_into::<js_sys::JsString>() {
                let message_str = text.as_string().unwrap_or_default();
                
                // Parse message
                match serde_json::from_str::<WebSocketMessage>(&message_str) {
                    Ok(message) => {
                        // Validate constitutional compliance
                        if message.constitutional_hash != CONSTITUTIONAL_HASH {
                            log::warn!("WebSocket message constitutional hash mismatch");
                            return;
                        }
                        
                        log::debug!("WebSocket message received: {}", message.message_type);
                        
                        // Handle message based on type
                        // Note: In a real implementation, you'd dispatch to registered handlers
                    }
                    Err(e) => {
                        log::error!("Failed to parse WebSocket message: {:?}", e);
                    }
                }
            }
        }) as Box<dyn FnMut(MessageEvent)>);
        socket.set_onmessage(Some(onmessage_callback.as_ref().unchecked_ref()));
        onmessage_callback.forget();
        
        // On error
        let onerror_callback = Closure::wrap(Box::new(move |e: ErrorEvent| {
            log::error!("WebSocket error: {:?}", e);
        }) as Box<dyn FnMut(ErrorEvent)>);
        socket.set_onerror(Some(onerror_callback.as_ref().unchecked_ref()));
        onerror_callback.forget();
        
        // On close
        let onclose_callback = Closure::wrap(Box::new(move |e: CloseEvent| {
            log::info!("WebSocket connection closed: code={}, reason={}", e.code(), e.reason());
        }) as Box<dyn FnMut(CloseEvent)>);
        socket.set_onclose(Some(onclose_callback.as_ref().unchecked_ref()));
        onclose_callback.forget();
        
        Ok(())
    }
    
    pub fn send_message(&self, message: &WebSocketMessage) -> Result<()> {
        if let Some(ref socket) = self.socket {
            if self.connected {
                let message_str = serde_json::to_string(message)
                    .map_err(|e| ACGSError::NetworkError(format!("Failed to serialize message: {:?}", e)))?;
                
                socket.send_with_str(&message_str)
                    .map_err(|e| ACGSError::NetworkError(format!("Failed to send message: {:?}", e)))?;
                
                log::debug!("WebSocket message sent: {}", message.message_type);
                Ok(())
            } else {
                Err(ACGSError::NetworkError("WebSocket not connected".to_string()))
            }
        } else {
            Err(ACGSError::NetworkError("WebSocket not initialized".to_string()))
        }
    }
    
    pub fn register_handler(&mut self, message_type: String, handler: Callback<serde_json::Value>) {
        self.message_handlers.insert(message_type, handler);
    }
    
    pub fn disconnect(&mut self) {
        if let Some(ref socket) = self.socket {
            let _ = socket.close();
            self.connected = false;
            self.socket = None;
            log::info!("WebSocket disconnected");
        }
    }
    
    pub fn is_connected(&self) -> bool {
        self.connected
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WebSocketMessage {
    pub message_type: String,
    pub data: serde_json::Value,
    pub timestamp: String,
    pub constitutional_hash: String,
    pub request_id: Option<String>,
}

impl WebSocketMessage {
    pub fn new(message_type: String, data: serde_json::Value) -> Self {
        Self {
            message_type,
            data,
            timestamp: chrono::Utc::now().to_rfc3339(),
            constitutional_hash: CONSTITUTIONAL_HASH.to_string(),
            request_id: Some(uuid::Uuid::new_v4().to_string()),
        }
    }
    
    pub fn is_constitutionally_valid(&self) -> bool {
        self.constitutional_hash == CONSTITUTIONAL_HASH
    }
}

// WebSocket hook for Yew components
#[hook]
pub fn use_websocket(url: String) -> (Option<WebSocketClient>, bool, Option<String>) {
    let client = use_state(|| None);
    let connected = use_state(|| false);
    let error = use_state(|| None);
    
    use_effect_with(url.clone(), {
        let client = client.clone();
        let connected = connected.clone();
        let error = error.clone();
        
        move |url| {
            wasm_bindgen_futures::spawn_local(async move {
                match WebSocketClient::new(url).await {
                    Ok(ws_client) => {
                        connected.set(ws_client.is_connected());
                        client.set(Some(ws_client));
                        error.set(None);
                    }
                    Err(e) => {
                        error.set(Some(format!("WebSocket connection failed: {}", e)));
                        connected.set(false);
                        client.set(None);
                    }
                }
            });
        }
    });
    
    ((*client).clone(), *connected, (*error).clone())
}

// WebSocket message sender hook
#[hook]
pub fn use_websocket_sender(client: Option<WebSocketClient>) -> Callback<WebSocketMessage> {
    Callback::from(move |message: WebSocketMessage| {
        if let Some(ref ws_client) = client {
            if let Err(e) = ws_client.send_message(&message) {
                log::error!("Failed to send WebSocket message: {:?}", e);
            }
        } else {
            log::warn!("WebSocket client not available");
        }
    })
}
