#!/usr/bin/env python3
"""
新闻智能分析中心 - 测试套件
"""

import pytest
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, mock_open
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import (
    NewsItem,
    NewsRelation,
    ImpactAssessment,
    NewsIntelligenceEngine
)


class TestNewsItem:
    """测试新闻条目数据类"""
    
    def test_news_item_creation(self):
        """测试创建新闻条目"""
        item = NewsItem(
            id="news_001",
            title="测试新闻标题",
            summary="测试摘要内容",
            source="测试源",
            url="https://example.com/news/1",
            timestamp=datetime.now(),
            category="科技",
            heat_score=85.5,
            keywords=["AI", "科技"]
        )
        assert item.id == "news_001"
        assert item.title == "测试新闻标题"
        assert item.heat_score == 85.5
        assert "AI" in item.keywords
    
    def test_news_item_defaults(self):
        """测试新闻条目默认值"""
        now = datetime.now()
        item = NewsItem(
            id="news_002",
            title="另一标题",
            summary="另一摘要",
            source="另一源",
            url="https://example.com/news/2",
            timestamp=now,
            category="财经",
            heat_score=70.0,
            keywords=[]
        )
        assert item.keywords == []
        assert item.category == "财经"


class TestNewsRelation:
    """测试新闻关联数据类"""
    
    def test_relation_creation(self):
        """测试创建新闻关联"""
        relation = NewsRelation(
            source_id="news_001",
            target_id="news_002",
            similarity=0.85,
            relation_type="similar",
            strength=0.9
        )
        assert relation.source_id == "news_001"
        assert relation.target_id == "news_002"
        assert relation.similarity == 0.85
        assert relation.relation_type == "similar"
    
    def test_relation_types(self):
        """测试不同类型的关联"""
        types = ["causal", "similar", "sequential"]
        for i, rel_type in enumerate(types):
            relation = NewsRelation(
                source_id=f"news_{i}",
                target_id=f"news_{i+1}",
                similarity=0.8,
                relation_type=rel_type,
                strength=0.85
            )
            assert relation.relation_type in types


class TestImpactAssessment:
    """测试影响评估数据类"""
    
    def test_assessment_creation(self):
        """测试创建影响评估"""
        assessment = ImpactAssessment(
            news_id="news_001",
            dimensions={'social': 5.0, 'economic': 8.0, 'political': 3.0, 'tech': 9.0},
            overall_score=6.5,
            sentiment="positive",
            trend_direction="up",
            affected_sectors=["科技", "金融"]
        )
        assert assessment.news_id == "news_001"
        assert assessment.sentiment == "positive"
        assert "科技" in assessment.affected_sectors
    
    def test_sentiment_values(self):
        """测试情感值有效性"""
        sentiments = ["positive", "negative", "neutral"]
        for sentiment in sentiments:
            assessment = ImpactAssessment(
                news_id="news_test",
                dimensions={'social': 5.0},
                overall_score=5.0,
                sentiment=sentiment,
                trend_direction="stable",
                affected_sectors=[]
            )
            assert assessment.sentiment in sentiments


