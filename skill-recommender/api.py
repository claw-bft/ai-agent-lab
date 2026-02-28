"""
技能推荐系统 Web API 集成
为 ClawHub Web 提供推荐服务接口
"""

import json
from typing import Dict, List, Optional
from skill_recommender import SkillRecommender


class RecommendationAPI:
    """
    推荐系统API接口
    用于与前端JavaScript交互
    """
    
    def __init__(self, recommender: Optional[SkillRecommender] = None):
        """
        初始化API
        
        Args:
            recommender: 推荐器实例，如果为None则创建新实例
        """
        self.recommender = recommender or SkillRecommender()
    
    def get_recommendations(self, user_id: str, n: int = 5, 
                           strategy: str = "hybrid") -> str:
        """
        获取用户推荐（JSON格式）
        
        Args:
            user_id: 用户ID
            n: 推荐数量
            strategy: 推荐策略
            
        Returns:
            JSON字符串
        """
        try:
            recommendations = self.recommender.recommend_for_user(
                user_id=user_id,
                n_recommendations=n,
                strategy=strategy
            )
            
            return json.dumps({
                "success": True,
                "data": recommendations,
                "user_id": user_id,
                "strategy": strategy,
                "count": len(recommendations)
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "user_id": user_id
            }, ensure_ascii=False)
    
    def get_similar_skills(self, skill_name: str, n: int = 5) -> str:
        """
        获取相似技能（JSON格式）
        
        Args:
            skill_name: 技能名称
            n: 返回数量
            
        Returns:
            JSON字符串
        """
        try:
            similar = self.recommender.get_similar_skills(skill_name, n_similar=n)
            
            result = []
            for name, score in similar:
                if name in self.recommender.skills:
                    skill_info = self.recommender.skills[name].to_dict()
                    skill_info["similarity_score"] = round(score, 3)
                    result.append(skill_info)
            
            return json.dumps({
                "success": True,
                "data": result,
                "skill_name": skill_name,
                "count": len(result)
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "skill_name": skill_name
            }, ensure_ascii=False)
    
    def get_trending(self, days: int = 7, n: int = 5) -> str:
        """
        获取热门技能（JSON格式）
        
        Args:
            days: 统计天数
            n: 返回数量
            
        Returns:
            JSON字符串
        """
        try:
            trending = self.recommender.get_trending_skills(days=days, n_skills=n)
            
            return json.dumps({
                "success": True,
                "data": trending,
                "days": days,
                "count": len(trending)
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
    
    def get_user_profile(self, user_id: str) -> str:
        """
        获取用户画像（JSON格式）
        
        Args:
            user_id: 用户ID
            
        Returns:
            JSON字符串
        """
        try:
            profile = self.recommender.get_user_profile(user_id)
            
            return json.dumps({
                "success": True,
                "data": profile,
                "user_id": user_id
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "user_id": user_id
            }, ensure_ascii=False)
    
    def record_interaction(self, user_id: str, skill_name: str, 
                          action: str, rating: Optional[int] = None) -> str:
        """
        记录用户交互（JSON格式）
        
        Args:
            user_id: 用户ID
            skill_name: 技能名称
            action: 交互类型
            rating: 评分（可选）
            
        Returns:
            JSON字符串
        """
        try:
            self.recommender.record_interaction(user_id, skill_name, action, rating)
            
            return json.dumps({
                "success": True,
                "message": f"Recorded {action} for {skill_name}",
                "user_id": user_id,
                "skill_name": skill_name
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "user_id": user_id,
                "skill_name": skill_name
            }, ensure_ascii=False)
    
    def get_categories(self) -> str:
        """
        获取所有分类（JSON格式）
        
        Returns:
            JSON字符串
        """
        try:
            categories = {}
            for skill in self.recommender.skills.values():
                cat = skill.category
                if cat not in categories:
                    categories[cat] = {
                        "name": self._get_category_name(cat),
                        "count": 0,
                        "skills": []
                    }
                categories[cat]["count"] += 1
                categories[cat]["skills"].append(skill.name)
            
            return json.dumps({
                "success": True,
                "data": categories,
                "count": len(categories)
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
    
    def _get_category_name(self, category_id: str) -> str:
        """获取分类显示名称"""
        names = {
            "finance": "金融分析",
            "coding": "开发工具",
            "research": "研究分析",
            "product": "产品管理",
            "ai": "AI增强",
            "productivity": "生产力",
            "infrastructure": "基础设施"
        }
        return names.get(category_id, category_id)


# 全局API实例（用于简单的JavaScript调用）
_api_instance = None

def get_api() -> RecommendationAPI:
    """获取全局API实例"""
    global _api_instance
    if _api_instance is None:
        _api_instance = RecommendationAPI()
    return _api_instance


# 便捷函数，直接导出给JavaScript调用
def recommend(user_id: str, n: int = 5) -> str:
    """获取推荐（JavaScript可直接调用）"""
    return get_api().get_recommendations(user_id, n)


def similar(skill_name: str, n: int = 5) -> str:
    """获取相似技能（JavaScript可直接调用）"""
    return get_api().get_similar_skills(skill_name, n)


def trending(days: int = 7, n: int = 5) -> str:
    """获取热门技能（JavaScript可直接调用）"""
    return get_api().get_trending(days, n)


def profile(user_id: str) -> str:
    """获取用户画像（JavaScript可直接调用）"""
    return get_api().get_user_profile(user_id)


def interact(user_id: str, skill_name: str, action: str, rating: int = None) -> str:
    """记录交互（JavaScript可直接调用）"""
    return get_api().record_interaction(user_id, skill_name, action, rating)


if __name__ == "__main__":
    # 演示API使用
    api = RecommendationAPI()
    
    print("=" * 60)
    print("推荐系统API演示")
    print("=" * 60)
    
    # 记录一些交互
    api.recommender.record_interaction("user_demo", "finance-pro", "download")
    api.recommender.record_interaction("user_demo", "coding-pro", "view")
    
    print("\n1. 获取推荐:")
    print(api.get_recommendations("user_demo", n=3))
    
    print("\n2. 获取相似技能:")
    print(api.get_similar_skills("finance-pro", n=3))
    
    print("\n3. 获取热门技能:")
    print(api.get_trending(days=7, n=3))
    
    print("\n4. 获取用户画像:")
    print(api.get_user_profile("user_demo"))
    
    print("\n5. 获取分类:")
    print(api.get_categories())
    
    print("\n" + "=" * 60)
