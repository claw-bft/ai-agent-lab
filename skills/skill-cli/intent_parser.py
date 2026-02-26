#!/usr/bin/env python3
"""
意图解析器 - Intent Parser
从自然语言中提取意图、实体和参数
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class IntentType(Enum):
    """意图类型枚举"""
    GET_QUOTE = "get_quote"           # 获取行情
    ANALYZE_STOCK = "analyze_stock"   # 分析股票
    SET_ALERT = "set_alert"           # 设置预警
    GENERATE_CODE = "generate_code"   # 生成代码
    REVIEW_CODE = "review_code"       # 代码审查
    RESEARCH = "research"             # 研究
    ANALYZE_DATA = "analyze_data"     # 数据分析
    CREATE_PRD = "create_prd"         # 创建PRD
    COMPETITOR_ANALYSIS = "competitor" # 竞品分析
    UNKNOWN = "unknown"               # 未知

@dataclass
class Intent:
    """意图数据结构"""
    type: IntentType
    confidence: float
    entities: Dict[str, Any]
    raw_text: str
    skill_hint: Optional[str] = None

class IntentParser:
    """自然语言意图解析器"""
    
    # 意图关键词映射
    INTENT_PATTERNS = {
        IntentType.GET_QUOTE: [
            r"查询[一下]?(.+?)(?:股票|股价|行情|价格|走势|怎么样)",
            r"(.+?)(?:股票|股价|行情|价格)[多少|怎么样]",
            r"看看(.+?)(?:的走势|的行情|的价格)",
            r"查[一下]?(.+?)(?:股价|行情)",
        ],
        IntentType.ANALYZE_STOCK: [
            r"分析[一下]?(.+?)(?:股票|走势|技术面)",
            r"(.+?)(?:技术面|基本面|财报)[分析|怎么样]",
            r"看看(.+?)(?:的技术面|的基本面|的财报)",
            r"诊断[一下]?(.+?)",
        ],
        IntentType.SET_ALERT: [
            r"(?:设置|添加|创建)[一个]?(?:价格)?预警",
            r"当(.+?)(?:达到|突破|跌破|涨到|跌到)(.+?)(?:时|就|请)?通知",
            r"(.+?)(?:价格|股价)(?:超过|低于|达到)(.+?)(?:时|就)提醒",
        ],
        IntentType.GENERATE_CODE: [
            r"(?:生成|写|创建)[一个]?(?:代码|程序|脚本|函数)",
            r"帮我写[一个]?(.+?)(?:代码|程序|脚本)",
            r"用(.+?)(?:语言|框架)?实现(.+)",
        ],
        IntentType.REVIEW_CODE: [
            r"(?:审查|检查|review)[一下]?(.+?)(?:代码|文件)",
            r"看看(.+?)(?:代码|实现|写得怎么样)",
            r"(.+?)(?:代码|文件)(?:有没有|是否有)(?:问题|bug|错误)",
        ],
        IntentType.RESEARCH: [
            r"(?:研究|调研|调查)[一下]?(.+)",
            r"了解[一下]?(.+)",
            r"(.+?)(?:行业|市场|趋势|发展)(?:怎么样|如何|研究)",
        ],
        IntentType.ANALYZE_DATA: [
            r"分析[一下]?(.+?)(?:数据|文件|表格)",
            r"(.+?)(?:数据|文件)(?:分析|统计|处理)",
            r"从(.+?)(?:中|里面)(?:提取|分析|统计)(.+)",
        ],
        IntentType.CREATE_PRD: [
            r"(?:写|创建|生成)[一个]?PRD",
            r"(?:产品需求|需求文档)(?:怎么写|创建|生成)",
            r"为(.+?)(?:功能|特性|需求)写PRD",
        ],
        IntentType.COMPETITOR_ANALYSIS: [
            r"(?:分析|调研)[一下]?(.+?)(?:竞品|竞争对手)",
            r"(.+?)(?:竞品|竞争对手)(?:分析|调研)",
            r"看看(.+?)(?:竞品|竞争对手)(?:怎么样|有哪些)",
        ],
    }
    
    # 股票代码模式
    STOCK_PATTERNS = [
        r"(\d{6})\.?(SH|SZ|BJ)?",  # 600519.SH, 000001.SZ
        r"([\u4e00-\u9fa5]{2,8})(?:股份|集团|科技|银行|证券|保险)?",  # 茅台, 中国平安
    ]
    
    # 技能提示词映射
    SKILL_HINTS = {
        "股票": "finance-pro",
        "股价": "finance-pro",
        "行情": "finance-pro",
        "代码": "coding-pro",
        "程序": "coding-pro",
        "PRD": "product-pro",
        "产品": "product-pro",
        "竞品": "product-pro",
        "研究": "research-pro",
        "调研": "research-pro",
        "分析": "research-pro",
    }
    
    def __init__(self):
        self.compiled_patterns = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """预编译正则表达式"""
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            self.compiled_patterns[intent_type] = [
                re.compile(p, re.IGNORECASE | re.UNICODE) for p in patterns
            ]
    
    def parse(self, text: str) -> Intent:
        """
        解析自然语言文本，提取意图
        
        Args:
            text: 用户输入的自然语言
            
        Returns:
            Intent对象
        """
        text = text.strip()
        
        # 尝试匹配所有意图模式
        best_match = None
        best_confidence = 0.0
        best_entities = {}
        
        for intent_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    # 计算置信度（基于匹配长度和位置）
                    confidence = self._calculate_confidence(match, text)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = intent_type
                        best_entities = self._extract_entities(match, intent_type, text)
        
        # 如果没有匹配到明确意图，尝试提取技能提示
        skill_hint = self._extract_skill_hint(text)
        
        if best_match is None:
            best_match = IntentType.UNKNOWN
            best_confidence = 0.3  # 基础置信度
        
        return Intent(
            type=best_match,
            confidence=best_confidence,
            entities=best_entities,
            raw_text=text,
            skill_hint=skill_hint
        )
    
    def _calculate_confidence(self, match: re.Match, text: str) -> float:
        """计算匹配置信度"""
        # 基于匹配长度比例
        match_ratio = len(match.group(0)) / len(text)
        # 基于匹配位置（越靠前越重要）
        position_weight = 1.0 - (match.start() / len(text)) * 0.3
        # 基础分
        base_score = 0.6
        
        return min(0.95, base_score + match_ratio * 0.3 + position_weight * 0.1)
    
    def _extract_entities(self, match: re.Match, intent_type: IntentType, text: str) -> Dict[str, Any]:
        """提取实体"""
        entities = {}
        groups = match.groups()
        
        if intent_type in [IntentType.GET_QUOTE, IntentType.ANALYZE_STOCK]:
            # 提取股票代码或名称
            entities["symbol"] = self._extract_stock_symbol(text) or (groups[0] if groups else None)
            
        elif intent_type == IntentType.SET_ALERT:
            if len(groups) >= 2:
                entities["symbol"] = self._extract_stock_symbol(groups[0]) or groups[0]
                entities["condition"] = groups[1]
                
        elif intent_type == IntentType.GENERATE_CODE:
            if len(groups) >= 2:
                entities["language"] = groups[0]
                entities["prompt"] = groups[1]
            elif groups:
                entities["prompt"] = groups[0]
                
        elif intent_type == IntentType.REVIEW_CODE:
            if groups:
                entities["path"] = groups[0]
                
        elif intent_type == IntentType.RESEARCH:
            if groups:
                entities["topic"] = groups[0]
                
        elif intent_type == IntentType.ANALYZE_DATA:
            if len(groups) >= 2:
                entities["file"] = groups[0]
                entities["query"] = groups[1]
            elif groups:
                entities["file"] = groups[0]
                
        elif intent_type == IntentType.CREATE_PRD:
            if groups:
                entities["feature"] = groups[0]
                
        elif intent_type == IntentType.COMPETITOR_ANALYSIS:
            if groups:
                entities["product"] = groups[0]
        
        return entities
    
    def _extract_stock_symbol(self, text: str) -> Optional[str]:
        """提取股票代码"""
        # 尝试匹配6位数字代码
        match = re.search(r'(\d{6})', text)
        if match:
            code = match.group(1)
            # 根据代码前缀判断交易所
            if code.startswith(('60', '68', '88', '89')):
                return f"{code}.SH"
            elif code.startswith(('00', '30', '82', '83')):
                return f"{code}.SZ"
            elif code.startswith(('43', '83', '87', '88')):
                return f"{code}.BJ"
            return code
        return None
    
    def _extract_skill_hint(self, text: str) -> Optional[str]:
        """从文本中提取技能提示"""
        for keyword, skill in self.SKILL_HINTS.items():
            if keyword in text:
                return skill
        return None
    
    def batch_parse(self, texts: List[str]) -> List[Intent]:
        """批量解析"""
        return [self.parse(t) for t in texts]


# 测试代码
if __name__ == "__main__":
    parser = IntentParser()
    
    test_cases = [
        "查询一下茅台股票",
        "分析一下600519的走势",
        "帮我写一个Python爬虫",
        "研究一下AI发展趋势",
        "分析竞品情况",
    ]
    
    for text in test_cases:
        intent = parser.parse(text)
        print(f"\n输入: {text}")
        print(f"意图: {intent.type.value} (置信度: {intent.confidence:.2f})")
        print(f"实体: {intent.entities}")
        print(f"技能提示: {intent.skill_hint}")
