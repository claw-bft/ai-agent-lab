"""
性能基准测试 - Skill Recommender
"""
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skill_recommender import SkillRecommender, Skill, UserInteraction
from datetime import datetime


def benchmark_recommendation_performance():
    """基准测试：推荐性能"""
    print("=" * 60)
    print("技能推荐系统性能基准测试")
    print("=" * 60)
    
    # 初始化测试数据
    skills_data = [
        {
            "name": f"skill-{i}",
            "display_name": f"Skill {i}",
            "description": f"Description for skill {i}",
            "category": ["dev", "data", "ai"][i % 3],
            "tags": ["python", "automation", "ai"][:i % 3 + 1],
            "downloads": i * 100,
            "rating": 3.5 + (i % 20) / 10,
            "rating_count": i * 10,
            "version": "1.0.0",
            "author": f"author-{i}",
            "updated_at": datetime.now().isoformat()
        }
        for i in range(100)
    ]
    
    # 测试1: 初始化性能
    start = time.time()
    recommender = SkillRecommender(skills_data)
    init_time = time.time() - start
    print(f"\n1. 初始化性能 (100个技能)")
    print(f"   耗时: {init_time:.4f}s")
    print(f"   状态: {'✅ 通过' if init_time < 1.0 else '⚠️ 较慢'}")
    
    # 测试2: 协同过滤推荐性能
    interactions = []
    for i in range(50):
        for j in range(10):
            interactions.append(UserInteraction(
                user_id=f"user-{i}",
                skill_name=f"skill-{j}",
                action="download",
                timestamp=datetime.now()
            ))
    
    for interaction in interactions:
        recommender.record_interaction(
            user_id=interaction.user_id,
            skill_name=interaction.skill_name,
            action=interaction.action,
            rating=interaction.rating
        )
    
    start = time.time()
    result = recommender.recommend_collaborative("user-1", n_recommendations=5)
    cf_time = time.time() - start
    print(f"\n2. 协同过滤推荐性能")
    print(f"   耗时: {cf_time:.4f}s")
    print(f"   状态: {'✅ 通过' if cf_time < 0.1 else '⚠️ 较慢'}")
    
    # 测试3: 内容推荐性能
    start = time.time()
    result = recommender.get_similar_skills("skill-1", n_similar=5)
    content_time = time.time() - start
    print(f"\n3. 内容推荐性能")
    print(f"   耗时: {content_time:.4f}s")
    print(f"   状态: {'✅ 通过' if content_time < 0.1 else '⚠️ 较慢'}")
    
    # 测试4: 热门推荐性能
    start = time.time()
    result = recommender.recommend_popular(n_recommendations=10)
    popular_time = time.time() - start
    print(f"\n4. 热门推荐性能")
    print(f"   耗时: {popular_time:.4f}s")
    print(f"   状态: {'✅ 通过' if popular_time < 0.01 else '⚠️ 较慢'}")
    
    # 测试5: 混合推荐性能
    start = time.time()
    result = recommender.recommend_for_user("user-1", n_recommendations=5, strategy="hybrid")
    hybrid_time = time.time() - start
    print(f"\n5. 混合推荐性能")
    print(f"   耗时: {hybrid_time:.4f}s")
    print(f"   状态: {'✅ 通过' if hybrid_time < 0.2 else '⚠️ 较慢'}")
    
    # 测试6: 大规模数据性能
    print(f"\n6. 大规模数据性能测试")
    large_skills = [
        {
            "name": f"large-skill-{i}",
            "display_name": f"Large Skill {i}",
            "description": f"Description for large skill {i}",
            "category": ["dev", "data", "ai", "web", "cloud"][i % 5],
            "tags": ["python", "automation", "ai", "web", "api"][:i % 5 + 1],
            "downloads": i * 1000,
            "rating": 3.5 + (i % 20) / 10,
            "rating_count": i * 100,
            "version": "1.0.0",
            "author": f"author-{i}",
            "updated_at": datetime.now().isoformat()
        }
        for i in range(500)
    ]
    
    start = time.time()
    large_recommender = SkillRecommender(large_skills)
    large_init_time = time.time() - start
    print(f"   初始化500个技能: {large_init_time:.4f}s")
    
    start = time.time()
    result = large_recommender.recommend_popular(n_recommendations=10)
    large_popular_time = time.time() - start
    print(f"   热门推荐: {large_popular_time:.4f}s")
    print(f"   状态: {'✅ 通过' if large_init_time < 2.0 and large_popular_time < 0.1 else '⚠️ 较慢'}")
    
    print("\n" + "=" * 60)
    print("性能基准测试完成")
    print("=" * 60)
    
    return {
        "init_time": init_time,
        "cf_time": cf_time,
        "content_time": content_time,
        "popular_time": popular_time,
        "hybrid_time": hybrid_time,
        "large_init_time": large_init_time,
        "large_popular_time": large_popular_time
    }


if __name__ == "__main__":
    benchmark_recommendation_performance()
