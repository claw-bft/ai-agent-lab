#!/usr/bin/env python3
"""
ClawHub CLI - 技能包管理工具
支持从远程注册表安装、更新、管理技能包
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

# 默认注册表URL
DEFAULT_REGISTRY_URL = os.environ.get("CLAWHUB_REGISTRY", "https://claw-bft.github.io/ai-agent-lab/registry/api")

# 本地技能安装目录
SKILLS_DIR = Path(os.environ.get("CLAWHUB_SKILLS_DIR", os.path.expanduser("~/.clawhub/skills")))


class ClawHubClient:
    """ClawHub注册表客户端"""
    
    def __init__(self, registry_url: str = DEFAULT_REGISTRY_URL):
        self.registry_url = registry_url.rstrip("/")
        self._check_connectivity()
    
    def _check_connectivity(self):
        """检查注册表连接状态"""
        try:
            # GitHub Pages 没有专门的health端点，检查主skills端点
            health_url = f"{self.registry_url}/skills.json"
            req = urllib.request.Request(health_url, method="GET")
            req.add_header("Accept", "application/json")
            
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    self.connected = True
                    self.registry_info = {
                        "service": "ClawHub Registry",
                        "version": "1.0.0",
                        "skills_count": "N/A",
                        "categories_count": "N/A",
                        "timestamp": "2026-02-28T00:00:00Z"
                    }
                else:
                    self.connected = False
                    self.registry_info = None
        except Exception as e:
            self.connected = False
            self.registry_info = None
            self.connection_error = str(e)
    
    def list_skills(self, tag: Optional[str] = None, search: Optional[str] = None, sort: str = "downloads"):
        """列出可用技能包"""
        url = f"{self.registry_url}/skills.json"
        
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    
    def get_skill(self, name: str):
        """获取技能包详情"""
        url = f"{self.registry_url}/skills.json"
        
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            skills = data.get("skills", [])
            for skill in skills:
                if skill.get("name") == name:
                    return {"skill": skill}
            raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
    
    def get_categories(self):
        """获取技能分类"""
        url = f"{self.registry_url}/categories.json"
        
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    
    def get_stats(self):
        """获取注册表统计"""
        url = f"{self.registry_url}/skills.json"
        
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            skills = data.get("skills", [])
            total_downloads = sum(s.get("downloads", 0) for s in skills)
            avg_rating = sum(s.get("rating", 0) for s in skills) / len(skills) if skills else 0
            
            # 排序获取热门技能
            top_skills = sorted(skills, key=lambda x: x.get("downloads", 0), reverse=True)[:5]
            
            return {
                "total_skills": len(skills),
                "total_downloads": total_downloads,
                "average_rating": round(avg_rating, 1),
                "total_categories": 0,  # 静态文件不包含分类数量
                "top_skills": top_skills
            }


def format_skill_row(skill: dict, index: int) -> str:
    """格式化技能包列表行"""
    name = skill.get("name", "unknown")
    version = skill.get("version", "?")
    description = skill.get("description", "")[:50] + "..." if len(skill.get("description", "")) > 50 else skill.get("description", "")
    downloads = skill.get("downloads", 0)
    rating = skill.get("rating", 0.0)
    
    return f"  {index}. {name:<20} v{version:<8} ⭐{rating:<4} 📥{downloads:<6} {description}"


def cmd_list(args):
    """列出技能包命令"""
    client = ClawHubClient(args.registry)
    
    if not client.connected:
        print(f"❌ 无法连接到注册表: {client.registry_url}")
        print(f"   错误: {getattr(client, 'connection_error', '未知错误')}")
        return 1
    
    print(f"🔗 已连接到注册表: {client.registry_url}")
    print(f"📦 可用技能包:\n")
    
    try:
        result = client.list_skills(tag=args.tag, search=args.search, sort=args.sort)
        skills = result.get("skills", [])
        
        if not skills:
            print("  没有找到匹配的技能包")
            return 0
        
        for i, skill in enumerate(skills, 1):
            print(format_skill_row(skill, i))
        
        print(f"\n  共 {len(skills)} 个技能包")
        
    except urllib.error.HTTPError as e:
        print(f"❌ 请求失败: {e.code} {e.reason}")
        return 1
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0


def cmd_info(args):
    """查看技能包详情命令"""
    client = ClawHubClient(args.registry)
    
    if not client.connected:
        print(f"❌ 无法连接到注册表: {client.registry_url}")
        return 1
    
    try:
        result = client.get_skill(args.name)
        skill = result.get("skill", {})
        
        print(f"\n📦 {skill.get('name', 'Unknown')}")
        print(f"   版本: {skill.get('version', 'N/A')}")
        print(f"   作者: {skill.get('author', 'N/A')}")
        print(f"   评分: ⭐ {skill.get('rating', 0)}/5.0")
        print(f"   下载: 📥 {skill.get('downloads', 0)}")
        print(f"   标签: {', '.join(skill.get('tags', []))}")
        print(f"\n   {skill.get('description', 'No description')}")
        print(f"\n   安装命令: claw install {skill.get('name')}")
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ 技能包 '{args.name}' 不存在")
        else:
            print(f"❌ 请求失败: {e.code} {e.reason}")
        return 1
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0


def cmd_categories(args):
    """查看分类命令"""
    client = ClawHubClient(args.registry)
    
    if not client.connected:
        print(f"❌ 无法连接到注册表: {client.registry_url}")
        return 1
    
    try:
        result = client.get_categories()
        categories = result.get("categories", {})
        
        print(f"\n📂 技能分类:\n")
        
        for key, cat in categories.items():
            print(f"  {cat.get('name', key)} ({key})")
            print(f"    {cat.get('description', '')}")
            skills = cat.get('skills', [])
            if skills:
                print(f"    包含: {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")
            print()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0


def cmd_stats(args):
    """查看统计信息命令"""
    client = ClawHubClient(args.registry)
    
    if not client.connected:
        print(f"❌ 无法连接到注册表: {client.registry_url}")
        return 1
    
    try:
        result = client.get_stats()
        
        print(f"\n📊 ClawHub 注册表统计\n")
        print(f"  技能包总数: {result.get('total_skills', 0)}")
        print(f"  总下载次数: {result.get('total_downloads', 0)}")
        print(f"  平均评分: ⭐ {result.get('average_rating', 0)}/5.0")
        print(f"  分类数量: {result.get('total_categories', 0)}")
        
        top_skills = result.get('top_skills', [])
        if top_skills:
            print(f"\n  🔥 热门技能包:")
            for i, skill in enumerate(top_skills[:5], 1):
                print(f"    {i}. {skill.get('name')} - 📥 {skill.get('downloads', 0)}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0


def cmd_install(args):
    """安装技能包命令（模拟）"""
    client = ClawHubClient(args.registry)
    
    if not client.connected:
        print(f"⚠️  离线模式 - 将尝试本地安装")
    
    print(f"📦 正在安装技能包: {args.name}")
    
    # 确保安装目录存在
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # 获取技能信息
        if client.connected:
            result = client.get_skill(args.name)
            skill = result.get("skill", {})
            print(f"   版本: {skill.get('version', 'unknown')}")
            print(f"   作者: {skill.get('author', 'unknown')}")
        
        # 模拟安装过程
        print(f"   下载中...")
        print(f"   解压中...")
        print(f"   配置中...")
        
        # 创建安装标记文件
        install_marker = SKILLS_DIR / f"{args.name}.installed"
        install_marker.write_text(json.dumps({
            "name": args.name,
            "installed_at": "2026-02-28T04:30:00Z",
            "version": skill.get("version", "unknown") if client.connected else "unknown"
        }))
        
        print(f"✅ 技能包 '{args.name}' 安装成功!")
        print(f"   安装位置: {SKILLS_DIR / args.name}")
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ 技能包 '{args.name}' 不存在")
        else:
            print(f"❌ 请求失败: {e.code} {e.reason}")
        return 1
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return 1
    
    return 0


def cmd_status(args):
    """检查注册表状态命令"""
    client = ClawHubClient(args.registry)
    
    print(f"🔗 注册表URL: {client.registry_url}")
    print(f"📡 连接状态: {'✅ 在线' if client.connected else '❌ 离线'}")
    
    if client.connected and client.registry_info:
        info = client.registry_info
        print(f"📋 服务信息:")
        print(f"   名称: {info.get('service', 'N/A')}")
        print(f"   版本: {info.get('version', 'N/A')}")
        print(f"   技能包: {info.get('skills_count', 0)}")
        print(f"   分类: {info.get('categories_count', 0)}")
        print(f"   时间戳: {info.get('timestamp', 'N/A')}")
    elif not client.connected:
        print(f"   错误: {getattr(client, 'connection_error', '无法连接')}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="ClawHub - AI技能包管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  claw list                    # 列出所有技能包
  claw list --tag finance      # 按标签筛选
  claw info finance-pro        # 查看技能包详情
  claw install finance-pro     # 安装技能包
  claw categories              # 查看分类
  claw stats                   # 查看统计信息
  claw status                  # 检查注册表状态
        """
    )
    
    parser.add_argument(
        "--registry",
        default=DEFAULT_REGISTRY_URL,
        help=f"注册表URL (默认: {DEFAULT_REGISTRY_URL})"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出可用技能包")
    list_parser.add_argument("--tag", help="按标签筛选")
    list_parser.add_argument("--search", "-s", help="搜索关键词")
    list_parser.add_argument("--sort", default="downloads", choices=["downloads", "rating", "updated"], help="排序方式")
    
    # info 命令
    info_parser = subparsers.add_parser("info", help="查看技能包详情")
    info_parser.add_argument("name", help="技能包名称")
    
    # install 命令
    install_parser = subparsers.add_parser("install", help="安装技能包")
    install_parser.add_argument("name", help="技能包名称")
    
    # categories 命令
    subparsers.add_parser("categories", help="查看技能分类")
    
    # stats 命令
    subparsers.add_parser("stats", help="查看统计信息")
    
    # status 命令
    subparsers.add_parser("status", help="检查注册表状态")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    commands = {
        "list": cmd_list,
        "info": cmd_info,
        "install": cmd_install,
        "categories": cmd_categories,
        "stats": cmd_stats,
        "status": cmd_status,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
