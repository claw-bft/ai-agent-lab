import axios from 'axios';
import type { Agent, Task, Session, SystemHealth, CronJob } from '../types';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const agentService = {
  getAll: () => api.get<Agent[]>('/agents').then(res => res.data),
  getById: (id: string) => api.get<Agent>(`/agents/${id}`).then(res => res.data),
  getStats: () => api.get<{ agents: Agent[], totalCompleted: number, totalFailed: number }>('/agents/stats').then(res => res.data),
};

export const taskService = {
  getAll: (params?: { status?: string; agentId?: string; search?: string }) =>
    api.get<Task[]>('/tasks', { params }).then(res => res.data),
  getById: (id: string) => api.get<Task>(`/tasks/${id}`).then(res => res.data),
  getRunning: () => api.get<Task[]>('/tasks/running').then(res => res.data),
  getRecent: (limit?: number) => api.get<Task[]>('/tasks/recent', { params: { limit } }).then(res => res.data),
};

export const sessionService = {
  getAll: () => api.get<Session[]>('/sessions').then(res => res.data),
  getActive: () => api.get<Session[]>('/sessions/active').then(res => res.data),
  getHistory: () => api.get<Session[]>('/sessions/history').then(res => res.data),
};

export const healthService = {
  getStatus: () => api.get<SystemHealth>('/health').then(res => res.data),
};

export const cronService = {
  getAll: () => api.get<CronJob[]>('/cron').then(res => res.data),
};

// WebSocket connection for real-time updates
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectInterval = 5000;
  private listeners: Map<string, ((data: any) => void)[]> = new Map();

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.emit('connected', {});
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.emit(data.type, data.payload);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected, reconnecting...');
      setTimeout(() => this.connect(), this.reconnectInterval);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)?.push(callback);
  }

  off(event: string, callback: (data: any) => void) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(cb => cb(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const wsService = new WebSocketService();