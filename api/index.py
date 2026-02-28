"""
ClawHub Registry API - Vercel Serverless Function
技能包注册表API，支持技能包的发布、查询、安装
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# 内存存储（生产环境应使用数据库）
SKILLS_REGISTRY: Dict[str, dict] = {
    "finance-pro": {
        "name": "finance-pro",
        "version": "1.2.0",
        "description": "多数据源金融数据获取，支持Yahoo/东方财富",
        "author": "claw-bft",
        "tags": ["finance", "stock", "data"],
        "downloads": 1250,
        "rating": 4.8,
        "updated_at": "2026-02-27T10:00:00Z",
        "repository": "https://github.com/claw-bft/ai-agent-lab/tree/main/finance-pro",
        "install_url": "https://github.com/claw-bft/ai-agent-lab/releases/download/finance-pro-v1.2.0/finance-pro.tar.gz"
    },
    "coding-pro": {
        "name": "coding-pro",
        "version": "1.1.0",
        "description": "AI代码生成器，支持多语言",
        "author": "claw-bft",
        "tags": ["coding", "generator", "ai"],
        "downloads": 980,
        "rating": 4.6,
        "updated_at": "2026-02-26T08:00:00Z",
        "repository": "https://github.com/claw-bft/ai-agent-lab/tree/main/coding-pro",
        "install_url": "https://github.com/claw-bft/ai-agent-lab/releases/download/coding-pro-v1.1.0/coding-pro.tar.gz"
    },
    "research-pro": {
        "name": "research-pro",
        "version": "1.0.0",
        "description": "智能研究助手，文献综述",
        "author": "claw-bft",
        "tags": ["research", "analysis", "ai"],
        "downloads": 750,
        "rating": 4.5,
        "updated_at": "2026-02-25T12:00:00Z",
        "repository": "https://github.com/claw-bft/ai-agent-lab/tree/main/research-pro",
        "install_url": "https://github.com/claw-bft/ai-agent-lab/releases/download/research-pro-v1.0.0/research-pro.tar.gz"
    },
    "product-pro": {
        "name": "product-pro",
        "version": "1.0.0",
        "description": "PRD生成与产品管理",
        "author": "claw-bft",
        "tags": ["product", "prd", "management"],
        "downloads": 620,
        "rating": 4.7,
        "updated_at": "2026-02-24T14:00:00Z",
        "repository": "https://github.com/claw-bft/ai-agent-lab/tree/main/product-pro",
        "install_url": "https://github.com/claw-bft/ai-agent-lab/releases/download/product-pro-v1.0.0/product-pro.tar.gz"
    },
    "skill-cli": {
        "name": "skill-cli",
        "version": "2.0.0",
        "description": "自然语言执行层，统一技能入口",
        "author": "claw-bft",
        "tags": ["cli", "interface", "core"],
        "downloads": 2100,
        "rating": 4.9,
        "updated_at": "2026-02-28T04:00:00Z",
        "repository": "https://github.com/claw-bft/ai-agent-lab/tree/main/skill-cli",
        "install_url": "https://github.com/claw-bft/ai-agent-lab/releases/download/skill-cli-v2.0.0/skill-cli.tar.gz"
    },
    "memory-enhanced": {
        "name": "memory-enhanced",
        "version": "1.0.0",
        "description": "向量记忆系统 (sqlite-vec)",
        "author": "claw-bft",
        "tags": ["memory", "vector", "database"],
        "downloads": 540,
        "rating": 4.4,
        "updated_at": "2026-02-23T09:00:00Z",
        "repository": "https://github.com/claw-bft/ai-agent-lab/tree/main/memory-enhanced",
        "install_url": "https://github.com/claw-bft/ai-agent-lab/releases/download/memory-enhanced-v1.0.0/memory-enhanced.tar.gz"
    },
    "agent-collaboration": {
        "name": "agent-collaboration",
        "version": "1.0.0",
        "description": "ACP协议多智能体协作",
        "author": "claw-bft",
        "tags": ["agent", "collaboration", "protocol"],
        "downloads": 480,
        "rating": 4.6,
        "updated_at": "2026-02-22T11:00:00Z",
        "repository": "https://github.com/claw-bft/ai-agent-lab/tree/main/agent-collaboration",
        "install_url": "https://github.com/claw-bft/ai-agent-lab/releases/download/agent-collaboration-v1.0.0/agent-collaboration.tar.gz"
    }
}

# 分类数据
CATEGORIES = {
    "finance": {
        "name": "金融分析",
        "description": "股票、基金、加密货币数据分析",
        "skills": ["finance-pro", "stock-portfolio-analyzer", "financial-daily"]
    },
    "coding": {
        "name": "开发工具",
        "description": "代码生成、开发辅助、部署工具",
        "skills": ["coding-pro", "skill-cli", "vercel-deploy"]
    },
    "research": {
        "name": "研究分析",
        "description": "深度研究、竞品分析、文献综述",
        "skills": ["research-pro", "product-pro"]
    },
    "productivity": {
        "name": "生产力",
        "description": "模板、通知、工作流",
        "skills": ["quick-templates", "notification-service", "workflow-orchestrator"]
    },
    "ai-core": {
        "name": "AI核心",
        "description": "记忆、协作、上下文管理",
        "skills": ["memory-enhanced", "agent-collaboration", "context-compressor"]
    }
}


def cors_headers():
    """CORS响应头"""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json"
    }


def json_response(data: dict, status: int = 200) -> tuple:
    """生成JSON响应"""
    return (status, json.dumps(data, ensure_ascii=False, indent=2))


def handle_health() -> tuple:
    """健康检查端点"""
    return json_response({
        "status": "healthy",
        "service": "clawhub-registry",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "skills_count": len(SKILLS_REGISTRY),
        "categories_count": len(CATEGORIES)
    })


def handle_list_skills(query_params: dict) -> tuple:
    """列出所有技能包"""
    tag_filter = query_params.get("tag", [None])[0]
    search_query = query_params.get("q", [None])[0]
    sort_by = query_params.get("sort", ["downloads"])[0]

    skills = list(SKILLS_REGISTRY.values())

    # 标签过滤
    if tag_filter:
        skills = [s for s in skills if tag_filter in s.get("tags", [])]

    # 搜索过滤
    if search_query:
        search_lower = search_query.lower()
        skills = [
            s for s in skills
            if (search_lower in s.get("name", "").lower() or
                search_lower in s.get("description", "").lower() or
                any(search_lower in tag.lower() for tag in s.get("tags", [])))
        ]

    # 排序
    if sort_by == "downloads":
        skills.sort(key=lambda x: x.get("downloads", 0), reverse=True)
    elif sort_by == "rating":
        skills.sort(key=lambda x: x.get("rating", 0), reverse=True)
    elif sort_by == "updated":
        skills.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    return json_response({
        "skills": skills,
        "total": len(skills),
        "filters": {
            "tag": tag_filter,
            "search": search_query,
            "sort": sort_by
        }
    })


def handle_get_skill(skill_name: str) -> tuple:
    """获取单个技能包详情"""
    skill = SKILLS_REGISTRY.get(skill_name)
    if not skill:
        return json_response({
            "error": "Skill not found",
            "skill": skill_name
        }, 404)

    # 增加下载计数（模拟）
    skill["downloads"] = skill.get("downloads", 0) + 1

    return json_response({
        "skill": skill,
        "install_command": f"claw install {skill_name}"
    })


def handle_categories() -> tuple:
    """获取分类列表"""
    return json_response({
        "categories": CATEGORIES
    })


def handle_stats() -> tuple:
    """获取注册表统计信息"""
    total_downloads = sum(s.get("downloads", 0) for s in SKILLS_REGISTRY.values())
    avg_rating = sum(s.get("rating", 0) for s in SKILLS_REGISTRY.values()) / len(SKILLS_REGISTRY) if SKILLS_REGISTRY else 0

    return json_response({
        "total_skills": len(SKILLS_REGISTRY),
        "total_downloads": total_downloads,
        "average_rating": round(avg_rating, 2),
        "total_categories": len(CATEGORIES),
        "top_skills": sorted(
            SKILLS_REGISTRY.values(),
            key=lambda x: x.get("downloads", 0),
            reverse=True
        )[:5]
    })


def handle_publish(body: dict) -> tuple:
    """发布新技能包（需要认证）"""
    # 简化实现，生产环境需要认证
    skill_name = body.get("name")
    if not skill_name:
        return json_response({"error": "Skill name is required"}, 400)

    if skill_name in SKILLS_REGISTRY:
        return json_response({"error": "Skill already exists"}, 409)

    skill_data = {
        "name": skill_name,
        "version": body.get("version", "1.0.0"),
        "description": body.get("description", ""),
        "author": body.get("author", "anonymous"),
        "tags": body.get("tags", []),
        "downloads": 0,
        "rating": 0.0,
        "updated_at": datetime.utcnow().isoformat(),
        "repository": body.get("repository", ""),
        "install_url": body.get("install_url", "")
    }

    SKILLS_REGISTRY[skill_name] = skill_data

    return json_response({
        "message": "Skill published successfully",
        "skill": skill_data
    }, 201)


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Handler"""

    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()

    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        # 路由分发
        if path == "/api/health" or path == "/health":
            status, body = handle_health()
        elif path == "/api/skills" or path == "/skills":
            status, body = handle_list_skills(query_params)
        elif path == "/api/categories" or path == "/categories":
            status, body = handle_categories()
        elif path == "/api/stats" or path == "/stats":
            status, body = handle_stats()
        elif path.startswith("/api/skills/"):
            skill_name = path.split("/")[-1]
            status, body = handle_get_skill(skill_name)
        elif path.startswith("/skills/"):
            skill_name = path.split("/")[-1]
            status, body = handle_get_skill(skill_name)
        else:
            status, body = json_response({
                "error": "Not found",
                "path": path,
                "available_endpoints": [
                    "GET /health",
                    "GET /skills",
                    "GET /skills/{name}",
                    "GET /categories",
                    "GET /stats"
                ]
            }, 404)

        self.send_response(status)
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'

        try:
            body_json = json.loads(body.decode())
        except json.JSONDecodeError:
            body_json = {}

        if path == "/api/skills" or path == "/skills":
            status, response_body = handle_publish(body_json)
        else:
            status, response_body = json_response({
                "error": "Not found",
                "path": path
            }, 404)

        self.send_response(status)
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response_body.encode())
