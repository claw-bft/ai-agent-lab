import { createClient } from '@vercel/kv';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';

// KV Client
let kv: ReturnType<typeof createClient> | null = null;

export function initKV() {
  if (!process.env.KV_REST_API_URL || !process.env.KV_REST_API_TOKEN) {
    console.warn('⚠️ Vercel KV not configured. Set KV_REST_API_URL and KV_REST_API_TOKEN env vars.');
    return false;
  }

  try {
    kv = createClient({
      url: process.env.KV_REST_API_URL,
      token: process.env.KV_REST_API_TOKEN,
    });
    console.log('✅ Vercel KV connected');
    return true;
  } catch (error) {
    console.error('❌ Failed to connect to Vercel KV:', error);
    return false;
  }
}

export function isKVConnected(): boolean {
  return kv !== null;
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

// KV Operations
const KEYS = {
  SESSIONS_LIST: 'sessions:list',
  SESSION_PREFIX: 'sessions:',
  STATS: 'stats',
  LAST_UPDATE: 'lastUpdate',
  MESSAGES: 'messages',
  TASKS: 'tasks',
};

export async function updateSessionsList(sessions: Session[]): Promise<void> {
  if (!kv) return;
  await kv.set(KEYS.SESSIONS_LIST, JSON.stringify(sessions));
  await kv.set(KEYS.LAST_UPDATE, Date.now().toString());
}

export async function updateSession(session: Session): Promise<void> {
  if (!kv) return;
  await kv.set(`${KEYS.SESSION_PREFIX}${session.id}`, JSON.stringify(session));
}

export async function removeSession(sessionId: string): Promise<void> {
  if (!kv) return;
  await kv.del(`${KEYS.SESSION_PREFIX}${sessionId}`);
}

export async function updateStats(stats: SystemStats): Promise<void> {
  if (!kv) return;
  await kv.set(KEYS.STATS, JSON.stringify(stats));
  await kv.set(KEYS.LAST_UPDATE, Date.now().toString());
}

export async function getSessionsList(): Promise<Session[]> {
  if (!kv) return [];
  const data = await kv.get<string>(KEYS.SESSIONS_LIST);
  return data ? JSON.parse(data) : [];
}

export async function getSession(sessionId: string): Promise<Session | null> {
  if (!kv) return null;
  const data = await kv.get<string>(`${KEYS.SESSION_PREFIX}${sessionId}`);
  return data ? JSON.parse(data) : null;
}

export async function getStats(): Promise<SystemStats | null> {
  if (!kv) return null;
  const data = await kv.get<string>(KEYS.STATS);
  return data ? JSON.parse(data) : null;
}

export async function getLastUpdate(): Promise<number> {
  if (!kv) return 0;
  const data = await kv.get<string>(KEYS.LAST_UPDATE);
  return data ? parseInt(data, 10) : 0;
}

// Tasks sync to KV
export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in-progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  createdAt: string;
  updatedAt: string;
}

export async function updateTasks(tasks: Task[]): Promise<void> {
  if (!kv) return;
  await kv.set(KEYS.TASKS, JSON.stringify(tasks));
  await kv.set(KEYS.LAST_UPDATE, Date.now().toString());
}

export async function getTasks(): Promise<Task[]> {
  if (!kv) return [];
  const data = await kv.get<string>(KEYS.TASKS);
  return data ? JSON.parse(data) : [];
}

// Messages sync to KV
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export async function addMessage(message: Message): Promise<void> {
  if (!kv) return;
  const messages = await getMessages();
  messages.push(message);
  // Keep only last 100 messages
  if (messages.length > 100) {
    messages.splice(0, messages.length - 100);
  }
  await kv.set(KEYS.MESSAGES, JSON.stringify(messages));
  await kv.set(KEYS.LAST_UPDATE, Date.now().toString());
}

export async function getMessages(): Promise<Message[]> {
  if (!kv) return [];
  const data = await kv.get<string>(KEYS.MESSAGES);
  return data ? JSON.parse(data) : [];
}

// Local session tracking for this backend instance
const localSessions = new Map<string, Session>();

export function registerLocalSession(sessionId: string, label: string, channel: string): Session {
  const session: Session = {
    id: sessionId,
    label,
    channel,
    status: 'active',
    lastActivity: new Date().toISOString(),
  };
  localSessions.set(sessionId, session);
  return session;
}

export function updateLocalSessionActivity(sessionId: string): void {
  const session = localSessions.get(sessionId);
  if (session) {
    session.lastActivity = new Date().toISOString();
    session.status = 'active';
  }
}

export function setLocalSessionOffline(sessionId: string): void {
  const session = localSessions.get(sessionId);
  if (session) {
    session.status = 'offline';
  }
}

export function getLocalSessions(): Session[] {
  return Array.from(localSessions.values());
}

export function removeLocalSession(sessionId: string): void {
  localSessions.delete(sessionId);
}

// Sync loop - call this periodically to sync local state to KV
export async function syncToKV(stats: SystemStats): Promise<void> {
  if (!kv) return;
  
  try {
    // Update sessions
    const sessions = getLocalSessions();
    await updateSessionsList(sessions);
    
    // Update stats
    await updateStats(stats);
    
    console.log(`📤 Synced to KV: ${sessions.length} sessions, stats updated`);
  } catch (error) {
    console.error('❌ Failed to sync to KV:', error);
  }
}
