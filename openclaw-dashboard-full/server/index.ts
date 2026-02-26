import express from 'express';
import cors from 'cors';
import { WebSocketServer, WebSocket } from 'ws';
import { createServer } from 'http';
import { v4 as uuidv4 } from 'uuid';
import * as fs from 'fs';
import * as path from 'path';
import chokidar from 'chokidar';
import {
  initKV,
  isKVConnected,
  syncToKV,
  registerLocalSession,
  updateLocalSessionActivity,
  setLocalSessionOffline,
  removeLocalSession,
  addMessage,
  updateTasks,
  Session,
  Task,
  Message,
} from './kv-store';

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

const PORT = process.env.PORT || 3001;
const WORKSPACE_DIR = process.env.WORKSPACE_DIR || '/root/.openclaw/workspace';
const TASKS_FILE = path.join(WORKSPACE_DIR, 'TASKS.md');
const MEMORY_FILE = path.join(WORKSPACE_DIR, 'MEMORY.md');
const SKILLS_DIR = path.join(WORKSPACE_DIR, 'skills');
const SYNC_INTERVAL = parseInt(process.env.SYNC_INTERVAL || '1000', 10); // Default 1 second

// Middleware
app.use(cors());
app.use(express.json());

// Types
interface Skill {
  name: string;
  description: string;
  version: string;
  installed: boolean;
}

// In-memory storage
let tasks: Task[] = [];
let messages: Message[] = [];
let connectedClients: WebSocket[] = [];
let serverStartTime = Date.now();

// Initialize KV
const kvEnabled = initKV();

// Ensure files exist
function ensureFileExists(filePath: string, defaultContent: string = '') {
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, defaultContent, 'utf-8');
  }
}

// Parse tasks from TASKS.md
function parseTasksFromMarkdown(content: string): Task[] {
  const tasks: Task[] = [];
  const lines = content.split('\n');
  let currentTask: Partial<Task> | null = null;

  for (const line of lines) {
    const taskMatch = line.match(/^- \[([ x])\] (.+)$/);
    if (taskMatch) {
      if (currentTask) {
        tasks.push(currentTask as Task);
      }
      currentTask = {
        id: uuidv4(),
        title: taskMatch[2],
        status: taskMatch[1] === 'x' ? 'done' : 'todo',
        description: '',
        priority: 'medium',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    } else if (currentTask && line.trim().startsWith('-')) {
      currentTask.description += line.trim().substring(1).trim() + ' ';
    }
  }

  if (currentTask) {
    tasks.push(currentTask as Task);
  }

  return tasks;
}

// Save tasks to TASKS.md
function saveTasksToMarkdown(tasks: Task[]): void {
  const lines = ['# Tasks\n'];
  for (const task of tasks) {
    const checkbox = task.status === 'done' ? '[x]' : '[ ]';
    lines.push(`- ${checkbox} ${task.title}`);
    if (task.description) {
      lines.push(`  - ${task.description}`);
    }
  }
  fs.writeFileSync(TASKS_FILE, lines.join('\n'), 'utf-8');
}

// Load tasks
function loadTasks() {
  ensureFileExists(TASKS_FILE, '# Tasks\n');
  const content = fs.readFileSync(TASKS_FILE, 'utf-8');
  tasks = parseTasksFromMarkdown(content);
}

// Scan skills directory
function scanSkills(): Skill[] {
  if (!fs.existsSync(SKILLS_DIR)) {
    return [];
  }

  const skills: Skill[] = [];
  const entries = fs.readdirSync(SKILLS_DIR, { withFileTypes: true });

  for (const entry of entries) {
    if (entry.isDirectory()) {
      const skillPath = path.join(SKILLS_DIR, entry.name);
      const skillFile = path.join(skillPath, 'SKILL.md');
      const packageFile = path.join(skillPath, 'package.json');

      let description = 'No description available';
      let version = '1.0.0';

      if (fs.existsSync(skillFile)) {
        const content = fs.readFileSync(skillFile, 'utf-8');
        const descMatch = content.match(/# (.+)\n\n(.+)/);
        if (descMatch) {
          description = descMatch[2].split('\n')[0];
        }
      }

      if (fs.existsSync(packageFile)) {
        try {
          const pkg = JSON.parse(fs.readFileSync(packageFile, 'utf-8'));
          version = pkg.version || version;
          description = pkg.description || description;
        } catch (e) {
          // Ignore parse errors
        }
      }

      skills.push({
        name: entry.name,
        description,
        version,
        installed: true,
      });
    }
  }

  return skills;
}

// Get current stats
function getStats() {
  return {
    uptime: Math.floor((Date.now() - serverStartTime) / 1000),
    memory: process.memoryUsage(),
    version: '1.0.0',
    workspace: WORKSPACE_DIR,
    tasksCount: tasks.length,
    skillsCount: scanSkills().length,
    connectedClients: connectedClients.length,
    timestamp: new Date().toISOString(),
  };
}

// WebSocket handling
wss.on('connection', (ws: WebSocket, req) => {
  const sessionId = uuidv4();
  const clientIp = req.socket.remoteAddress || 'unknown';
  
  console.log(`WebSocket client connected: ${sessionId} from ${clientIp}`);
  connectedClients.push(ws);
  
  // Register this session
  registerLocalSession(sessionId, `Client-${sessionId.slice(0, 8)}`, 'websocket');

  ws.send(JSON.stringify({
    type: 'connected',
    data: { 
      message: 'Connected to OpenClaw Dashboard',
      sessionId,
      kvEnabled,
    }
  }));

  ws.on('message', (message: string) => {
    try {
      const data = JSON.parse(message.toString());
      handleWebSocketMessage(ws, data, sessionId);
    } catch (e) {
      ws.send(JSON.stringify({
        type: 'error',
        data: { message: 'Invalid JSON' }
      }));
    }
  });

  ws.on('close', () => {
    console.log(`WebSocket client disconnected: ${sessionId}`);
    connectedClients = connectedClients.filter(client => client !== ws);
    setLocalSessionOffline(sessionId);
  });

  ws.on('error', (error) => {
    console.error(`WebSocket error for ${sessionId}:`, error);
    removeLocalSession(sessionId);
  });
});

function handleWebSocketMessage(ws: WebSocket, data: any, sessionId: string) {
  updateLocalSessionActivity(sessionId);
  
  switch (data.type) {
    case 'ping':
      ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
      break;
    case 'subscribe':
      ws.send(JSON.stringify({
        type: 'subscribed',
        data: { channels: data.channels || [] }
      }));
      break;
    case 'message':
      // Handle chat messages
      if (data.content) {
        const message: Message = {
          id: uuidv4(),
          role: data.role || 'user',
          content: data.content,
          timestamp: new Date().toISOString(),
        };
        messages.push(message);
        if (messages.length > 100) {
          messages = messages.slice(-100);
        }
        addMessage(message);
        broadcastToAll({
          type: 'message',
          data: message
        });
      }
      break;
    default:
      broadcastToAll({
        type: 'broadcast',
        data: { ...data, fromSession: sessionId }
      });
  }
}

function broadcastToAll(message: any) {
  const messageStr = JSON.stringify(message);
  connectedClients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(messageStr);
    }
  });
}

