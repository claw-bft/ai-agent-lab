# ClawHub Registry API - Vercel Serverless Adapter
"""
ClawHub Skill Registry API - Vercel Serverless Entry Point

提供技能包的注册、查询、安装等API服务
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# In-memory registry storage (Vercel serverless - no persistent storage)
# In production, this should connect to a database
REGISTRY_DATA = {
    "skills": [
        {
            "name": "finance-pro",
            "version": "1.0.0",
            "description": "专业金融分析技能包 - 股票行情、技术分析、投资组合",
            "author": "claw-bft",
            "tags": ["finance", "stock", "investment", "analysis"],
            "downloads": 1523,
            "rating": 4.8,
            "repository": "https://github.com/claw-bft/ai-agent-lab/tree/master/finance-pro"
        },
        {
            "name": "coding-pro", 
            "version": "1.0.0",
            "description": "AI代码生成与审查技能包 - 多语言支持、框架模板",
            "author": "claw-bft",
            "tags": ["coding", "ai", "generator", "review"],
            "downloads": 2341,
            "rating": 4.9,
            "repository": "https://github.com/claw-bft/ai-agent-lab/tree/master/coding-pro"
        },
        {
            "name": "product-pro",
            "version": "1.0.0", 
            "description": "产品管理技能包 - PRD生成、竞品分析、市场调研",
            "author": "claw-bft",
            "tags": ["product", "management", "prd", "competitor"],
            "downloads": 1876,
            "rating": 4.7,
            "repository": "https://github.com/claw-bft/ai-agent-lab/tree/master/product-pro"
        },
        {
            "name": "research-pro",
            "version": "1.0.0",
            "description": "深度研究技能包 - 网络搜索、数据分析、竞品监控",
            "author": "claw-bft",
            "tags": ["research", "search", "analysis", "monitor"],
            "downloads": 1245,
            "rating": 4.6,
            "repository": "https://github.com/claw-bft/ai-agent-lab/tree/master/research-pro"
        },
        {
            "name": "clawhub",
            "version": "1.0.0",
            "description": "技能包管理CLI - 安装、更新、发布技能包",
            "author": "claw-bft",
            "tags": ["cli", "skill", "management", "registry"],
            "downloads": 3421,
            "rating": 4.9,
            "repository": "https://github.com/claw-bft/ai-agent-lab/tree/master/skill-cli"
        }
    ],
    "meta": {
        "name": "ClawHub Official Registry",
        "version": "1.0.0",
        "total_skills": 5,
        "total_downloads": 10406
    }
}


class Handler(BaseHTTPRequestHandler):
    """Vercel Serverless HTTP Handler"""
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        # API Routes
        if path == '/api/skills' or path == '/skills':
            # List all skills with optional filtering
            skills = REGISTRY_DATA["skills"]
            
            # Filter by tag
            if 'tag' in query:
                tag = query['tag'][0]
                skills = [s for s in skills if tag in s.get('tags', [])]
            
            # Filter by search query
            if 'q' in query:
                q = query['q'][0].lower()
                skills = [s for s in skills if q in s['name'].lower() 
                         or q in s['description'].lower()
                         or any(q in t for t in s.get('tags', []))]
            
            # Sort by downloads or rating
            sort_by = query.get('sort', ['downloads'])[0]
            if sort_by in ['downloads', 'rating']:
                skills = sorted(skills, key=lambda x: x.get(sort_by, 0), reverse=True)
            
            self.send_json_response({
                "success": True,
                "data": {
                    "skills": skills,
                    "meta": REGISTRY_DATA["meta"],
                    "count": len(skills)
                }
            })
            return
        
        elif path.startswith('/api/skills/') or path.startswith('/skills/'):
            # Get specific skill
            skill_name = path.split('/')[-1]
            skill = next((s for s in REGISTRY_DATA["skills"] if s['name'] == skill_name), None)
            
            if skill:
                self.send_json_response({
                    "success": True,
                    "data": skill
                })
            else:
                self.send_json_response({
                    "success": False,
                    "error": f"Skill '{skill_name}' not found"
                }, 404)
            return
        
        elif path == '/api/health' or path == '/health':
            # Health check
            self.send_json_response({
                "success": True,
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2026-02-28T03:45:00Z"
            })
            return
        
        elif path == '/' or path == '/api':
            # API root
            self.send_json_response({
                "success": True,
                "name": "ClawHub Registry API",
                "version": "1.0.0",
                "endpoints": [
                    {"path": "/api/skills", "method": "GET", "description": "List all skills"},
                    {"path": "/api/skills/{name}", "method": "GET", "description": "Get skill details"},
                    {"path": "/api/health", "method": "GET", "description": "Health check"}
                ],
                "documentation": "https://github.com/claw-bft/ai-agent-lab"
            })
            return
        
        # 404 Not Found
        self.send_json_response({
            "success": False,
            "error": "Not found",
            "path": path
        }, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json_response({
                "success": False,
                "error": "Invalid JSON"
            }, 400)
            return
        
        # Install endpoint (mock for now)
        if path == '/api/install' or path == '/install':
            skill_name = data.get('skill')
            if not skill_name:
                self.send_json_response({
                    "success": False,
                    "error": "Missing 'skill' parameter"
                }, 400)
                return
            
            skill = next((s for s in REGISTRY_DATA["skills"] if s['name'] == skill_name), None)
            if not skill:
                self.send_json_response({
                    "success": False,
                    "error": f"Skill '{skill_name}' not found"
                }, 404)
                return
            
            self.send_json_response({
                "success": True,
                "message": f"Skill '{skill_name}' installation initiated",
                "data": {
                    "skill": skill_name,
                    "version": skill['version'],
                    "repository": skill['repository']
                }
            })
            return
        
        # 404 Not Found
        self.send_json_response({
            "success": False,
            "error": "Not found",
            "path": path
        }, 404)


# Vercel serverless entry point
def handler(request, context):
    """
    Vercel serverless function handler
    
    Args:
        request: Vercel request object
        context: Vercel context object
    
    Returns:
        Response dict with statusCode, headers, and body
    """
    path = request.get('path', '/')
    method = request.get('method', 'GET')
    query = request.get('query', {})
    
    # Handle CORS
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Health check
    if path in ['/health', '/api/health']:
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                "success": True,
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2026-02-28T03:45:00Z"
            })
        }
    
    # List skills
    if path in ['/skills', '/api/skills']:
        skills = REGISTRY_DATA["skills"]
        
        # Filter by tag
        if 'tag' in query:
            tag = query['tag']
            skills = [s for s in skills if tag in s.get('tags', [])]
        
        # Filter by search
        if 'q' in query:
            q = query['q'].lower()
            skills = [s for s in skills if q in s['name'].lower() 
                     or q in s['description'].lower()
                     or any(q in t for t in s.get('tags', []))]
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                "success": True,
                "data": {
                    "skills": skills,
                    "meta": REGISTRY_DATA["meta"],
                    "count": len(skills)
                }
            })
        }
    
    # Get specific skill
    if path.startswith('/skills/') or path.startswith('/api/skills/'):
        skill_name = path.split('/')[-1]
        skill = next((s for s in REGISTRY_DATA["skills"] if s['name'] == skill_name), None)
        
        if skill:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    "success": True,
                    "data": skill
                })
            }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({
                    "success": False,
                    "error": f"Skill '{skill_name}' not found"
                })
            }
    
    # Install skill (POST)
    if method == 'POST' and path in ['/install', '/api/install']:
        body = request.get('body', '{}')
        try:
            data = json.loads(body)
        except:
            data = {}
        
        skill_name = data.get('skill')
        if not skill_name:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    "success": False,
                    "error": "Missing 'skill' parameter"
                })
            }
        
        skill = next((s for s in REGISTRY_DATA["skills"] if s['name'] == skill_name), None)
        if not skill:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({
                    "success": False,
                    "error": f"Skill '{skill_name}' not found"
                })
            }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                "success": True,
                "message": f"Skill '{skill_name}' installation initiated",
                "data": {
                    "skill": skill_name,
                    "version": skill['version'],
                    "repository": skill['repository']
                }
            })
        }
    
    # API root
    if path in ['/', '/api']:
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                "success": True,
                "name": "ClawHub Registry API",
                "version": "1.0.0",
                "endpoints": [
                    {"path": "/api/skills", "method": "GET", "description": "List all skills"},
                    {"path": "/api/skills/{name}", "method": "GET", "description": "Get skill details"},
                    {"path": "/api/health", "method": "GET", "description": "Health check"}
                ],
                "documentation": "https://github.com/claw-bft/ai-agent-lab"
            })
        }
    
    # 404
    return {
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({
            "success": False,
            "error": "Not found",
            "path": path
        })
    }
