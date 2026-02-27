#!/usr/bin/env python3
"""
技能包适配器 - 连接四个专业技能包到ACP协议
"""

import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 添加技能包路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'finance-pro'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'coding-pro'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'product-pro'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'research-pro'))

from agent_protocol import (
    CollaborationAgent, AgentRole, Message, MessageType,
    AgentRegistry, MessageBus, TaskOrchestrator
)


class FinanceProAdapter(CollaborationAgent):
    """Finance Pro 技能包适配器"""
    
    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        super().__init__(
            agent_id="finance-pro",
            role=AgentRole.SPECIALIST,
            capabilities=["finance", "stock", "quote", "analysis", "portfolio"],
            registry=registry,
            message_bus=message_bus
        )
        
        # 尝试导入finance-pro模块
        try:
            import finance_pro
            self._finance_module = finance_pro
            self._available = True
        except ImportError:
            self._finance_module = None
            self._available = False
    
    def _handle_task(self, message: Message):
        """处理Finance相关任务"""
        payload = message.payload
        task_type = payload.get("task_type", "")
        params = payload.get("parameters", {})
        task_id = payload.get("task_id", "")
        
        try:
            if task_type == "finance.quote":
                result = self._get_stock_quote(params.get("symbol", ""))
            elif task_type == "finance.analyze":
                result = self._analyze_stock(
                    params.get("symbol", ""),
                    params.get("indicators", ["MACD", "RSI"])
                )
            elif task_type == "finance.financial":
                result = self._get_financial_data(
                    params.get("symbol", ""),
                    params.get("quarter", "")
                )
            else:
                result = {"error": f"Unknown task type: {task_type}"}
            
            self.send_result(task_id, result)
            
        except Exception as e:
            self.send_error(task_id, str(e))
    
    def _handle_query(self, message: Message):
        """处理查询"""
        payload = message.payload
        query_type = payload.get("query_type", "")
        params = payload.get("parameters", {})
        
        if query_type == "finance.capabilities":
            self._message_bus.send(Message(
                msg_type=MessageType.RESPONSE,
                sender=self.agent_id,
                receiver=message.sender,
                correlation_id=message.correlation_id,
                payload={
                    "capabilities": self.capabilities,
                    "available": self._available
                }
            ))
    
    def _get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """获取股票行情"""
        if self._finance_module:
            try:
                analyzer = self._finance_module.StockAnalyzer(symbol)
                quote = analyzer.get_realtime_quote()
                return {
                    "symbol": symbol,
                    "quote": quote,
                    "timestamp": quote.get("time", ""),
                    "source": "akshare"
                }
            except Exception as e:
                return {"error": str(e), "symbol": symbol}
        
        # Mock数据
        return {
            "symbol": symbol,
            "quote": {
                "name": f"Stock-{symbol}",
                "price": 100.0,
                "change": 1.5,
                "change_percent": 1.52,
                "volume": 1000000
            },
            "timestamp": "2024-01-01T00:00:00",
            "source": "mock"
        }
    
    def _analyze_stock(self, symbol: str, indicators: List[str]) -> Dict[str, Any]:
        """分析股票技术指标"""
        return {
            "symbol": symbol,
            "indicators": indicators,
            "analysis": {
                "trend": "bullish",
                "strength": 0.75,
                "signals": ["MACD golden cross", "RSI neutral"]
            }
        }
    
    def _get_financial_data(self, symbol: str, quarter: str) -> Dict[str, Any]:
        """获取财务数据"""
        return {
            "symbol": symbol,
            "quarter": quarter,
            "financials": {
                "revenue": 1000000000,
                "profit": 200000000,
                "pe_ratio": 15.5,
                "pb_ratio": 2.3
            }
        }


