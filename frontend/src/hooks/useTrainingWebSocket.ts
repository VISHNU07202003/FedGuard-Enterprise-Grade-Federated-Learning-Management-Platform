import { useState, useEffect, useCallback, useRef } from 'react';

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting' | 'error';

export interface WebSocketEvent {
  event: string;
  version: number;
  timestamp: string;
  run_id: string;
  round?: number;
  client_id?: string;
  payload: Record<string, any>;
}

export function useTrainingWebSocket(runId: string | null) {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [events, setEvents] = useState<WebSocketEvent[]>([]);
  const [latestEvent, setLatestEvent] = useState<WebSocketEvent | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  
  const connect = useCallback(() => {
    if (!runId) return;
    
    // Determine WS URL from API URL
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const wsUrl = apiUrl.replace(/^http/, 'ws') + `/ws/training/${runId}`;
    
    setStatus('connecting');
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    
    ws.onopen = () => {
      setStatus('connected');
      setError(null);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WebSocketEvent;
        if (data.event === 'error') {
           setError(data.payload.message || 'Unknown error');
        } else {
           setLatestEvent(data);
           setEvents(prev => [...prev.slice(-99), data]); // Keep last 100
        }
      } catch (e) {
        console.error('Failed to parse websocket message', e);
      }
    };
    
    ws.onclose = () => {
      setStatus('disconnected');
      // Reconnect logic
      reconnectTimeout.current = setTimeout(() => {
        setStatus('reconnecting');
        connect();
      }, 5000);
    };
    
    ws.onerror = () => {
      setStatus('error');
      // onClose will handle reconnect
    };
    
  }, [runId]);
  
  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);
  
  return { status, events, latestEvent, error };
}
