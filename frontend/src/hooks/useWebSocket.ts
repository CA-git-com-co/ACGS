// Constitutional Hash: cdd01ef066bc6cf2

import { useEffect, useRef, useState, useCallback } from 'react';
import { CONFIG } from '@/config';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  constitutionalCompliance?: {
    hash: string;
    timestamp: string;
  };
}

export interface WebSocketHook {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  sendMessage: (type: string, data: any) => void;
  send: (type: string, data: any) => void;
  subscribe: (type: string, callback: (data: any) => void) => () => void;
  disconnect: () => void;
  reconnect: () => void;
}

export function useWebSocket(url?: string): WebSocketHook {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 1000;
  const listenersRef = useRef<Map<string, ((data: any) => void)[]>>(new Map());

  const wsUrl = url || CONFIG.api.wsUrl;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        reconnectAttempts.current = 0;
        
        // Send constitutional hash for validation
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            type: 'auth',
            data: { constitutionalHash: CONFIG.constitutional.hash },
            constitutionalCompliance: {
              hash: CONFIG.constitutional.hash,
              timestamp: new Date().toISOString(),
            },
          }));
        }
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          // Validate constitutional hash if present
          if (message.constitutionalCompliance?.hash && 
              message.constitutionalCompliance.hash !== CONFIG.constitutional.hash) {
            console.error('Constitutional hash mismatch in WebSocket message');
            return;
          }

          setLastMessage(message);
          
          // Call subscribers for this message type
          const listeners = listenersRef.current.get(message.type) || [];
          listeners.forEach(listener => listener(message.data));
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);
        handleReconnect();
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setIsConnected(false);
    }
  }, [wsUrl]);

  const handleReconnect = useCallback(() => {
    if (reconnectAttempts.current < maxReconnectAttempts) {
      reconnectAttempts.current++;
      const delay = reconnectDelay * Math.pow(2, reconnectAttempts.current - 1);
      
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, delay);
    }
  }, [connect]);

  const sendMessage = useCallback((type: string, data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message = {
        type,
        data,
        timestamp: new Date().toISOString(),
        constitutionalCompliance: {
          hash: CONFIG.constitutional.hash,
          timestamp: new Date().toISOString(),
        },
      };
      
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setLastMessage(null);
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttempts.current = 0;
    connect();
  }, [disconnect, connect]);

  const subscribe = useCallback((type: string, callback: (data: any) => void) => {
    const listeners = listenersRef.current.get(type) || [];
    listeners.push(callback);
    listenersRef.current.set(type, listeners);

    // Return unsubscribe function
    return () => {
      const currentListeners = listenersRef.current.get(type) || [];
      const index = currentListeners.indexOf(callback);
      if (index > -1) {
        currentListeners.splice(index, 1);
        listenersRef.current.set(type, currentListeners);
      }
    };
  }, []);

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    send: sendMessage, // Alias for sendMessage
    subscribe,
    disconnect,
    reconnect,
  };
}