# Skill Recommender - AI驱动的技能推荐系统

基于用户使用模式和技能特征的智能推荐引擎，为ClawHub平台提供个性化技能包推荐服务。

## 功能特性

- **协同过滤推荐**: 基于用户行为相似性推荐相关技能
- **内容推荐**: 基于技能标签和描述相似性进行匹配
- **热门推荐**: 基于下载量和评分的趋势推荐
- **混合推荐**: 智能加权融合多种推荐策略
- **实时学习**: 根据用户交互反馈持续优化推荐效果
- **Web API集成**: 提供RESTful JSON接口供前端调用

## 快速开始

### 安装依赖

```bash
pip install numpy
```

### 基础使用

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

# 获取热门技能
trending = recommender.get_trending_skills(days=7, n_skills=5)
```

### Web API使用

```python
from api import RecommendationAPI

api = RecommendationAPI()

# 获取JSON格式推荐
result = api.get_recommendations("user_123", n=5, strategy="hybrid")

# 获取热门技能
result = api.get_trending(days=7, n=5)

# 获取用户画像
result = api.get_user_profile("user_123")
```

## 推荐算法详解

### 1. 协同过滤 (Collaborative Filtering)

基于用户-技能交互矩阵，找出行为相似的用户群体，推荐他们喜欢的技能。

```python
# 记录用户交互
recommender.record_interaction(
    user_id="user_123",
    skill_name="finance-pro",
    action="download",  # view, download, rate, install
    rating=5  # 可选，1-5评分
)

# 协同过滤推荐
recommendations = recommender.recommend_for_user(
    user_id="user_123",
    strategy="collaborative"
)
```

### 2. 内容推荐 (Content-Based)

使用TF-IDF向量化技能描述和标签，计算余弦相似度。

```python
# 基于内容推荐相似技能
similar = recommender.get_similar_skills("coding-pro", n_similar=5)
```

### 3. 热门推荐 (Popularity-Based)

基于下载量、评分和近期活跃度计算热门技能。

```python
# 获取7天内热门技能
trending = recommender.get_trending_skills(days=7, n_skills=10)
```

### 4. 混合推荐 (Hybrid)

智能加权融合多种策略，为新用户和老用户提供最佳推荐。

```python
# 混合策略推荐（默认）
recommendations = recommender.recommend_for_user(
    user_id="user_123",
    n_recommendations=5,
    strategy="hybrid"
)
```

## 用户画像分析

```python
# 获取用户画像
profile = recommender.get_user_profile("user_123")

# 返回示例:
# {
#     "activity_level": "high",  # low, medium, high
#     "total_interactions": 25,
#     "unique_skills": 8,
#     "favorite_category": "finance",
#     "avg_rating": 4.2
# }
```

## 模型持久化

```python
# 导出模型
recommender.export_model("recommender_model.json")

# 导入模型
recommender.import_model("recommender_model.json")
```

## 测试

运行测试套件:

```bash
python -m pytest tests/ -v
```

测试覆盖:
- 推荐算法正确性
- 边界条件处理
- API接口功能
- 模型导入导出

## 性能优化

- 使用numpy进行高效的矩阵运算
- 缓存技能向量避免重复计算
- 惰性加载用户交互数据

## 架构设计

```
skill-recommender/
├── skill_recommender.py  # 核心推荐引擎
├── api.py                # Web API接口
├── tests/                # 测试套件
├── README.md            # 使用文档
└── SKILL.md             # 技能包规范文档
```

## 贡献指南

欢迎提交Issue和PR来改进推荐算法或添加新功能。

## 许可证

MIT License
