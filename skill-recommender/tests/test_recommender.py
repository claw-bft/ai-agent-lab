"""
技能推荐系统测试套件
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skill_recommender import (
    SkillRecommender, Skill, UserInteraction,
    create_recommender, get_recommendations
)


class TestSkillRecommender:
    """测试技能推荐器核心功能"""
    
    @pytest.fixture
    def recommender(self):
        """创建测试用的推荐器实例"""
        return SkillRecommender()
    
    @pytest.fixture
    def sample_skills(self):
        """测试用技能数据"""
        return [
            {
                "name": "test-skill-1",
                "display_name": "Test Skill 1",
                "description": "A test skill for coding and development",
                "category": "coding",
                "tags": ["coding", "test"],
                "downloads": 100,
                "rating": 4.5
            },
            {
                "name": "test-skill-2",
                "display_name": "Test Skill 2",
                "description": "Another test skill for finance analysis",
                "category": "finance",
                "tags": ["finance", "analysis"],
                "downloads": 200,
                "rating": 4.0
            }
        ]
    
    def test_initialization(self, recommender):
        """测试推荐器初始化"""
        assert len(recommender.skills) > 0
        assert len(recommender.skill_vectors) > 0
        assert len(recommender.idf_scores) > 0
    
    def test_load_skills(self, sample_skills):
        """测试加载技能数据"""
        recommender = SkillRecommender(skills_data=sample_skills)
        assert "test-skill-1" in recommender.skills
        assert "test-skill-2" in recommender.skills
        assert recommender.skills["test-skill-1"].category == "coding"
    
    def test_record_interaction(self, recommender):
        """测试记录用户交互"""
        recommender.record_interaction("user_001", "finance-pro", "view")
        recommender.record_interaction("user_001", "finance-pro", "download")
        recommender.record_interaction("user_001", "finance-pro", "rate", 5)
        
        assert len(recommender.user_interactions) == 3
        assert "finance-pro" in recommender.user_skill_matrix["user_001"]
        assert recommender.user_skill_matrix["user_001"]["finance-pro"] > 0
    
    def test_get_similar_skills(self, recommender):
        """测试获取相似技能"""
        similar = recommender.get_similar_skills("finance-pro", n_similar=3)
        
        assert isinstance(similar, list)
        assert len(similar) <= 3
        
        if similar:
            skill_name, score = similar[0]
            assert isinstance(skill_name, str)
            assert isinstance(score, float)
            assert 0 <= score <= 1.5  # 考虑类别匹配加分
    
    def test_recommend_popular(self, recommender):
        """测试热门推荐"""
        popular = recommender.recommend_popular(n_recommendations=5)
        
        assert isinstance(popular, list)
        assert len(popular) <= 5
        
        if len(popular) >= 2:
            # 验证按分数排序
            assert popular[0][1] >= popular[1][1]
    
    def test_recommend_collaborative_new_user(self, recommender):
        """测试新用户的协同过滤推荐（应返回热门推荐）"""
        recommendations = recommender.recommend_collaborative("new_user", n_recommendations=5)
        
        assert isinstance(recommendations, list)
        # 新用户应该返回热门推荐
        assert len(recommendations) > 0
    
    def test_recommend_content_based(self, recommender):
        """测试基于内容的推荐"""
        # 先记录一些交互
        recommender.record_interaction("user_001", "finance-pro", "download")
        recommender.record_interaction("user_001", "stock-portfolio-analyzer", "download")
        
        recommendations = recommender.recommend_content_based("user_001", n_recommendations=5)
        
        assert isinstance(recommendations, list)
        # 不应推荐已交互的技能
        for skill_name, _ in recommendations:
            assert skill_name not in ["finance-pro", "stock-portfolio-analyzer"]
    
    def test_hybrid_recommend(self, recommender):
        """测试混合推荐"""
        # 记录用户行为
        recommender.record_interaction("user_001", "finance-pro", "download")
        
        recommendations = recommender._hybrid_recommend("user_001", n_recommendations=5)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
    
    def test_recommend_for_user(self, recommender):
        """测试为用户生成推荐"""
        recommender.record_interaction("user_001", "finance-pro", "download")
        
        # 测试不同策略
        for strategy in ["hybrid", "collaborative", "content", "popular"]:
            recommendations = recommender.recommend_for_user(
                "user_001", 
                n_recommendations=3,
                strategy=strategy
            )
            
            assert isinstance(recommendations, list)
            for rec in recommendations:
                assert "name" in rec
                assert "recommend_score" in rec
                assert "recommend_reason" in rec
    
    def test_get_user_profile(self, recommender):
        """测试获取用户画像"""
        # 新用户
        profile = recommender.get_user_profile("new_user")
        assert profile["user_id"] == "new_user"
        assert profile["total_interactions"] == 0
        assert profile["activity_level"] == "new"
        
        # 活跃用户
        recommender.record_interaction("active_user", "finance-pro", "download")
        recommender.record_interaction("active_user", "coding-pro", "download")
        recommender.record_interaction("active_user", "skill-cli", "rate", 5)
        
        profile = recommender.get_user_profile("active_user")
        assert profile["total_interactions"] == 3
        assert profile["favorite_category"] is not None
        assert len(profile["top_skills"]) > 0
    
    def test_get_trending_skills(self, recommender):
        """测试获取热门技能"""
        # 记录一些近期交互
        recommender.record_interaction("user_001", "finance-pro", "download")
        recommender.record_interaction("user_002", "finance-pro", "download")
        recommender.record_interaction("user_003", "coding-pro", "download")
        
        trending = recommender.get_trending_skills(days=7, n_skills=5)
        
        assert isinstance(trending, list)
        # 验证返回的技能包含下载次数
        for skill in trending:
            assert "recent_downloads" in skill
    
    def test_cosine_similarity(self, recommender):
        """测试余弦相似度计算"""
        vec1 = {"a": 1.0, "b": 2.0}
        vec2 = {"a": 1.0, "b": 2.0}
        vec3 = {"a": -1.0, "b": -2.0}
        
        # 相同向量相似度为1
        sim = recommender._cosine_similarity(vec1, vec2)
        assert abs(sim - 1.0) < 0.001
        
        # 相反向量相似度为-1
        sim = recommender._cosine_similarity(vec1, vec3)
        assert abs(sim - (-1.0)) < 0.001
        
        # 零向量
        sim = recommender._cosine_similarity({}, vec1)
        assert sim == 0.0
    
    def test_export_import_model(self, recommender):
        """测试模型导出导入"""
        # 记录一些数据
        recommender.record_interaction("user_001", "finance-pro", "download")
        
        # 导出
        exported = recommender.export_model()
        
        assert "skills" in exported
        assert "user_interactions" in exported
        assert "user_skill_matrix" in exported
        
        # 创建新推荐器并导入
        new_recommender = SkillRecommender()
        new_recommender.import_model(exported)
        
        assert len(new_recommender.user_interactions) == len(recommender.user_interactions)
        assert "user_001" in new_recommender.user_skill_matrix
    
    def test_get_recommend_reason(self, recommender):
        """测试推荐理由生成"""
        # 记录用户行为
        recommender.record_interaction("user_001", "finance-pro", "download")
        
        reason = recommender._get_recommend_reason("user_001", "stock-portfolio-analyzer")
        assert isinstance(reason, str)
        assert len(reason) > 0
    
    def test_action_weights(self, recommender):
        """测试不同交互类型的权重"""
        view_weight = recommender._get_action_weight("view")
        download_weight = recommender._get_action_weight("download")
        install_weight = recommender._get_action_weight("install")
        rate_weight = recommender._get_action_weight("rate", 5)
        
        assert view_weight < download_weight
        assert download_weight < install_weight
        assert rate_weight > 0
    
    def test_similar_skills_same_category_bonus(self, recommender):
        """测试相似技能推荐中的类别匹配加分"""
        similar = recommender.get_similar_skills("finance-pro", n_similar=10)
        
        # 检查前几个推荐是否包含相同类别的技能
        finance_skills = [
            name for name, _ in similar 
            if recommender.skills[name].category == "finance"
        ]
        
        # 相同类别的技能应该排在前面
        if len(finance_skills) >= 2:
            assert finance_skills[0] == similar[0][0]


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_create_recommender(self):
        """测试创建推荐器函数"""
        recommender = create_recommender()
        assert isinstance(recommender, SkillRecommender)
        assert len(recommender.skills) > 0
    
    def test_get_recommendations(self):
        """测试快速获取推荐函数"""
        recommendations = get_recommendations("test_user", n=3)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 3
        
        for rec in recommendations:
            assert "name" in rec
            assert "recommend_score" in rec


class TestEdgeCases:
    """测试边界情况"""
    
    def test_empty_skills_data(self):
        """测试空技能数据 - 当传入空列表时，仍会加载默认技能"""
        # 注意：SkillRecommender 在 skills_data=[] 时会加载默认技能
        # 如果要测试真正的空数据，需要直接操作内部状态
        recommender = SkillRecommender(skills_data=[])
        # 默认会加载15个技能
        assert len(recommender.skills) == 15
    
    def test_nonexistent_skill(self):
        """测试不存在的技能"""
        recommender = SkillRecommender()
        similar = recommender.get_similar_skills("non-existent-skill")
        assert similar == []
    
    def test_zero_recommendations(self):
        """测试请求0个推荐"""
        recommender = SkillRecommender()
        recommendations = recommender.recommend_for_user("user_001", n_recommendations=0)
        assert recommendations == []
    
    def test_large_n_recommendations(self):
        """测试请求超过可用数量的推荐"""
        recommender = SkillRecommender()
        recommendations = recommender.recommend_for_user(
            "user_001", 
            n_recommendations=1000
        )
        # 应该返回所有可用技能
        assert len(recommendations) <= len(recommender.skills)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