// File watcher
const watcher = chokidar.watch([
  TASKS_FILE,
  MEMORY_FILE,
  SKILLS_DIR
], {
  ignored: /node_modules/,
  persistent: true
});

watcher.on('change', (filePath) => {
  console.log(`File changed: ${filePath}`);
  if (filePath === TASKS_FILE) {
    loadTasks();
    updateTasks(tasks);
    broadcastToAll({
      type: 'tasks_updated',
      data: tasks
    });
  }
});

// API Routes

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    kv: isKVConnected() ? 'connected' : 'disconnected',
  });
});

// Get system status
app.get('/api/status', (req, res) => {
  const status = getStats();
  res.json(status);
});

// Tasks API
app.get('/api/tasks', (req, res) => {
  loadTasks();
  res.json(tasks);
});

app.post('/api/tasks', (req, res) => {
  const { title, description, priority = 'medium' } = req.body;
  
  if (!title) {
    return res.status(400).json({ error: 'Title is required' });
  }

  const newTask: Task = {
    id: uuidv4(),
    title,
    description: description || '',
    status: 'todo',
    priority,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  tasks.push(newTask);
  saveTasksToMarkdown(tasks);
  updateTasks(tasks);

  broadcastToAll({
    type: 'task_created',
    data: newTask
  });

  res.status(201).json(newTask);
});

app.put('/api/tasks/:id', (req, res) => {
  const { id } = req.params;
  const { title, description, status, priority } = req.body;

  const taskIndex = tasks.findIndex(t => t.id === id);
  if (taskIndex === -1) {
    return res.status(404).json({ error: 'Task not found' });
  }

  tasks[taskIndex] = {
    ...tasks[taskIndex],
    title: title || tasks[taskIndex].title,
    description: description !== undefined ? description : tasks[taskIndex].description,
    status: status || tasks[taskIndex].status,
    priority: priority || tasks[taskIndex].priority,
    updatedAt: new Date().toISOString(),
  };

  saveTasksToMarkdown(tasks);
  updateTasks(tasks);

  broadcastToAll({
    type: 'task_updated',
    data: tasks[taskIndex]
  });

  res.json(tasks[taskIndex]);
});

app.delete('/api/tasks/:id', (req, res) => {
  const { id } = req.params;
  const taskIndex = tasks.findIndex(t => t.id === id);

  if (taskIndex === -1) {
    return res.status(404).json({ error: 'Task not found' });
  }

  const deletedTask = tasks[taskIndex];
  tasks.splice(taskIndex, 1);
  saveTasksToMarkdown(tasks);
  updateTasks(tasks);

  broadcastToAll({
    type: 'task_deleted',
    data: deletedTask
  });

  res.json({ message: 'Task deleted', task: deletedTask });
});

// Skills API
app.get('/api/skills', (req, res) => {
  const skills = scanSkills();
  res.json(skills);
});

app.post('/api/skills/:name/install', (req, res) => {
  res.json({ message: 'Skill installation not implemented yet' });
});

app.post('/api/skills/:name/uninstall', (req, res) => {
  res.json({ message: 'Skill uninstallation not implemented yet' });
});

// Messages API
app.get('/api/messages', (req, res) => {
  res.json(messages);
});

app.post('/api/message', (req, res) => {
  const { content, role = 'user' } = req.body;

  if (!content) {
    return res.status(400).json({ error: 'Content is required' });
  }

  const message: Message = {
    id: uuidv4(),
    role,
    content,
    timestamp: new Date().toISOString(),
  };

  messages.push(message);

  // Keep only last 100 messages
  if (messages.length > 100) {
    messages = messages.slice(-100);
  }

  addMessage(message);

  broadcastToAll({
    type: 'message',
    data: message
  });

  res.status(201).json(message);
});

// Memory API
app.get('/api/memory', (req, res) => {
  ensureFileExists(MEMORY_FILE, '# Memory\n');
  const content = fs.readFileSync(MEMORY_FILE, 'utf-8');
  res.json({ content });
});

app.post('/api/memory', (req, res) => {
  const { content } = req.body;
  fs.writeFileSync(MEMORY_FILE, content, 'utf-8');
  res.json({ message: 'Memory updated' });
});

// Workspace files API
app.get('/api/files', (req, res) => {
  const listFiles = (dir: string, basePath: string = ''): any[] => {
    if (!fs.existsSync(dir)) return [];
    
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    const files: any[] = [];

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.join(basePath, entry.name);

      if (entry.isDirectory() && entry.name !== 'node_modules' && !entry.name.startsWith('.')) {
        files.push({
          name: entry.name,
          path: relativePath,
          type: 'directory',
          children: listFiles(fullPath, relativePath)
        });
      } else if (entry.isFile()) {
        files.push({
          name: entry.name,
          path: relativePath,
          type: 'file',
          size: fs.statSync(fullPath).size
        });
      }
    }

    return files;
  };

  res.json(listFiles(WORKSPACE_DIR));
});

