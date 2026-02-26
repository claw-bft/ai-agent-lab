import { useState, useEffect, useCallback, useRef } from 'react';

// KV API configuration
const KV_REST_API_URL = (import.meta as any).env?.VITE_KV_REST_API_URL || '';
const KV_REST_API_TOKEN = (import.meta as any).env?.VITE_KV_REST_API_TOKEN || '';

interface KVConfig {
  url: string;
  token: string;
}

export function getKVConfig(): KVConfig | null {
  if (!KV_REST_API_URL || !KV_REST_API_TOKEN) {
    return null;
  }
  return { url: KV_REST_API_URL, token: KV_REST_API_TOKEN };
}

export function isKVConfigured(): boolean {
  return !!KV_REST_API_URL && !!KV_REST_API_TOKEN;
}

// Types
export interface Session {
  id: string;
  label: string;
  channel: string;
  status: 'active' | 'idle' | 'offline';
  lastActivity: string;
  metadata?: Record<string, any>;
}

export interface SystemStats {
  uptime: number;
  memory: {
    rss: number;
    heapTotal: number;
    heapUsed: number;
    external: number;
  };
  version: string;
  workspace: string;
  tasksCount: number;
  skillsCount: number;
  connectedClients: number;
  timestamp: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in-progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  createdAt: string;
  updatedAt: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

// KV Data interface
export interface KVData {
  sessions: Session[];
  stats: SystemStats | null;
  tasks: Task[];
  messages: Message[];
  lastUpdate: number;
}

// Fetch from KV
async function fetchFromKV<T>(key: string, config: KVConfig): Promise<T | null> {
  try {
    const response = await fetch(`${config.url}/get/${key}`, {
      headers: {
        'Authorization': `Bearer ${config.token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`KV API error: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.error) {
      return null;
    }

    // Vercel KV returns the value directly or wrapped
    const value = result.result || result;
    
    if (typeof value === 'string') {
      try {
        return JSON.parse(value) as T;
      } catch {
        return value as unknown as T;
      }
    }
    
    return value as T;
  } catch (error) {
    console.error(`Failed to fetch ${key} from KV:`, error);
    return null;
  }
}

// Hook for polling KV data
export function useKVPolling(intervalMs: number = 3000) {
  const [data, setData] = useState<KVData>({
    sessions: [],
    stats: null,
    tasks: [],
    messages: [],
    lastUpdate: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastFetchTime, setLastFetchTime] = useState<number>(0);
  
  const config = getKVConfig();
  const isConfigured = isKVConfigured();

  const fetchData = useCallback(async () => {
    if (!config) {
      setError('Vercel KV not configured');
      setIsLoading(false);
      return;
    }

    try {
      const [sessions, stats, tasks, messages, lastUpdate] = await Promise.all([
        fetchFromKV<string>('sessions:list', config),
        fetchFromKV<string>('stats', config),
        fetchFromKV<string>('tasks', config),
        fetchFromKV<string>('messages', config),
        fetchFromKV<string>('lastUpdate', config),
      ]);

      setData({
        sessions: sessions ? JSON.parse(sessions) : [],
        stats: stats ? JSON.parse(stats) : null,
        tasks: tasks ? JSON.parse(tasks) : [],
        messages: messages ? JSON.parse(messages) : [],
        lastUpdate: lastUpdate ? parseInt(lastUpdate, 10) : 0,
      });
      
      setLastFetchTime(Date.now());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setIsLoading(false);
    }
  }, [config]);

  useEffect(() => {
    if (!isConfigured) {
      setIsLoading(false);
      return;
    }

    // Initial fetch
    fetchData();

    // Set up polling
    const interval = setInterval(fetchData, intervalMs);

    return () => clearInterval(interval);
  }, [fetchData, intervalMs, isConfigured]);

  const refresh = useCallback(() => {
    setIsLoading(true);
    fetchData();
  }, [fetchData]);

  return {
    data,
    isLoading,
    error,
    isConfigured,
    lastFetchTime,
    refresh,
  };
}

// Hook for real-time WebSocket connection (fallback when KV is not available)
export function useWebSocket(url?: string) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    // Skip WebSocket if KV is configured (we use polling instead)
    if (isKVConfigured()) {
      return;
    }

    const wsUrl = url || `ws://${window.location.host}/ws`;
    
    const connect = () => {
      const socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        reconnectAttempts.current = 0;
      };

      socket.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Attempt reconnection
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          setTimeout(connect, 3000 * reconnectAttempts.current);
        }
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      setWs(socket);
    };

    connect();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [url]);

  const sendMessage = useCallback((data: any) => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }, [ws]);

  return { ws, isConnected, lastMessage, sendMessage };
}

// Combined hook that uses KV polling when available, falls back to WebSocket
export function useDashboardData(pollIntervalMs: number = 3000) {
  const kvData = useKVPolling(pollIntervalMs);
  const wsData = useWebSocket();
  
  // Use KV data if configured, otherwise fall back to WebSocket
  const isUsingKV = kvData.isConfigured;
  
  return {
    // Data
    sessions: kvData.data.sessions,
    stats: kvData.data.stats,
    tasks: kvData.data.tasks,
    messages: kvData.data.messages,
    lastUpdate: kvData.data.lastUpdate,
    
    // Status
    isLoading: kvData.isLoading,
    error: kvData.error,
    isUsingKV,
    
    // Connection status
    isConnected: isUsingKV ? !kvData.error : wsData.isConnected,
    lastMessage: wsData.lastMessage,
    lastFetchTime: kvData.lastFetchTime,
    
    // Actions
    refresh: kvData.refresh,
    sendMessage: wsData.sendMessage,
  };
}
