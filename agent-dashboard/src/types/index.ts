export interface Agent {
  id: string;
  name: string;
  status: 'active' | 'idle' | 'busy' | 'error';
  currentTask?: string;
  completedTasks: number;
  failedTasks: number;
  totalTokens: number;
  avgResponseTime: number;
  lastActive: string;
}

export interface Task {
  id: string;
  agentId: string;
  agentName: string;
  status: 'running' | 'completed' | 'failed' | 'pending';
  type: string;
  input: string;
  output?: string;
  startTime: string;
  endTime?: string;
  duration?: number;
  tokensUsed: number;
  error?: string;
}

export interface Session {
  id: string;
  agentId: string;
  agentName: string;
  status: 'active' | 'completed' | 'error';
  startTime: string;
  lastActivity: string;
  taskCount: number;
}

export interface SystemHealth {
  status: 'healthy' | 'warning' | 'critical';
  activeSessions: number;
  totalAgents: number;
  runningTasks: number;
  queuedTasks: number;
  cpuUsage: number;
  memoryUsage: number;
  uptime: number;
}

export interface CronJob {
  id: string;
  name: string;
  schedule: string;
  command: string;
  enabled: boolean;
  lastRun?: string;
  nextRun?: string;
  lastStatus?: 'success' | 'failed';
}