app.get('/api/files/*', (req, res) => {
  const filePath = path.join(WORKSPACE_DIR, (req.params as any)[0]);
  
  // Security check
  if (!filePath.startsWith(WORKSPACE_DIR)) {
    return res.status(403).json({ error: 'Access denied' });
  }

  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'File not found' });
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  res.json({ content, path: (req.params as any)[0] });
});

app.post('/api/files/*', (req, res) => {
  const filePath = path.join(WORKSPACE_DIR, (req.params as any)[0]);
  const { content } = req.body;

  // Security check
  if (!filePath.startsWith(WORKSPACE_DIR)) {
    return res.status(403).json({ error: 'Access denied' });
  }

  // Ensure directory exists
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(filePath, content, 'utf-8');
  res.json({ message: 'File saved' });
});

// Initialize
loadTasks();

// Start sync loop
if (isKVConnected()) {
  setInterval(() => {
    syncToKV(getStats());
  }, SYNC_INTERVAL);
  console.log(`🔄 KV sync started: every ${SYNC_INTERVAL}ms`);
}

// Start server
server.listen(PORT, () => {
  console.log(`🚀 OpenClaw Dashboard Server running on port ${PORT}`);
  console.log(`📁 Workspace: ${WORKSPACE_DIR}`);
  console.log(`🔌 WebSocket: ws://localhost:${PORT}/ws`);
  console.log(`☁️  Vercel KV: ${isKVConnected() ? '✅ Connected' : '⚠️  Not configured'}`);
});
