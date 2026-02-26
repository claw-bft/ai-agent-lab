#!/usr/bin/env python3
"""
OpenClaw Dashboard WebSocket Server
Real-time bidirectional communication for interactive dashboard
"""

import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WORKSPACE_DIR = Path(os.environ.get('WORKSPACE_DIR', '/root/.openclaw/workspace'))
HOST = os.environ.get('WS_HOST', '0.0.0.0')
PORT = int(os.environ.get('WS_PORT', '8000'))
HEARTBEAT_INTERVAL = 30  # seconds
DATA_PUSH_INTERVAL = 1   # seconds - push data every second

# Global state
connected_clients: Dict[str, any] = {}
session_data: Dict[str, Any] = {
    'sessions': {},
    'tasks': [],
    'messages': [],
    'stats': {},
    'skills': [],
    'files': []
}
server_start_time = time.time()

# File paths
TASKS_FILE = WORKSPACE_DIR / 'TASKS.md'
MEMORY_FILE = WORKSPACE_DIR / 'MEMORY.md'
SKILLS_DIR = WORKSPACE_DIR / 'skills'


class DashboardServer:
    def __init__(self):
        self.clients: Dict[str, any] = {}
        self.client_info: Dict[str, Dict] = {}
        self.running = False
        
    async def register_client(self, websocket, client_id: str):
        """Register a new WebSocket client"""
        self.clients[client_id] = websocket
        self.client_info[client_id] = {
            'connected_at': datetime.now().isoformat(),
            'ip': websocket.remote_address[0] if websocket.remote_address else 'unknown',
            'port': websocket.remote_address[1] if websocket.remote_address else 0,
            'last_ping': time.time()
        }
        logger.info(f"Client {client_id} connected from {self.client_info[client_id]['ip']}")
        
        # Send welcome message
        await self.send_to_client(client_id, {
            'type': 'connected',
            'data': {
                'client_id': client_id,
                'server_time': datetime.now().isoformat(),
                'message': 'Connected to OpenClaw Dashboard'
            }
        })
        
        # Broadcast client count update
        await self.broadcast({
            'type': 'clients_update',
            'data': {'count': len(self.clients)}
        })
    
    async def unregister_client(self, client_id: str):
        """Unregister a WebSocket client"""
        if client_id in self.clients:
            del self.clients[client_id]
        if client_id in self.client_info:
            logger.info(f"Client {client_id} disconnected")
            del self.client_info[client_id]
        
        # Broadcast client count update
        await self.broadcast({
            'type': 'clients_update',
            'data': {'count': len(self.clients)}
        })
    
    async def send_to_client(self, client_id: str, message: Dict):
        """Send message to specific client"""
        if client_id in self.clients:
            try:
                await self.clients[client_id].send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
    
    async def broadcast(self, message: Dict, exclude: Optional[str] = None):
        """Broadcast message to all connected clients"""
        message_str = json.dumps(message)
        disconnected = []
        
        for client_id, websocket in self.clients.items():
            if client_id == exclude:
                continue
            try:
                await websocket.send(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            await self.unregister_client(client_id)
    
    async def handle_message(self, websocket, client_id: str, data: Dict):
        """Handle incoming WebSocket message"""
        msg_type = data.get('type', 'unknown')
        
        if msg_type == 'ping':
            await self.send_to_client(client_id, {
                'type': 'pong',
                'timestamp': int(time.time() * 1000)
            })
        
        elif msg_type == 'subscribe':
            channels = data.get('channels', [])
            await self.send_to_client(client_id, {
                'type': 'subscribed',
                'data': {'channels': channels}
            })
        
        elif msg_type == 'get_stats':
            stats = self.get_system_stats()
            await self.send_to_client(client_id, {
                'type': 'stats',
                'data': stats
            })
        
        elif msg_type == 'get_tasks':
            tasks = self.load_tasks()
            await self.send_to_client(client_id, {
                'type': 'tasks',
                'data': tasks
            })
        
        elif msg_type == 'create_task':
            task = self.create_task(data.get('data', {}))
            await self.broadcast({
                'type': 'task_created',
                'data': task
            })
        
        elif msg_type == 'update_task':
            task = self.update_task(data.get('id'), data.get('data', {}))
            if task:
                await self.broadcast({
                    'type': 'task_updated',
                    'data': task
                })
        
        elif msg_type == 'delete_task':
            success = self.delete_task(data.get('id'))
            if success:
                await self.broadcast({
                    'type': 'task_deleted',
                    'data': {'id': data.get('id')}
                })
        
        elif msg_type == 'get_skills':
            skills = self.scan_skills()
            await self.send_to_client(client_id, {
                'type': 'skills',
                'data': skills
            })
        
        elif msg_type == 'get_files':
            files = self.list_files()
            await self.send_to_client(client_id, {
                'type': 'files',
                'data': files
            })
        
        elif msg_type == 'read_file':
            content = self.read_file(data.get('path', ''))
            await self.send_to_client(client_id, {
                'type': 'file_content',
                'data': {
                    'path': data.get('path'),
                    'content': content
                }
            })
        
        elif msg_type == 'write_file':
            success = self.write_file(data.get('path', ''), data.get('content', ''))
            await self.send_to_client(client_id, {
                'type': 'file_written',
                'data': {
                    'path': data.get('path'),
                    'success': success
                }
            })
            if success:
                await self.broadcast({
                    'type': 'files_updated',
                    'data': self.list_files()
                })
        
        elif msg_type == 'execute_command':
            # Execute shell command (restricted)
            result = await self.execute_command(data.get('command', ''))
            await self.send_to_client(client_id, {
                'type': 'command_result',
                'data': result
            })
        
        elif msg_type == 'chat_message':
            message = {
                'id': str(uuid.uuid4()),
                'role': data.get('role', 'user'),
                'content': data.get('content', ''),
                'timestamp': datetime.now().isoformat()
            }
            session_data['messages'].append(message)
            if len(session_data['messages']) > 100:
                session_data['messages'] = session_data['messages'][-100:]
            
            await self.broadcast({
                'type': 'chat_message',
                'data': message
            })
        
        else:
            # Echo back for unknown types
            await self.send_to_client(client_id, {
                'type': 'echo',
                'data': data
            })
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        import psutil
        
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'uptime': int(time.time() - server_start_time),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100
            },
            'clients_connected': len(self.clients),
            'timestamp': datetime.now().isoformat()
        }
    
    def load_tasks(self) -> List[Dict]:
        """Load tasks from TASKS.md"""
        tasks = []
        if TASKS_FILE.exists():
            content = TASKS_FILE.read_text()
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- ['):
                    match = line.split('] ', 1)
                    if len(match) == 2:
                        status = 'done' if '[x]' in line.lower() else 'todo'
                        title = match[1]
                        tasks.append({
                            'id': str(uuid.uuid4()),
                            'title': title,
                            'status': status,
                            'created_at': datetime.now().isoformat()
                        })
        session_data['tasks'] = tasks
        return tasks
    
    def create_task(self, data: Dict) -> Dict:
        """Create a new task"""
        task = {
            'id': str(uuid.uuid4()),
            'title': data.get('title', 'Untitled Task'),
            'status': data.get('status', 'todo'),
            'description': data.get('description', ''),
            'priority': data.get('priority', 'medium'),
            'created_at': datetime.now().isoformat()
        }
        session_data['tasks'].append(task)
        self.save_tasks()
        return task
    
    def update_task(self, task_id: str, data: Dict) -> Optional[Dict]:
        """Update an existing task"""
        for i, task in enumerate(session_data['tasks']):
            if task['id'] == task_id:
                session_data['tasks'][i].update(data)
                session_data['tasks'][i]['updated_at'] = datetime.now().isoformat()
                self.save_tasks()
                return session_data['tasks'][i]
        return None
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        for i, task in enumerate(session_data['tasks']):
            if task['id'] == task_id:
                session_data['tasks'].pop(i)
                self.save_tasks()
                return True
        return False
    
    def save_tasks(self):
        """Save tasks to TASKS.md"""
        lines = ['# Tasks\n']
        for task in session_data['tasks']:
            checkbox = '[x]' if task.get('status') == 'done' else '[ ]'
            lines.append(f'- {checkbox} {task["title"]}')
            if task.get('description'):
                lines.append(f'  - {task["description"]}')
        TASKS_FILE.write_text('\n'.join(lines))
    
    def scan_skills(self) -> List[Dict]:
        """Scan skills directory"""
        skills = []
        if SKILLS_DIR.exists():
            for entry in SKILLS_DIR.iterdir():
                if entry.is_dir() and not entry.name.startswith('.'):
                    skill_file = entry / 'SKILL.md'
                    description = 'No description available'
                    if skill_file.exists():
                        content = skill_file.read_text()
                        lines = content.split('\n')
                        if len(lines) > 1:
                            description = lines[1][:100] if lines[1] else description
                    
                    skills.append({
                        'name': entry.name,
                        'description': description,
                        'installed': True
                    })
        session_data['skills'] = skills
        return skills
    
    def list_files(self, path: str = '') -> List[Dict]:
        """List files in workspace"""
        files = []
        target_dir = WORKSPACE_DIR / path if path else WORKSPACE_DIR
        
        if target_dir.exists():
            for entry in sorted(target_dir.iterdir()):
                if entry.name.startswith('.') or entry.name == 'node_modules':
                    continue
                
                file_info = {
                    'name': entry.name,
                    'path': str(entry.relative_to(WORKSPACE_DIR)),
                    'type': 'directory' if entry.is_dir() else 'file',
                    'size': entry.stat().st_size if entry.is_file() else 0,
                    'modified': datetime.fromtimestamp(entry.stat().st_mtime).isoformat()
                }
                
                if entry.is_dir():
                    try:
                        children = self.list_files(str(entry.relative_to(WORKSPACE_DIR)))
                        file_info['children'] = children[:10]  # Limit children
                    except:
                        pass
                
                files.append(file_info)
        
        return files
    
    def read_file(self, file_path: str) -> str:
        """Read file content"""
        target = WORKSPACE_DIR / file_path
        # Security check
        try:
            target.relative_to(WORKSPACE_DIR)
        except ValueError:
            return "Access denied"
        
        if target.exists() and target.is_file():
            try:
                return target.read_text()
            except:
                return "Binary file"
        return "File not found"
    
    def write_file(self, file_path: str, content: str) -> bool:
        """Write file content"""
        target = WORKSPACE_DIR / file_path
        # Security check
        try:
            target.relative_to(WORKSPACE_DIR)
        except ValueError:
            return False
        
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            return True
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            return False
    
    async def execute_command(self, command: str) -> Dict:
        """Execute shell command (restricted)"""
        # Whitelist safe commands
        allowed_prefixes = ['ls', 'cat', 'head', 'tail', 'grep', 'find', 'pwd', 'echo', 'ps']
        
        cmd_parts = command.split()
        if not cmd_parts or cmd_parts[0] not in allowed_prefixes:
            return {
                'success': False,
                'error': 'Command not allowed. Allowed: ' + ', '.join(allowed_prefixes)
            }
        
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=WORKSPACE_DIR
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
            
            return {
                'success': proc.returncode == 0,
                'stdout': stdout.decode()[:10000],  # Limit output
                'stderr': stderr.decode()[:1000]
            }
        except asyncio.TimeoutError:
            return {'success': False, 'error': 'Command timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def data_pusher(self):
        """Push data updates to all clients periodically"""
        while self.running:
            try:
                stats = self.get_system_stats()
                await self.broadcast({
                    'type': 'stats_update',
                    'data': stats
                })
                await asyncio.sleep(DATA_PUSH_INTERVAL)
            except Exception as e:
                logger.error(f"Error in data pusher: {e}")
                await asyncio.sleep(1)
    
    async def heartbeat_checker(self):
        """Check client heartbeats"""
        while self.running:
            try:
                now = time.time()
                disconnected = []
                
                for client_id, info in self.client_info.items():
                    if now - info.get('last_ping', 0) > HEARTBEAT_INTERVAL * 2:
                        disconnected.append(client_id)
                
                for client_id in disconnected:
                    logger.warning(f"Client {client_id} heartbeat timeout")
                    await self.unregister_client(client_id)
                
                await asyncio.sleep(HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.error(f"Error in heartbeat checker: {e}")
                await asyncio.sleep(1)
    
    async def handle_client(self, websocket, path: str):
        """Handle WebSocket client connection"""
        client_id = str(uuid.uuid4())[:8]
        
        try:
            await self.register_client(websocket, client_id)
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, client_id, data)
                except json.JSONDecodeError:
                    await self.send_to_client(client_id, {
                        'type': 'error',
                        'data': {'message': 'Invalid JSON'}
                    })
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    await self.send_to_client(client_id, {
                        'type': 'error',
                        'data': {'message': str(e)}
                    })
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for client {client_id}")
        except Exception as e:
            logger.error(f"Error with client {client_id}: {e}")
        finally:
            await self.unregister_client(client_id)
    
    async def start(self):
        """Start the WebSocket server"""
        self.running = True
        
        # Start background tasks
        asyncio.create_task(self.data_pusher())
        asyncio.create_task(self.heartbeat_checker())
        
        logger.info(f"🚀 Starting WebSocket server on ws://{HOST}:{PORT}")
        logger.info(f"📁 Workspace: {WORKSPACE_DIR}")
        
        async with websockets.serve(self.handle_client, HOST, PORT):
            await asyncio.Future()  # Run forever


async def main():
    """Main entry point"""
    server = DashboardServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.running = False


if __name__ == '__main__':
    asyncio.run(main())