class CodingProAdapter(CollaborationAgent):
    """Coding Pro 技能包适配器"""
    
    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        super().__init__(
            agent_id="coding-pro",
            role=AgentRole.SPECIALIST,
            capabilities=["coding", "generate", "review", "debug", "refactor"],
            registry=registry,
            message_bus=message_bus
        )
        
        try:
            import ai_code_generator
            self._coding_module = ai_code_generator
            self._available = True
        except ImportError:
            self._coding_module = None
            self._available = False
    
    def _handle_task(self, message: Message):
        """处理Coding相关任务"""
        payload = message.payload
        task_type = payload.get("task_type", "")
        params = payload.get("parameters", {})
        task_id = payload.get("task_id", "")
        
        try:
            if task_type == "coding.generate":
                result = self._generate_code(
                    params.get("prompt", ""),
                    params.get("language", "python"),
                    params.get("framework", "")
                )
            elif task_type == "coding.review":
                result = self._review_code(params.get("code", ""))
            elif task_type == "coding.debug":
                result = self._debug_code(
                    params.get("code", ""),
                    params.get("error", "")
                )
            else:
                result = {"error": f"Unknown task type: {task_type}"}
            
            self.send_result(task_id, result)
            
        except Exception as e:
            self.send_error(task_id, str(e))
    
    def _handle_query(self, message: Message):
        """处理查询"""
        payload = message.payload
        query_type = payload.get("query_type", "")
        
        if query_type == "coding.capabilities":
            self._message_bus.send(Message(
                msg_type=MessageType.RESPONSE,
                sender=self.agent_id,
                receiver=message.sender,
                correlation_id=message.correlation_id,
                payload={
                    "capabilities": self.capabilities,
                    "available": self._available,
                    "languages": ["python", "typescript", "javascript", "go", "rust"]
                }
            ))
    
    def _generate_code(self, prompt: str, language: str, framework: str) -> Dict[str, Any]:
        """生成代码"""
        if self._coding_module:
            try:
                generator = self._coding_module.AICodeGenerator()
                request = self._coding_module.CodeGenerationRequest(
                    prompt=prompt,
                    language=language,
                    framework=framework,
                    output_dir="./generated"
                )
                result = generator.generate(request)
                
                return {
                    "success": result.success,
                    "files": [{"path": f.path, "content": f.content[:500]} for f in result.files],
                    "language": language,
                    "framework": framework
                }
            except Exception as e:
                return {"error": str(e)}
        
        return {
            "success": True,
            "files": [{"path": "main.py", "content": f"# Generated code for: {prompt}"}],
            "language": language,
            "framework": framework,
            "source": "mock"
        }
    
    def _review_code(self, code: str) -> Dict[str, Any]:
        """代码审查"""
        return {
            "issues": [],
            "suggestions": ["Consider adding type hints", "Add docstrings"],
            "score": 85
        }
    
    def _debug_code(self, code: str, error: str) -> Dict[str, Any]:
        """调试代码"""
        return {
            "error_analysis": error,
            "suggested_fix": "Check variable initialization",
            "confidence": 0.8
        }


class ProductProAdapter(CollaborationAgent):
    """Product Pro 技能包适配器"""
    
    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        super().__init__(
            agent_id="product-pro",
            role=AgentRole.SPECIALIST,
            capabilities=["product", "competitor", "prd", "roadmap", "strategy"],
            registry=registry,
            message_bus=message_bus
        )
        
        try:
            import product_pro
            self._product_module = product_pro
            self._available = True
        except ImportError:
            self._product_module = None
            self._available = False
    
    def _handle_task(self, message: Message):
        """处理Product相关任务"""
        payload = message.payload
        task_type = payload.get("task_type", "")
        params = payload.get("parameters", {})
        task_id = payload.get("task_id", "")
        
        try:
            if task_type == "product.competitor":
                result = self._analyze_competitor(params.get("product", ""))
            elif task_type == "product.prd":
                result = self._create_prd(params.get("feature", ""))
            elif task_type == "product.roadmap":
                result = self._create_roadmap(params.get("product", ""))
            else:
                result = {"error": f"Unknown task type: {task_type}"}
            
            self.send_result(task_id, result)
            
        except Exception as e:
            self.send_error(task_id, str(e))
    
    def _handle_query(self, message: Message):
        """处理查询"""
        payload = message.payload
        query_type = payload.get("query_type", "")
        
        if query_type == "product.capabilities":
            self._message_bus.send(Message(
                msg_type=MessageType.RESPONSE,
                sender=self.agent_id,
                receiver=message.sender,
                correlation_id=message.correlation_id,
                payload={
                    "capabilities": self.capabilities,
                    "available": self._available
                }
            ))
    
    def _analyze_competitor(self, product: str) -> Dict[str, Any]:
        """竞品分析"""
        return {
            "product": product,
            "competitors": [
                {"name": "Competitor A", "strength": "Market leader", "weakness": "Expensive"},
                {"name": "Competitor B", "strength": "Innovative", "weakness": "Small user base"}
            ],
            "market_share": {"us": 15, "competitor_a": 45, "competitor_b": 20, "others": 20},
            "recommendations": ["Focus on pricing", "Improve UX"]
        }
    
    def _create_prd(self, feature: str) -> Dict[str, Any]:
        """创建PRD"""
        return {
            "feature": feature,
            "prd": {
                "overview": f"Product requirements for {feature}",
                "goals": ["Improve user experience", "Increase engagement"],
                "requirements": [
                    {"id": "REQ-001", "description": "User authentication", "priority": "high"},
                    {"id": "REQ-002", "description": "Data persistence", "priority": "high"}
                ],
                "timeline": "4 weeks"
            }
        }
    
    def _create_roadmap(self, product: str) -> Dict[str, Any]:
        """创建产品路线图"""
        return {
            "product": product,
            "roadmap": [
                {"quarter": "Q1", "features": ["MVP", "Core functionality"]},
                {"quarter": "Q2", "features": ["User feedback integration", "Performance optimization"]},
                {"quarter": "Q3", "features": ["Advanced features", "Enterprise support"]}
            ]
        }


