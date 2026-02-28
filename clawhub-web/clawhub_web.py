"""
ClawHub Web - Python API
ClawHub技能包市场的Python接口和工具集。
"""

import os
import json
import urllib.request
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class SkillPackage:
    """技能包信息"""
    name: str
    display_name: str
    description: str
    category: str
    tags: List[str]
    rating: float
    downloads: int
    install_command: str
    author: str = ""
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillPackage":
        """从字典创建对象"""
        return cls(
            name=data.get('name', ''),
            display_name=data.get('display_name', data.get('displayName', '')),
            description=data.get('description', ''),
            category=data.get('category', ''),
            tags=data.get('tags', []),
            rating=data.get('rating', 0.0),
            downloads=data.get('downloads', 0),
            install_command=data.get('install_command', data.get('installCommand', '')),
            author=data.get('author', ''),
            version=data.get('version', '1.0.0')
        )


@dataclass
class Category:
    """分类信息"""
    id: str
    name: str
    icon: str
    count: int = 0


class ClawHubAPI:
    """ClawHub API客户端"""
    
    DEFAULT_REGISTRY_URL = "https://claw-bft.github.io/ai-agent-lab/registry/api"
    
    def __init__(self, registry_url: Optional[str] = None):
        """
        初始化ClawHub API客户端
        
        Args:
            registry_url: 注册表URL，默认使用GitHub Pages地址
        """
        self.registry_url = registry_url or self.DEFAULT_REGISTRY_URL
    
    def _fetch_json(self, endpoint: str) -> Dict[str, Any]:
        """获取JSON数据"""
        url = f"{self.registry_url}/{endpoint}"
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            # 返回模拟数据作为后备
            return self._get_mock_data(endpoint)
    
    def _get_mock_data(self, endpoint: str) -> Dict[str, Any]:
        """获取模拟数据"""
        if endpoint == "skills":
            return {
                "skills": [
                    {
                        "name": "coding-pro",
                        "displayName": "Coding Pro",
                        "description": "专业代码生成与审查工具",
                        "category": "development",
                        "tags": ["code", "ai", "productivity"],
                        "rating": 4.8,
                        "downloads": 15420,
                        "installCommand": "claw install coding-pro"
                    },
                    {
                        "name": "finance-pro",
                        "displayName": "Finance Pro",
                        "description": "金融数据分析与报告生成",
                        "category": "finance",
                        "tags": ["finance", "data", "report"],
                        "rating": 4.5,
                        "downloads": 8930,
                        "installCommand": "claw install finance-pro"
                    },
                    {
                        "name": "research-pro",
                        "displayName": "Research Pro",
                        "description": "智能研究助手，支持多源信息整合",
                        "category": "research",
                        "tags": ["research", "ai", "productivity"],
                        "rating": 4.6,
                        "downloads": 12340,
                        "installCommand": "claw install research-pro"
                    }
                ]
            }
        elif endpoint == "categories":
            return {
                "categories": [
                    {"id": "development", "name": "开发工具", "icon": "💻", "count": 8},
                    {"id": "finance", "name": "金融", "icon": "💰", "count": 5},
                    {"id": "research", "name": "研究", "icon": "🔬", "count": 4},
                    {"id": "productivity", "name": "生产力", "icon": "⚡", "count": 6}
                ]
            }
        elif endpoint == "stats":
            return {
                "totalSkills": 24,
                "totalDownloads": 125000,
                "totalAuthors": 15,
                "lastUpdated": "2026-03-01T00:00:00Z"
            }
        return {}
    
    def list_skills(self, category: Optional[str] = None,
                   search: Optional[str] = None,
                   sort_by: str = "downloads") -> List[SkillPackage]:
        """
        获取技能包列表
        
        Args:
            category: 分类筛选
            search: 搜索关键词
            sort_by: 排序方式 (downloads/rating/name)
            
        Returns:
            技能包列表
        """
        data = self._fetch_json("skills")
        skills = [SkillPackage.from_dict(s) for s in data.get('skills', [])]
        
        # 分类筛选
        if category:
            skills = [s for s in skills if s.category == category]
        
        # 搜索筛选
        if search:
            search_lower = search.lower()
            skills = [
                s for s in skills 
                if search_lower in s.name.lower() 
                or search_lower in s.description.lower()
                or any(search_lower in t.lower() for t in s.tags)
            ]
        
        # 排序
        if sort_by == "downloads":
            skills.sort(key=lambda x: x.downloads, reverse=True)
        elif sort_by == "rating":
            skills.sort(key=lambda x: x.rating, reverse=True)
        elif sort_by == "name":
            skills.sort(key=lambda x: x.display_name)
        
        return skills
    
    def get_skill(self, name: str) -> Optional[SkillPackage]:
        """
        获取技能包详情
        
        Args:
            name: 技能包名称
            
        Returns:
            技能包信息，不存在则返回None
        """
        data = self._fetch_json(f"skills/{name}")
        if data and 'name' in data:
            return SkillPackage.from_dict(data)
        
        # 尝试从列表中查找
        skills = self.list_skills()
        for skill in skills:
            if skill.name == name:
                return skill
        return None
    
    def list_categories(self) -> List[Category]:
        """
        获取分类列表
        
        Returns:
            分类列表
        """
        data = self._fetch_json("categories")
        return [
            Category(
                id=c.get('id', ''),
                name=c.get('name', ''),
                icon=c.get('icon', '📦'),
                count=c.get('count', 0)
            )
            for c in data.get('categories', [])
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计数据
        """
        return self._fetch_json("stats")


class ClawHubWeb:
    """ClawHub Web工具类"""
    
    def __init__(self, registry_url: Optional[str] = None):
        """
        初始化ClawHub Web工具
        
        Args:
            registry_url: 注册表URL
        """
        self.api = ClawHubAPI(registry_url)
    
    def search_skills(self, query: str) -> List[SkillPackage]:
        """
        搜索技能包
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的技能包列表
        """
        return self.api.list_skills(search=query)
    
    def get_install_command(self, skill_name: str) -> str:
        """
        获取安装命令
        
        Args:
            skill_name: 技能包名称
            
        Returns:
            安装命令
        """
        skill = self.api.get_skill(skill_name)
        if skill:
            return skill.install_command
        return f"claw install {skill_name}"
    
    def get_top_skills(self, limit: int = 5) -> List[SkillPackage]:
        """
        获取热门技能包
        
        Args:
            limit: 返回数量
            
        Returns:
            热门技能包列表
        """
        skills = self.api.list_skills(sort_by="downloads")
        return skills[:limit]
    
    def get_highest_rated(self, limit: int = 5) -> List[SkillPackage]:
        """
        获取评分最高的技能包
        
        Args:
            limit: 返回数量
            
        Returns:
            高评分技能包列表
        """
        skills = self.api.list_skills(sort_by="rating")
        return skills[:limit]
    
    def generate_readme(self, skill_name: str) -> str:
        """
        生成技能包README模板
        
        Args:
            skill_name: 技能包名称
            
        Returns:
            README模板内容
        """
        skill = self.api.get_skill(skill_name)
        if not skill:
            return f"# {skill_name}\n\n技能包信息未找到"
        
        return f"""# {skill.display_name}

{skill.description}

## 安装

```bash
{skill.install_command}
```

## 标签

{', '.join(skill.tags)}

## 评分

⭐ {skill.rating}/5.0

## 下载量

📥 {skill.downloads:,}

## 更多信息

访问 [ClawHub](https://claw-bft.github.io/ai-agent-lab/clawhub-web/) 查看更多技能包。
"""


def search(query: str) -> List[Dict[str, Any]]:
    """
    快速搜索技能包
    
    Args:
        query: 搜索关键词
        
    Returns:
        技能包列表(字典格式)
        
    Example:
        >>> results = search("finance")
        >>> print(results[0]['display_name'])
        'Finance Pro'
    """
    hub = ClawHubWeb()
    skills = hub.search_skills(query)
    return [s.to_dict() for s in skills]


def install_cmd(skill_name: str) -> str:
    """
    获取技能包安装命令
    
    Args:
        skill_name: 技能包名称
        
    Returns:
        安装命令
        
    Example:
        >>> install_cmd("coding-pro")
        'claw install coding-pro'
    """
    hub = ClawHubWeb()
    return hub.get_install_command(skill_name)


if __name__ == "__main__":
    # 简单测试
    import sys
    
    hub = ClawHubWeb()
    
    if len(sys.argv) > 1:
        query = sys.argv[1]
        results = hub.search_skills(query)
        print(f"搜索 '{query}' 找到 {len(results)} 个技能包:")
        for skill in results:
            print(f"  - {skill.display_name}: {skill.description}")
    else:
        print("热门技能包:")
        for skill in hub.get_top_skills(5):
            print(f"  - {skill.display_name} (⭐{skill.rating}, 📥{skill.downloads})")
