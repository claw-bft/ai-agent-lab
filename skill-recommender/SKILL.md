---
name: skill-recommender
description: AI驱动的技能推荐系统 - 基于用户使用模式和技能特征的智能推荐引擎
---

# Skill Recommender - AI技能推荐系统

基于协同过滤、内容分析和热门趋势的智能技能推荐引擎，为ClawHub用户提供个性化技能包推荐。

## 核心功能

### 1. 协同过滤推荐
- 基于用户行为相似性进行推荐
- 自动学习用户偏好模式
- 发现相似用户的兴趣

### 2. 内容推荐
- TF-IDF向量化技能特征
- 余弦相似度计算
- 基于技能标签和描述匹配

### 3. 热门推荐
- 基于下载量排序
- 基于评分高低排序
- 时间衰减算法

### 4. 混合推荐
- 加权融合多种策略
- 智能权重调整
- 冷启动处理

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用

```python
from skill_recommender import SkillRecommender

# 创建推荐器
recommender = SkillRecommender()

# 为用户获取推荐
recommendations = recommender.recommend_for_user(
    user_id="user_123",
    n_recommendations=5,
    strategy="hybrid"  # 可选: collaborative, content, popularity, hybrid
)

for rec in recommendations:
    print(f"{rec['name']}: {rec['reason']}")
```

### 记录用户行为

```python
from skill_recommender import UserInteraction
from datetime import datetime

# 记录用户下载行为
interaction = UserInteraction(
    user_id="user_123",
    skill_name="coding-pro",
    action="download",
    timestamp=datetime.now()
)
recommender.add_interaction(interaction)

# 记录用户评分
rating = UserInteraction(
    user_id="user_123",
    skill_name="coding-pro",
    action="rate",
    timestamp=datetime.now(),
    rating=5
)
recommender.add_interaction(rating)
```

## Web API 集成

### 启动API服务

```python
from api import RecommendationAPI

api = RecommendationAPI()

# 获取推荐 (返回JSON)
result = api.get_recommendations(
    user_id="user_123",
    n=5,
    strategy="hybrid"
)
print(result)
```

### API端点

| 方法 | 描述 | 参数 |
|------|------|------|
| `get_recommendations` | 获取用户推荐 | user_id, n, strategy |
| `get_similar_skills` | 获取相似技能 | skill_name, n |
| `get_trending` | 获取热门技能 | days, n |
| `get_user_profile` | 获取用户画像 | user_id |
| `record_interaction` | 记录交互 | user_id, skill_name, action |

### JavaScript集成示例

```javascript
// 获取推荐
fetch('/api/recommendations', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        user_id: 'user_123',
        n: 5,
        strategy: 'hybrid'
    })
})
.then(res => res.json())
.then(data => {
    console.log('推荐结果:', data);
});
```

## 推荐策略详解

### 协同过滤 (Collaborative Filtering)

```python
# 基于用户相似度
recommendations = recommender.recommend_for_user(
    user_id="user_123",
    strategy="collaborative"
)
```

**原理**: 找到与目标用户行为相似的其他用户，推荐他们喜欢的技能。

### 内容推荐 (Content-Based)

```python
# 基于技能特征相似度
recommendations = recommender.recommend_for_user(
    user_id="user_123",
    strategy="content"
)
```

**原理**: 分析用户历史喜欢的技能特征，推荐相似特征的技能。

### 热门推荐 (Popularity)

```python
# 基于全局热度
recommendations = recommender.recommend_for_user(
    user_id="user_123",
    strategy="popularity"
)
```

**原理**: 根据下载量、评分等综合热度排序。

### 混合推荐 (Hybrid)

```python
# 融合多种策略
recommendations = recommender.recommend_for_user(
    user_id="user_123",
    strategy="hybrid"
)
```

**原理**: 加权融合协同过滤、内容推荐和热门推荐的结果。

## 用户画像分析

```python
# 获取用户画像
profile = recommender.get_user_profile("user_123")

print(f"活跃度: {profile['activity_level']}")
print(f"类别偏好: {profile['category_preferences']}")
print(f"平均评分: {profile['avg_rating']}")
print(f"总交互次数: {profile['total_interactions']}")
```

## 模型持久化

```python
# 保存模型
recommender.save_model("recommender_model.json")

# 加载模型
recommender.load_model("recommender_model.json")
```

## 测试

```bash
# 运行测试
python -m pytest tests/test_recommender.py -v

# 运行特定测试
python -m pytest tests/test_recommender.py::TestSkillRecommender::test_recommend_collaborative -v
```

## 性能优化

- 使用缓存减少重复计算
- 异步加载技能数据
- 增量更新用户画像
- 批量处理交互记录

## 配置文件

```json
{
    "recommendation": {
        "default_strategy": "hybrid",
        "collaborative_weight": 0.4,
        "content_weight": 0.3,
        "popularity_weight": 0.3,
        "min_interactions": 3
    },
    "cache": {
        "enabled": true,
        "ttl_seconds": 300
    }
}
```

## 更新日志

### v1.0.0
- ✅ 协同过滤推荐算法
- ✅ 内容推荐算法
- ✅ 热门推荐算法
- ✅ 混合推荐策略
- ✅ Web API接口
- ✅ 用户画像分析
- ✅ 模型导入导出
- ✅ 22个单元测试

## 相关链接

- [ClawHub Web](../clawhub-web/README.md)
- [技能包评分系统](../clawhub-web/app.js)
- [项目主页](https://github.com/claw-bft/ai-agent-lab)