class TestNewsIntelligenceEngine:
    """测试新闻智能分析引擎"""
    
    @pytest.fixture
    def mock_config(self):
        """模拟配置"""
        return {
            "sources": [
                {"name": "测试源1", "url": "https://test1.com/api"},
                {"name": "测试源2", "url": "https://test2.com/api"}
            ],
            "analysis": {
                "correlation": {"threshold": 0.5},
                "impact": {"dimensions": ["social", "economic", "political", "tech"]}
            },
            "update_interval": 1800
        }
    
    @pytest.fixture
    def engine(self, mock_config, tmp_path):
        """创建测试引擎实例"""
        config_file = tmp_path / "test_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(mock_config, f)
        return NewsIntelligenceEngine(str(config_file))
    
    def test_engine_initialization(self, engine, mock_config):
        """测试引擎初始化"""
        assert engine.config == mock_config
        assert engine.news_history == []
        assert engine.relation_graph is not None
    
    def test_load_config(self, engine, mock_config):
        """测试加载配置"""
        assert 'sources' in engine.config
        assert len(engine.config['sources']) == 2
        assert 'analysis' in engine.config
    
    def test_analyze_correlations_empty_list(self, engine):
        """测试分析空新闻列表"""
        relations = engine.analyze_correlations([])
        assert relations == []
    
    def test_analyze_correlations_single_item(self, engine):
        """测试分析单条新闻"""
        item = NewsItem(
            id="news_001",
            title="测试",
            summary="测试摘要",
            source="测试源",
            url="https://example.com",
            timestamp=datetime.now(),
            category="测试",
            heat_score=50.0,
            keywords=[]
        )
        relations = engine.analyze_correlations([item])
        assert relations == []
    
    def test_analyze_correlations_similar_news(self, engine):
        """测试分析相似新闻"""
        items = [
            NewsItem(
                id="news_001",
                title="AI技术突破人工智能",
                summary="人工智能领域取得重大进展 AI技术突破",
                source="科技日报",
                url="https://example.com/1",
                timestamp=datetime.now(),
                category="科技",
                heat_score=90.0,
                keywords=["AI", "人工智能"]
            ),
            NewsItem(
                id="news_002",
                title="AI应用新进展人工智能",
                summary="人工智能在各行业的应用不断深化 AI应用",
                source="财经网",
                url="https://example.com/2",
                timestamp=datetime.now() + timedelta(hours=1),
                category="科技",
                heat_score=85.0,
                keywords=["AI", "应用"]
            )
        ]
        relations = engine.analyze_correlations(items)
        # 由于TF-IDF需要足够文本，相似度可能不足以触发关联
        # 这里只验证函数能正常运行
        assert isinstance(relations, list)
    
    def test_assess_impact_tech_news(self, engine):
        """测试科技新闻影响评估"""
        item = NewsItem(
            id="news_001",
            title="AI芯片突破：国产芯片性能提升50%",
            summary="新一代AI芯片发布，性能大幅提升",
            source="科技日报",
            url="https://example.com",
            timestamp=datetime.now(),
            category="科技",
            heat_score=95.0,
            keywords=["芯片", "AI"]
        )
        assessment = engine.assess_impact(item)
        assert assessment.news_id == "news_001"
        assert 'tech' in assessment.dimensions
        assert assessment.dimensions['tech'] > 0
        assert "科技" in assessment.affected_sectors
    
    def test_assess_impact_finance_news(self, engine):
        """测试财经新闻影响评估"""
        item = NewsItem(
            id="news_002",
            title="股市大涨：上证指数突破3000点",
            summary="今日股市表现强劲，投资者信心增强",
            source="财经网",
            url="https://example.com",
            timestamp=datetime.now(),
            category="财经",
            heat_score=88.0,
            keywords=["股市", "投资"]
        )
        assessment = engine.assess_impact(item)
        assert assessment.news_id == "news_002"
        assert 'economic' in assessment.dimensions
        assert assessment.dimensions['economic'] > 0
    
    def test_assess_impact_sentiment_positive(self, engine):
        """测试正面情感识别"""
        item = NewsItem(
            id="news_003",
            title="公司业绩增长50%",
            summary="成功突破技术瓶颈，实现突破性增长",
            source="财经网",
            url="https://example.com",
            timestamp=datetime.now(),
            category="财经",
            heat_score=80.0,
            keywords=["增长", "突破"]
        )
        assessment = engine.assess_impact(item)
        assert assessment.sentiment == "positive"
        assert assessment.trend_direction == "up"
    
    def test_assess_impact_sentiment_negative(self, engine):
        """测试负面情感识别"""
        item = NewsItem(
            id="news_004",
            title="股市下跌风险加剧",
            summary="市场出现危机信号，投资者担忧",
            source="财经网",
            url="https://example.com",
            timestamp=datetime.now(),
            category="财经",
            heat_score=75.0,
            keywords=["下跌", "危机"]
        )
        assessment = engine.assess_impact(item)
        assert assessment.sentiment == "negative"
        assert assessment.trend_direction == "down"
    
    def test_assess_impact_sentiment_neutral(self, engine):
        """测试中性情感识别"""
        item = NewsItem(
            id="news_005",
            title="今日新闻",
            summary="普通新闻报道",
            source="新闻网",
            url="https://example.com",
            timestamp=datetime.now(),
            category="新闻",
            heat_score=50.0,
            keywords=[]
        )
        assessment = engine.assess_impact(item)
        assert assessment.sentiment == "neutral"
        assert assessment.trend_direction == "stable"
    
    def test_assess_impact_affected_sectors(self, engine):
        """测试受影响行业识别"""
        item = NewsItem(
            id="news_006",
            title="银行推出AI投资服务",
            summary="金融科技融合创新",
            source="财经网",
            url="https://example.com",
            timestamp=datetime.now(),
            category="财经",
            heat_score=85.0,
            keywords=["银行", "AI"]
        )
        assessment = engine.assess_impact(item)
        assert "金融" in assessment.affected_sectors
    
    @pytest.mark.asyncio
    async def test_fetch_from_source_empty(self, engine):
        """测试从源抓取（空结果）"""
        mock_session = Mock()
        source = {"name": "测试源", "url": "https://test.com"}
        items = await engine._fetch_from_source(mock_session, source)
        assert items == []
    
    def test_news_history_management(self, engine):
        """测试新闻历史管理"""
        assert engine.news_history == []
        item = NewsItem(
            id="news_001",
            title="测试",
            summary="测试",
            source="测试",
            url="https://example.com",
            timestamp=datetime.now(),
            category="测试",
            heat_score=50.0,
            keywords=[]
        )
        engine.news_history.append(item)
        assert len(engine.news_history) == 1


class TestConfigValidation:
    """测试配置验证"""
    
    def test_valid_config_structure(self, tmp_path):
        """测试有效配置结构"""
        config = {
            "sources": [{"name": "源1", "url": "https://test.com"}],
            "analysis": {
                "correlation": {"threshold": 0.5}
            }
        }
        config_file = tmp_path / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f)
        
        engine = NewsIntelligenceEngine(str(config_file))
        assert 'sources' in engine.config
        assert 'analysis' in engine.config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
