# Skill Recommender - AI驱动的技能推荐系统

基于用户使用模式和技能特征的智能推荐系统。

## 功能特性

- **协同过滤推荐**: 基于用户行为相似性推荐
- **内容推荐**: 基于技能标签和描述相似性
- **热门推荐**: 基于下载量和评分
- **混合推荐**: 综合多种推荐策略
- **实时学习**: 根据用户反馈持续优化

## 使用方法

```python
from skill_recommender import SkillRecommender

# 初始化推荐器
recommender = SkillRecommender()

# 获取个性化推荐
recommendations = recommender.recommend_for_user(
    user_id="user_123",
    n_recommendations=5
)

# 获取相似技能
similar_skills = recommender.get_similar_skills(
    skill_name="finance-pro",
    n_similar=3
)
```

## 推荐算法

1. **用户-技能交互矩阵**: 记录用户下载、评分行为
2. **TF-IDF向量化**: 技能描述和标签的文本特征
3. **余弦相似度**: 计算技能和用户的相似度
4. **加权混合**: 综合多种推荐策略的得分

## 测试

```bash
python -m pytest tests/ -v
```
