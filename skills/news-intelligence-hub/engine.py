#!/usr/bin/env python3
"""
热点新闻抓取与关联分析系统
每半小时自动抓取热点新闻，进行关联分析和影响评估
"""

import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

@dataclass
class NewsItem:
    """新闻条目"""
    id: str
    title: str
    summary: str
    source: str
    url: str
    timestamp: datetime
    category: str
    heat_score: float
    keywords: List[str]
    
@dataclass
class NewsRelation:
    """新闻关联"""
    source_id: str
    target_id: str
    similarity: float
    relation_type: str
    strength: float

@dataclass
class ImpactAssessment:
    """影响评估"""
    news_id: str
    dimensions: Dict[str, float]
    overall_score: float
    sentiment: str
    trend_direction: str
    affected_sectors: List[str]

class NewsIntelligenceEngine:
    """新闻智能分析引擎"""
    
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.news_history: List[NewsItem] = []
        self.relation_graph = nx.DiGraph()
        
    async def fetch_news(self) -> List[NewsItem]:
        """抓取热点新闻"""
        news_items = []
        
        async with aiohttp.ClientSession() as session:
            for source in self.config['sources']:
                try:
                    items = await self._fetch_from_source(session, source)
                    news_items.extend(items)
                except Exception as e:
                    print(f"Error fetching from {source['name']}: {e}")
                    
        seen = set()
        unique_items = []
        for item in sorted(news_items, key=lambda x: x.heat_score, reverse=True):
            if item.title not in seen:
                seen.add(item.title)
                unique_items.append(item)
                
        return unique_items[:50]
    
    async def _fetch_from_source(self, session: aiohttp.ClientSession, 
                                  source: Dict) -> List[NewsItem]:
        """从特定源抓取新闻"""
        items = []
        return items
    
    def analyze_correlations(self, news_items: List[NewsItem]) -> List[NewsRelation]:
        """分析新闻之间的关联"""
        if len(news_items) < 2:
            return []
            
        texts = [f"{item.title} {item.summary}" for item in news_items]
        vectorizer = TfidfVectorizer(max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        relations = []
        threshold = self.config['analysis']['correlation']['threshold']
        
        for i in range(len(news_items)):
            for j in range(i + 1, len(news_items)):
                sim = similarity_matrix[i][j]
                if sim > threshold:
                    time_diff = (news_items[j].timestamp - news_items[i].timestamp).total_seconds()
                    
                    if time_diff > 0 and sim > 0.9:
                        rel_type = 'causal'
                    elif abs(time_diff) < 3600:
                        rel_type = 'similar'
                    else:
                        rel_type = 'sequential'
                    
                    relations.append(NewsRelation(
                        source_id=news_items[i].id,
                        target_id=news_items[j].id,
                        similarity=sim,
                        relation_type=rel_type,
                        strength=min(sim * 1.2, 1.0)
                    ))
        
        return relations
    
    def assess_impact(self, news_item: NewsItem) -> ImpactAssessment:
        """评估新闻影响"""
        dimensions = {'social': 0.0, 'economic': 0.0, 'political': 0.0, 'tech': 0.0}
        
        keyword_mapping = {
            'social': ['社会', '民生', '教育', '医疗', '就业', '住房', '养老'],
            'economic': ['经济', '金融', '股市', '房地产', '消费', '投资', '贸易'],
            'political': ['政策', '政府', '法规', '国际', '外交', '军事'],
            'tech': ['科技', 'AI', '人工智能', '芯片', '互联网', '新能源']
        }
        
        text = f"{news_item.title} {news_item.summary}"
        
        for dim, keywords in keyword_mapping.items():
            score = sum(1 for kw in keywords if kw in text)
            dimensions[dim] = min(score * 2, 10)
        
        overall = np.mean(list(dimensions.values())) * (news_item.heat_score / 100)
        
        positive_words = ['增长', '上涨', '突破', '成功', '利好', '创新']
        negative_words = ['下降', '下跌', '危机', '失败', '风险', '问题']
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            sentiment = 'positive'
        elif neg_count > pos_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        sectors = []
        sector_keywords = {
            '科技': ['AI', '芯片', '互联网', '软件'],
            '金融': ['银行', '保险', '证券', '投资'],
            '房地产': ['房价', '楼市', '地产'],
            '消费': ['零售', '电商', '消费'],
            '制造': ['汽车', '工业', '制造']
        }
        
        for sector, kws in sector_keywords.items():
            if any(kw in text for kw in kws):
                sectors.append(sector)
        
        return ImpactAssessment(
            news_id=news_item.id,
            dimensions=dimensions,
            overall_score=overall,
            sentiment=sentiment,
            trend_direction='up' if sentiment == 'positive' else 'down' if sentiment == 'negative' else 'stable',
            affected_sectors=sectors
        )
