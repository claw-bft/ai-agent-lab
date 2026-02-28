"""
AI驱动的技能推荐系统
基于用户使用模式和技能特征的智能推荐引擎
"""

import json
import math
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Skill:
    """技能包数据模型"""
    name: str
    display_name: str
    description: str
    category: str
    tags: List[str] = field(default_factory=list)
    downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    version: str = "1.0.0"
    author: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "downloads": self.downloads,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "version": self.version,
            "author": self.author,
            "updated_at": self.updated_at
        }


@dataclass
class UserInteraction:
    """用户与技能的交互记录"""
    user_id: str
    skill_name: str
    action: str  # 'view', 'download', 'rate', 'install'
    timestamp: datetime
    rating: Optional[int] = None  # 1-5评分
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "skill_name": self.skill_name,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "rating": self.rating
        }


class SkillRecommender:
    """
    技能推荐引擎
    
    支持多种推荐策略:
    - 协同过滤 (Collaborative Filtering)
    - 基于内容的推荐 (Content-Based)
    - 热门推荐 (Popularity-Based)
    - 混合推荐 (Hybrid)
    """
    
    def __init__(self, skills_data: Optional[List[Dict]] = None):
        """
        初始化推荐器
        
        Args:
            skills_data: 技能包数据列表，如果为None则使用默认数据
        """
        self.skills: Dict[str, Skill] = {}
        self.user_interactions: List[UserInteraction] = []
        self.user_skill_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.skill_vectors: Dict[str, Dict[str, float]] = {}
        self.idf_scores: Dict[str, float] = {}
        
        # 加载技能数据
        if skills_data:
            self._load_skills(skills_data)
        else:
            self._load_default_skills()
        
        # 构建特征向量
        self._build_skill_vectors()
    
    def _load_skills(self, skills_data: List[Dict]):
        """加载技能数据"""
        for data in skills_data:
            skill = Skill(
                name=data.get("name", ""),
                display_name=data.get("display_name", data.get("name", "")),
                description=data.get("description", ""),
                category=data.get("category", "other"),
                tags=data.get("tags", []),
                downloads=data.get("downloads", 0),
                rating=data.get("rating", 0.0),
                rating_count=data.get("rating_count", 0),
                version=data.get("version", "1.0.0"),
                author=data.get("author", ""),
                updated_at=data.get("updated_at", "")
            )
            self.skills[skill.name] = skill
    
    def _load_default_skills(self):
        """加载默认技能数据"""
        default_skills = [
            {
                "name": "finance-pro",
                "display_name": "Finance Pro",
                "description": "多数据源金融数据获取，支持Yahoo/东方财富，含技术指标计算",
                "category": "finance",
                "tags": ["finance", "data", "stocks", "indicators"],
                "downloads": 342,
                "rating": 4.8,
                "rating_count": 45
            },
            {
                "name": "stock-portfolio-analyzer",
                "display_name": "Stock Portfolio Analyzer",
                "description": "投资组合分析与早报生成，支持多维度风险评估",
                "category": "finance",
                "tags": ["finance", "analysis", "portfolio", "risk"],
                "downloads": 298,
                "rating": 4.7,
                "rating_count": 38
            },
            {
                "name": "coding-pro",
                "display_name": "Coding Pro",
                "description": "AI代码生成器，支持多语言和框架，含测试生成",
                "category": "coding",
                "tags": ["coding", "ai", "code-generation", "testing"],
                "downloads": 256,
                "rating": 4.5,
                "rating_count": 32
            },
            {
                "name": "skill-cli",
                "display_name": "Skill CLI",
                "description": "自然语言执行层，让AI理解并执行复杂任务",
                "category": "ai",
                "tags": ["cli", "core", "nlp", "execution"],
                "downloads": 412,
                "rating": 4.9,
                "rating_count": 58
            },
            {
                "name": "research-pro",
                "display_name": "Research Pro",
                "description": "智能研究助手，文献综述与竞品分析",
                "category": "research",
                "tags": ["research", "analysis", "literature", "competitive"],
                "downloads": 189,
                "rating": 4.6,
                "rating_count": 24
            },
            {
                "name": "product-pro",
                "display_name": "Product Pro",
                "description": "PRD生成与产品管理，快速产出专业文档",
                "category": "product",
                "tags": ["product", "docs", "prd", "management"],
                "downloads": 234,
                "rating": 4.7,
                "rating_count": 31
            },
            {
                "name": "memory-enhanced",
                "display_name": "Memory Enhanced",
                "description": "向量记忆系统，基于sqlite-vec的长期记忆",
                "category": "ai",
                "tags": ["ai", "memory", "vector", "sqlite"],
                "downloads": 178,
                "rating": 4.4,
                "rating_count": 22
            },
            {
                "name": "agent-collaboration",
                "display_name": "Agent Collaboration",
                "description": "ACP协议多智能体协作框架",
                "category": "ai",
                "tags": ["ai", "collaboration", "agents", "protocol"],
                "downloads": 156,
                "rating": 4.5,
                "rating_count": 19
            },
            {
                "name": "claude-domain-skills",
                "display_name": "Claude Domain Skills",
                "description": "18个领域的专业知识库，涵盖商业/金融/创意等",
                "category": "ai",
                "tags": ["domains", "knowledge", "claude", "expertise"],
                "downloads": 567,
                "rating": 4.9,
                "rating_count": 72
            },
            {
                "name": "token-manager",
                "display_name": "Token Manager",
                "description": "统一配置管理系统，多技能包配置共享",
                "category": "productivity",
                "tags": ["config", "core", "tokens", "management"],
                "downloads": 312,
                "rating": 4.8,
                "rating_count": 41
            },
            {
                "name": "workflow-orchestrator",
                "display_name": "Workflow Orchestrator",
                "description": "可视化工作流编排系统，支持节点编辑和自动执行",
                "category": "ai",
                "tags": ["workflow", "visual", "automation", "editor"],
                "downloads": 223,
                "rating": 4.6,
                "rating_count": 28
            },
            {
                "name": "context-compressor",
                "display_name": "Context Compressor",
                "description": "智能上下文压缩，优化大模型token使用",
                "category": "ai",
                "tags": ["ai", "compression", "context", "optimization"],
                "downloads": 167,
                "rating": 4.3,
                "rating_count": 18
            },
            {
                "name": "multi-tenant",
                "display_name": "Multi Tenant",
                "description": "企业级多租户系统，支持SaaS部署",
                "category": "infrastructure",
                "tags": ["enterprise", "saas", "multi-tenant", "auth"],
                "downloads": 145,
                "rating": 4.5,
                "rating_count": 16
            },
            {
                "name": "notification-service",
                "display_name": "Notification Service",
                "description": "统一通知服务，支持多通道消息推送",
                "category": "infrastructure",
                "tags": ["notifications", "service", "messaging", "alerts"],
                "downloads": 198,
                "rating": 4.4,
                "rating_count": 25
            },
            {
                "name": "financial-daily",
                "display_name": "Financial Daily",
                "description": "每日财经早报生成，自动抓取市场数据",
                "category": "finance",
                "tags": ["finance", "daily", "news", "automation"],
                "downloads": 276,
                "rating": 4.6,
                "rating_count": 34
            }
        ]
        self._load_skills(default_skills)
    
    def _build_skill_vectors(self):
        """构建技能的TF-IDF特征向量"""
        # 收集所有词汇
        all_terms = set()
        term_freq = defaultdict(lambda: defaultdict(int))
        
        for skill_name, skill in self.skills.items():
            # 从描述和标签中提取词汇
            text = skill.description.lower() + " " + " ".join(skill.tags).lower()
            terms = self._tokenize(text)
            
            for term in terms:
                term_freq[skill_name][term] += 1
                all_terms.add(term)
        
        # 计算IDF
        n_skills = len(self.skills)
        for term in all_terms:
            doc_count = sum(1 for skill_name in term_freq if term_freq[skill_name][term] > 0)
            self.idf_scores[term] = math.log(n_skills / (doc_count + 1)) + 1
        
        # 构建TF-IDF向量
        for skill_name, skill in self.skills.items():
            vector = {}
            terms = self._tokenize(skill.description.lower() + " " + " ".join(skill.tags).lower())
            term_count = len(terms)
            
            for term in set(terms):
                tf = term_freq[skill_name][term] / term_count if term_count > 0 else 0
                idf = self.idf_scores.get(term, 1.0)
                vector[term] = tf * idf
            
            self.skill_vectors[skill_name] = vector
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 移除非字母数字字符，分词
        import re
        return re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """计算两个向量的余弦相似度"""
        all_keys = set(vec1.keys()) | set(vec2.keys())
        
        dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in all_keys)
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def record_interaction(self, user_id: str, skill_name: str,
                           action: str, rating: Optional[int] = None):
        """
        记录用户交互
        
        Args:
            user_id: 用户ID
            skill_name: 技能名称
            action: 交互类型 ('view', 'download', 'rate', 'install')
            rating: 评分 (1-5)，仅当action为'rate'时需要
        """
        interaction = UserInteraction(
            user_id=user_id,
            skill_name=skill_name,
            action=action,
            timestamp=datetime.now(),
            rating=rating
        )
        self.user_interactions.append(interaction)
        
        # 更新用户-技能矩阵
        weight = self._get_action_weight(action, rating)
        if skill_name in self.user_skill_matrix[user_id]:
            self.user_skill_matrix[user_id][skill_name] += weight
        else:
            self.user_skill_matrix[user_id][skill_name] = weight
    
    def _get_action_weight(self, action: str, rating: Optional[int] = None) -> float:
        """获取交互类型的权重"""
        weights = {
            'view': 0.5,
            'download': 2.0,
            'install': 3.0,
            'rate': 1.0
        }
        base_weight = weights.get(action, 0.5)
        
        if action == 'rate' and rating:
            # 评分权重：高分表示更喜欢
            base_weight *= (rating / 3.0)
        
        return base_weight
    
    def get_similar_skills(self, skill_name: str, n_similar: int = 5) -> List[Tuple[str, float]]:
        """
        获取与指定技能相似的技能
        
        Args:
            skill_name: 参考技能名称
            n_similar: 返回的相似技能数量
            
        Returns:
            列表，每项为(技能名称, 相似度分数)
        """
        if skill_name not in self.skills:
            return []
        
        target_vector = self.skill_vectors.get(skill_name, {})
        similarities = []
        
        for name, vector in self.skill_vectors.items():
            if name != skill_name:
                sim = self._cosine_similarity(target_vector, vector)
                # 加入类别匹配加分
                if self.skills[name].category == self.skills[skill_name].category:
                    sim += 0.1
                similarities.append((name, sim))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n_similar]
    
    def recommend_collaborative(self, user_id: str, n_recommendations: int = 5) -> List[Tuple[str, float]]:
        """
        基于协同过滤的推荐
        
        Args:
            user_id: 用户ID
            n_recommendations: 推荐数量
            
        Returns:
            列表，每项为(技能名称, 推荐分数)
        """
        user_skills = self.user_skill_matrix.get(user_id, {})
        
        if not user_skills:
            # 新用户，返回热门推荐
            return self.recommend_popular(n_recommendations)
        
        # 找到相似用户
        user_similarities = []
        for other_user_id, other_skills in self.user_skill_matrix.items():
            if other_user_id != user_id:
                sim = self._user_similarity(user_skills, other_skills)
                if sim > 0:
                    user_similarities.append((other_user_id, sim))
        
        user_similarities.sort(key=lambda x: x[1], reverse=True)
        top_similar_users = user_similarities[:10]  # 取前10个相似用户
        
        # 基于相似用户的偏好推荐
        skill_scores = defaultdict(float)
        
        for other_user_id, similarity in top_similar_users:
            for skill_name, weight in self.user_skill_matrix[other_user_id].items():
                if skill_name not in user_skills:  # 只推荐用户未交互过的
                    skill_scores[skill_name] += similarity * weight
        
        # 排序并返回
        recommendations = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]
    
    def _user_similarity(self, user1_skills: Dict[str, float],
                         user2_skills: Dict[str, float]) -> float:
        """计算两个用户的相似度（基于共同喜欢的技能）"""
        common_skills = set(user1_skills.keys()) & set(user2_skills.keys())
        
        if not common_skills:
            return 0.0
        
        # 使用余弦相似度
        all_skills = set(user1_skills.keys()) | set(user2_skills.keys())
        vec1 = [user1_skills.get(s, 0) for s in all_skills]
        vec2 = [user2_skills.get(s, 0) for s in all_skills]
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a ** 2 for a in vec1))
        norm2 = math.sqrt(sum(b ** 2 for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def recommend_content_based(self, user_id: str, n_recommendations: int = 5) -> List[Tuple[str, float]]:
        """
        基于内容的推荐
        
        Args:
            user_id: 用户ID
            n_recommendations: 推荐数量
            
        Returns:
            列表，每项为(技能名称, 推荐分数)
        """
        user_skills = self.user_skill_matrix.get(user_id, {})
        
        if not user_skills:
            return self.recommend_popular(n_recommendations)
        
        # 构建用户偏好向量（基于已交互技能的加权平均）
        user_vector = defaultdict(float)
        total_weight = 0
        
        for skill_name, weight in user_skills.items():
            if skill_name in self.skill_vectors:
                for term, value in self.skill_vectors[skill_name].items():
                    user_vector[term] += value * weight
                total_weight += weight
        
        if total_weight > 0:
            for term in user_vector:
                user_vector[term] /= total_weight
        
        # 计算与所有未交互技能的相似度
        skill_scores = []
        for skill_name, skill_vector in self.skill_vectors.items():
            if skill_name not in user_skills:
                sim = self._cosine_similarity(dict(user_vector), skill_vector)
                skill_scores.append((skill_name, sim))
        
        skill_scores.sort(key=lambda x: x[1], reverse=True)
        return skill_scores[:n_recommendations]
    
    def recommend_popular(self, n_recommendations: int = 5,
                          exclude_user: Optional[str] = None) -> List[Tuple[str, float]]:
        """
        基于热门程度的推荐
        
        Args:
            n_recommendations: 推荐数量
            exclude_user: 排除该用户已交互的技能
            
        Returns:
            列表，每项为(技能名称, 推荐分数)
        """
        exclude_skills = set()
        if exclude_user and exclude_user in self.user_skill_matrix:
            exclude_skills = set(self.user_skill_matrix[exclude_user].keys())
        
        # 综合下载量和评分计算热门分数
        popularity_scores = []
        for skill_name, skill in self.skills.items():
            if skill_name not in exclude_skills:
                # 归一化下载量 (假设最大下载量为1000)
                download_score = min(skill.downloads / 1000, 1.0)
                # 评分分数
                rating_score = skill.rating / 5.0 if skill.rating else 0
                # 综合分数
                score = download_score * 0.6 + rating_score * 0.4
                popularity_scores.append((skill_name, score))
        
        popularity_scores.sort(key=lambda x: x[1], reverse=True)
        return popularity_scores[:n_recommendations]
    
    def recommend_for_user(self, user_id: str, n_recommendations: int = 5,
                           strategy: str = "hybrid") -> List[Dict]:
        """
        为用户生成推荐
        
        Args:
            user_id: 用户ID
            n_recommendations: 推荐数量
            strategy: 推荐策略 ('hybrid', 'collaborative', 'content', 'popular')
            
        Returns:
            推荐技能列表，每项包含完整技能信息和推荐分数
        """
        if strategy == "collaborative":
            recommendations = self.recommend_collaborative(user_id, n_recommendations)
        elif strategy == "content":
            recommendations = self.recommend_content_based(user_id, n_recommendations)
        elif strategy == "popular":
            recommendations = self.recommend_popular(n_recommendations, user_id)
        else:  # hybrid
            recommendations = self._hybrid_recommend(user_id, n_recommendations)
        
        # 转换为完整技能信息
        result = []
        for skill_name, score in recommendations:
            if skill_name in self.skills:
                skill_info = self.skills[skill_name].to_dict()
                skill_info["recommend_score"] = round(score, 3)
                skill_info["recommend_reason"] = self._get_recommend_reason(user_id, skill_name)
                result.append(skill_info)
        
        return result
    
    def _hybrid_recommend(self, user_id: str, n_recommendations: int) -> List[Tuple[str, float]]:
        """混合推荐策略"""
        # 获取各种策略的推荐
        collaborative = self.recommend_collaborative(user_id, n_recommendations * 2)
        content_based = self.recommend_content_based(user_id, n_recommendations * 2)
        popular = self.recommend_popular(n_recommendations * 2, user_id)
        
        # 加权融合
        skill_scores = defaultdict(float)
        
        # 协同过滤权重 0.4
        for skill_name, score in collaborative:
            skill_scores[skill_name] += score * 0.4
        
        # 内容推荐权重 0.35
        for skill_name, score in content_based:
            skill_scores[skill_name] += score * 0.35
        
        # 热门推荐权重 0.25
        for skill_name, score in popular:
            skill_scores[skill_name] += score * 0.25
        
        # 排序
        recommendations = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]
    
    def _get_recommend_reason(self, user_id: str, skill_name: str) -> str:
        """生成推荐理由"""
        user_skills = self.user_skill_matrix.get(user_id, {})
        skill = self.skills.get(skill_name)

        if not skill:
            return "热门推荐"

        # 检查是否有相似用户喜欢
        reason = self._get_collaborative_reason(user_id, skill_name, user_skills)
        if reason:
            return reason

        # 检查内容相似性
        reason = self._get_content_reason(user_skills, skill)
        if reason:
            return reason

        # 基于热门程度或评分
        return self._get_popularity_reason(skill)

    def _get_collaborative_reason(self, user_id: str, skill_name: str,
                                  user_skills: Dict[str, float]) -> Optional[str]:
        """基于协同过滤生成推荐理由"""
        if not user_skills:
            return None

        for other_user, other_skills in self.user_skill_matrix.items():
            if other_user != user_id and skill_name in other_skills:
                common = set(user_skills.keys()) & set(other_skills.keys())
                if common:
                    return f"与您使用过的 {len(common)} 个技能相似的用户也喜欢"
        return None

    def _get_content_reason(self, user_skills: Dict[str, float], skill) -> Optional[str]:
        """基于内容相似性生成推荐理由"""
        if not user_skills:
            return None

        for user_skill_name in user_skills:
            if user_skill_name in self.skills:
                user_skill = self.skills[user_skill_name]
                if user_skill.category == skill.category:
                    return f"基于您对 {user_skill.display_name} 的喜好推荐"
        return None

    def _get_popularity_reason(self, skill) -> str:
        """基于热门程度生成推荐理由"""
        if skill.downloads > 300:
            return f"{skill.downloads}+ 次下载的热门技能"

        if skill.rating >= 4.5:
            return f"高评分技能 ({skill.rating}⭐)"

        return "为您推荐"
    
    def get_trending_skills(self, days: int = 7, n_skills: int = 5) -> List[Dict]:
        """
        获取近期热门技能
        
        Args:
            days: 统计天数
            n_skills: 返回数量
            
        Returns:
            热门技能列表
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 统计近期交互
        recent_interactions = defaultdict(int)
        for interaction in self.user_interactions:
            if interaction.timestamp >= cutoff_date:
                recent_interactions[interaction.skill_name] += 1
        
        # 排序
        trending = sorted(recent_interactions.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for skill_name, count in trending[:n_skills]:
            if skill_name in self.skills:
                skill_info = self.skills[skill_name].to_dict()
                skill_info["recent_downloads"] = count
                result.append(skill_info)
        
        return result
    
    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户画像信息
        """
        user_skills = self.user_skill_matrix.get(user_id, {})
        
        if not user_skills:
            return {
                "user_id": user_id,
                "total_interactions": 0,
                "favorite_category": None,
                "top_skills": [],
                "activity_level": "new"
            }
        
        # 统计类别偏好
        category_counts = defaultdict(float)
        top_skills = []
        
        for skill_name, weight in sorted(user_skills.items(), key=lambda x: x[1], reverse=True):
            if skill_name in self.skills:
                skill = self.skills[skill_name]
                category_counts[skill.category] += weight
                top_skills.append({
                    "name": skill_name,
                    "display_name": skill.display_name,
                    "weight": weight
                })
        
        favorite_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        
        # 活跃度分级
        total_weight = sum(user_skills.values())
        if total_weight > 20:
            activity_level = "highly_active"
        elif total_weight > 10:
            activity_level = "active"
        elif total_weight > 5:
            activity_level = "moderate"
        else:
            activity_level = "casual"
        
        return {
            "user_id": user_id,
            "total_interactions": len(user_skills),
            "favorite_category": favorite_category,
            "top_skills": top_skills[:5],
            "activity_level": activity_level,
            "category_preferences": dict(category_counts)
        }
    
    def export_model(self) -> Dict:
        """导出推荐模型数据"""
        return {
            "skills": {name: skill.to_dict() for name, skill in self.skills.items()},
            "user_interactions": [i.to_dict() for i in self.user_interactions],
            "user_skill_matrix": dict(self.user_skill_matrix),
            "skill_vectors": self.skill_vectors,
            "idf_scores": self.idf_scores,
            "export_time": datetime.now().isoformat()
        }
    
    def import_model(self, data: Dict):
        """导入推荐模型数据"""
        if "skills" in data:
            self._load_skills(list(data["skills"].values()))
        
        if "user_interactions" in data:
            self.user_interactions = [
                UserInteraction(
                    user_id=i["user_id"],
                    skill_name=i["skill_name"],
                    action=i["action"],
                    timestamp=datetime.fromisoformat(i["timestamp"]),
                    rating=i.get("rating")
                )
                for i in data["user_interactions"]
            ]
        
        if "user_skill_matrix" in data:
            self.user_skill_matrix = defaultdict(dict, data["user_skill_matrix"])
        
        if "skill_vectors" in data:
            self.skill_vectors = data["skill_vectors"]
        
        if "idf_scores" in data:
            self.idf_scores = data["idf_scores"]


# 便捷函数
def create_recommender(skills_data: Optional[List[Dict]] = None) -> SkillRecommender:
    """创建推荐器实例"""
    return SkillRecommender(skills_data)


def get_recommendations(user_id: str, n: int = 5, strategy: str = "hybrid") -> List[Dict]:
    """快速获取推荐（使用默认数据）"""
    recommender = SkillRecommender()
    return recommender.recommend_for_user(user_id, n, strategy)


if __name__ == "__main__":
    # 演示
    print("=" * 60)
    print("AI技能推荐系统演示")
    print("=" * 60)
    
    recommender = SkillRecommender()
    
    # 模拟用户行为
    print("\n1. 模拟用户行为...")
    recommender.record_interaction("user_001", "finance-pro", "download")
    recommender.record_interaction("user_001", "stock-portfolio-analyzer", "download")
    recommender.record_interaction("user_001", "finance-pro", "rate", 5)
    
    recommender.record_interaction("user_002", "coding-pro", "download")
    recommender.record_interaction("user_002", "skill-cli", "download")
    recommender.record_interaction("user_002", "finance-pro", "download")
    
    # 为用户001生成推荐
    print("\n2. 为用户 user_001 生成推荐...")
    recommendations = recommender.recommend_for_user("user_001", n_recommendations=5)
    
    print("\n推荐结果:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['display_name']} ({rec['name']})")
        print(f"     分数: {rec['recommend_score']}")
        print(f"     原因: {rec['recommend_reason']}")
    
    # 获取相似技能
    print("\n3. 与 'finance-pro' 相似的技能:")
    similar = recommender.get_similar_skills("finance-pro", n_similar=3)
    for skill_name, score in similar:
        skill = recommender.skills[skill_name]
        print(f"  - {skill.display_name}: {score:.3f}")
    
    # 用户画像
    print("\n4. 用户画像:")
    profile = recommender.get_user_profile("user_001")
    print(f"  用户ID: {profile['user_id']}")
    print(f"  交互次数: {profile['total_interactions']}")
    print(f"  偏好类别: {profile['favorite_category']}")
    print(f"  活跃程度: {profile['activity_level']}")
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)