class ResearchProAdapter(CollaborationAgent):
    """Research Pro 技能包适配器"""
    
    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        super().__init__(
            agent_id="research-pro",
            role=AgentRole.SPECIALIST,
            capabilities=["research", "search", "deep", "report", "synthesize"],
            registry=registry,
            message_bus=message_bus
        )
        
        try:
            import research_pro
            self._research_module = research_pro
            self._available = True
        except ImportError:
            self._research_module = None
            self._available = False
    
    def _handle_task(self, message: Message):
        """处理Research相关任务"""
        payload = message.payload
        task_type = payload.get("task_type", "")
        params = payload.get("parameters", {})
        task_id = payload.get("task_id", "")
        
        try:
            if task_type == "research.search":
                result = self._search(params.get("query", ""))
            elif task_type == "research.deep":
                result = self._deep_research(params.get("topic", ""))
            elif task_type == "research.report":
                result = self._generate_report(params.get("topic", ""))
            else:
                result = {"error": f"Unknown task type: {task_type}"}
            
            self.send_result(task_id, result)
            
        except Exception as e:
            self.send_error(task_id, str(e))
    
    def _handle_query(self, message: Message):
        """处理查询"""
        payload = message.payload
        query_type = payload.get("query_type", "")
        
        if query_type == "research.capabilities":
            self._message_bus.send(Message(
                msg_type=MessageType.RESPONSE,
                sender=self.agent_id,
                receiver=message.sender,
                correlation_id=message.correlation_id,
                payload={
                    "capabilities": self.capabilities,
                    "available": self._available
                }
            ))
    
    def _search(self, query: str) -> Dict[str, Any]:
        """搜索"""
        if self._research_module:
            try:
                results = self._research_module.search(query, limit=5)
                return {
                    "query": query,
                    "results": results,
                    "source": "tavily"
                }
            except Exception as e:
                return {"error": str(e)}
        
        return {
            "query": query,
            "results": [
                {"title": f"Result 1 for {query}", "url": "https://example.com/1", "snippet": "..."},
                {"title": f"Result 2 for {query}", "url": "https://example.com/2", "snippet": "..."}
            ],
            "source": "mock"
        }
    
    def _deep_research(self, topic: str) -> Dict[str, Any]:
        """深度研究"""
        return {
            "topic": topic,
            "summary": f"Deep research summary for {topic}",
            "key_findings": [
                "Finding 1: Market is growing at 20% CAGR",
                "Finding 2: Key players are consolidating"
            ],
            "sources": ["Industry report 2024", "Academic paper"],
            "confidence": 0.85
        }
    
    def _generate_report(self, topic: str) -> Dict[str, Any]:
        """生成报告"""
        return {
            "topic": topic,
            "report": {
                "title": f"Research Report: {topic}",
                "sections": ["Executive Summary", "Market Analysis", "Recommendations"],
                "generated_at": "2024-01-01T00:00:00"
            }
        }


def create_skill_agents():
    """创建所有技能包Agent"""
    from agent_protocol import create_collaboration_system
    
    # 创建基础系统
    master, registry, message_bus, orchestrator, aggregator = create_collaboration_system()
    
    # 创建技能包适配器
    agents = {
        "finance": FinanceProAdapter(registry, message_bus),
        "coding": CodingProAdapter(registry, message_bus),
        "product": ProductProAdapter(registry, message_bus),
        "research": ResearchProAdapter(registry, message_bus),
        "master": master
    }
    
    # 启动所有Agent
    for agent in agents.values():
        if agent != master:  # master已经在create_collaboration_system中启动
            agent.start()
    
    return agents, registry, message_bus, orchestrator


if __name__ == "__main__":
    print("=== Skill Adapters Test ===")
    
    agents, registry, bus, orchestrator = create_skill_agents()
    
    print(f"\nRegistered agents: {len(registry.list_agents())}")
    for agent in registry.list_agents():
        print(f"  - {agent.agent_id}: {agent.role.value} ({', '.join(agent.capabilities)})")
    
    # 测试任务创建
    print("\n=== Creating test task ===")
    task = orchestrator.create_task(
        task_type="finance.quote",
        description="查询茅台股票",
        parameters={"symbol": "600519.SH"}
    )
    print(f"Task created: {task.task_id}")
    
    # 自动分配
    assigned = orchestrator.auto_assign(task.task_id)
    print(f"Auto-assigned to: {assigned}")
    
    print("\n=== Test Complete ===")
