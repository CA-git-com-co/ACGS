// Constitutional Hash: cdd01ef066bc6cf2

import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { CONFIG } from '@/config';

interface WebSocketMessage {
  type: string;
  data: any;
  constitutionalHash?: string;
  timestamp?: string;
  requestId?: string;
}

interface WebSocketHook {
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  subscribe: (event: string, callback: (data: any) => void) => () => void;
  unsubscribe: (event: string, callback?: (data: any) => void) => void;
  send: (type: string, data: any) => void;
  lastMessage: WebSocketMessage | null;
  reconnect: () => void;
  disconnect: () => void;
  getMetrics: () => WebSocketMetrics;
}

interface WebSocketMetrics {
  totalMessages: number;
  messagesPerSecond: number;
  averageLatency: number;
  reconnectCount: number;
  uptime: number;
  lastReconnect: string | null;
}

interface PendingMessage {
  id: string;
  timestamp: number;
  message: WebSocketMessage;
}

// Hook with performance optimizations and better error handling
export function useOptimizedWebSocket(url?: string): WebSocketHook {
  const wsUrl = url || CONFIG.api.wsUrl;
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  
  // Performance tracking
  const metricsRef = useRef({
    totalMessages: 0,
    messagesPerSecond: 0,
    averageLatency: 0,
    reconnectCount: 0,
    connectionStartTime: Date.now(),
    lastReconnect: null as string | null,
    latencySum: 0,
    latencyCount: 0,
    messageTimestamps: [] as number[],
  });

  // Use Map for better performance with many subscribers
  const subscribersRef = useRef<Map<string, Set<(data: any) => void>>>(new Map());
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const metricsIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pendingMessagesRef = useRef<Map<string, PendingMessage>>(new Map());

  // Optimized message queue for offline scenarios
  const messageQueueRef = useRef<WebSocketMessage[]>([]);
  const maxQueueSize = 100;

  // Connection configuration
  const maxReconnectAttempts = CONFIG.polling.reconnectAttempts;
  const baseReconnectDelay = 1000;
  const maxReconnectDelay = 30000;
  const pingInterval = 30000; // 30 seconds

  // Memoized helper functions
  const getReconnectDelay = useCallback((attempt: number) => {
    return Math.min(baseReconnectDelay * Math.pow(2, attempt), maxReconnectDelay) + Math.random() * 1000;
  }, []);

  const updateMetrics = useCallback(() => {
    const now = Date.now();
    const metrics = metricsRef.current;
    
    // Calculate messages per second
    metrics.messageTimestamps = metrics.messageTimestamps.filter(timestamp => now - timestamp < 1000);
    metrics.messagesPerSecond = metrics.messageTimestamps.length;
    
    // Calculate average latency
    if (metrics.latencyCount > 0) {
      metrics.averageLatency = metrics.latencySum / metrics.latencyCount;
    }
  }, []);

  // Start metrics tracking
  useEffect(() => {
    if (CONFIG.features.enablePerformanceMonitoring) {
      metricsIntervalRef.current = setInterval(updateMetrics, 1000);
    }
    
    return () => {
      if (metricsIntervalRef.current) {
        clearInterval(metricsIntervalRef.current);
      }
    };
  }, [updateMetrics]);

  const validateMessage = useCallback((message: WebSocketMessage): boolean => {
    if (!CONFIG.constitutional.validationEnabled) {
      return true;
    }
    
    if (message.constitutionalHash !== CONFIG.constitutional.hash) {
      console.warn('Constitutional compliance violation in WebSocket message:', message);
      return false;
    }
    
    return true;
  }, []);

  const processMessage = useCallback((message: WebSocketMessage) => {
    if (!validateMessage(message)) {
      return;
    }

    // Update metrics
    const metrics = metricsRef.current;
    metrics.totalMessages++;
    metrics.messageTimestamps.push(Date.now());

    // Calculate latency if timestamp is available
    if (message.timestamp) {
      const latency = Date.now() - new Date(message.timestamp).getTime();
      metrics.latencySum += latency;
      metrics.latencyCount++;
    }

    // Remove from pending messages if this is a response
    if (message.requestId) {
      pendingMessagesRef.current.delete(message.requestId);
    }

    // Notify subscribers
    const eventSubscribers = subscribersRef.current.get(message.type);
    if (eventSubscribers) {
      // Use requestIdleCallback for non-critical updates to improve performance
      if (typeof window !== 'undefined' && window.requestIdleCallback) {
        window.requestIdleCallback(() => {
          eventSubscribers.forEach(callback => {
            try {
              callback(message.data);
            } catch (error) {
              console.error('Error in WebSocket subscriber:', error);
            }
          });
        });
      } else {
        eventSubscribers.forEach(callback => {
          try {
            callback(message.data);
          } catch (error) {
            console.error('Error in WebSocket subscriber:', error);
          }
        });
      }
    }

    setLastMessage(message);
  }, [validateMessage]);

  const sendPing = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      const pingMessage: WebSocketMessage = {
        type: 'ping',
        data: { timestamp: Date.now() },
        constitutionalHash: CONFIG.constitutional.hash,
      };
      ws.current.send(JSON.stringify(pingMessage));
    }
  }, []);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN || ws.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    setConnectionStatus('connecting');
    
    try {
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectAttemptsRef.current = 0;
        metricsRef.current.connectionStartTime = Date.now();
        
        // Send constitutional compliance verification
        const authMessage: WebSocketMessage = {
          type: 'constitutional-verification',
          data: { constitutionalHash: CONFIG.constitutional.hash },
          constitutionalHash: CONFIG.constitutional.hash,
          timestamp: new Date().toISOString(),
        };
        ws.current?.send(JSON.stringify(authMessage));

        // Send queued messages
        messageQueueRef.current.forEach(message => {
          ws.current?.send(JSON.stringify(message));
        });
        messageQueueRef.current = [];

        // Start ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        pingIntervalRef.current = setInterval(sendPing, pingInterval);
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          // Handle pong messages for latency calculation
          if (message.type === 'pong' && message.data?.timestamp) {
            const latency = Date.now() - message.data.timestamp;
            metricsRef.current.latencySum += latency;
            metricsRef.current.latencyCount++;
            return;
          }
          
          processMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onclose = (event) => {
        setIsConnected(false);
        setConnectionStatus('disconnected');
        
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Only attempt reconnection if it wasn't a clean close
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          metricsRef.current.reconnectCount++;
          metricsRef.current.lastReconnect = new Date().toISOString();
          
          const delay = getReconnectDelay(reconnectAttemptsRef.current);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setConnectionStatus('error');
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionStatus('error');
    }
  }, [wsUrl, processMessage, sendPing, getReconnectDelay]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (ws.current) {
      ws.current.close(1000, 'User initiated disconnect');
      ws.current = null;
    }

    setIsConnected(false);
    setConnectionStatus('disconnected');
    reconnectAttemptsRef.current = maxReconnectAttempts; // Prevent auto-reconnect
  }, []);

  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    disconnect();
    setTimeout(connect, 100);
  }, [connect, disconnect]);

  const subscribe = useCallback((event: string, callback: (data: any) => void) => {
    if (!subscribersRef.current.has(event)) {
      subscribersRef.current.set(event, new Set());
    }
    subscribersRef.current.get(event)!.add(callback);

    // Return unsubscribe function
    return () => {
      const eventSubscribers = subscribersRef.current.get(event);
      if (eventSubscribers) {
        eventSubscribers.delete(callback);
        if (eventSubscribers.size === 0) {
          subscribersRef.current.delete(event);
        }
      }
    };
  }, []);

  const unsubscribe = useCallback((event: string, callback?: (data: any) => void) => {
    if (callback) {
      subscribersRef.current.get(event)?.delete(callback);
    } else {
      subscribersRef.current.delete(event);
    }
  }, []);

  const send = useCallback((type: string, data: any) => {
    const message: WebSocketMessage = {
      type,
      data,
      constitutionalHash: CONFIG.constitutional.hash,
      timestamp: new Date().toISOString(),
      requestId: `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };

    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
      
      // Track pending message for latency calculation
      pendingMessagesRef.current.set(message.requestId!, {
        id: message.requestId!,
        timestamp: Date.now(),
        message,
      });
    } else {
      // Queue message for when connection is restored
      if (messageQueueRef.current.length < maxQueueSize) {
        messageQueueRef.current.push(message);
      } else {
        console.warn('WebSocket message queue is full, dropping message');
      }
    }
  }, []);

  const getMetrics = useCallback((): WebSocketMetrics => {
    const metrics = metricsRef.current;
    const uptime = Date.now() - metrics.connectionStartTime;
    
    return {
      totalMessages: metrics.totalMessages,
      messagesPerSecond: metrics.messagesPerSecond,
      averageLatency: metrics.averageLatency,
      reconnectCount: metrics.reconnectCount,
      uptime,
      lastReconnect: metrics.lastReconnect,
    };
  }, []);

  // Initial connection
  useEffect(() => {
    if (CONFIG.features.enableWebsocketUpdates) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
      if (metricsIntervalRef.current) {
        clearInterval(metricsIntervalRef.current);
      }
    };
  }, []);

  return {
    isConnected,
    connectionStatus,
    subscribe,
    unsubscribe,
    send,
    lastMessage,
    reconnect,
    disconnect,
    getMetrics,
  };
}