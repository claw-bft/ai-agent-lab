"""
研究Agent委托分析Agent的协作示例
演示如何使用ACP协议实现Agent间协作
"""
import asyncio
from typing import Dict, Any
from acp.core import ACPAgent, ACPRegistry, TaskResult, AgentStatus
from acp.transport import HTTPTransportAdapter, ACPTransport


class ResearchAgent(ACPAgent):
    """研究Agent - 负责收集信息并委托分析"""
    
    def __init__(self, registry: ACPRegistry):
        super().__init__(
            agent_id="research_agent_001",
            agent_type="research",
            capabilities=["web_search", "data_collection", "task_delegation"],
            endpoint="http://localhost:8081",
            registry=registry
        )
        
        # 注册自己的处理器
        self.register_handler("research_topic", self._handle_research_topic)
        self.transport: ACPTransport = None
    
    def _handle_research_topic(self, payload: Dict) -> Dict:
        """处理研究主题任务"""
        topic = payload.get("topic", "")
        print(f"[ResearchAgent] 开始研究主题: {topic}")
        
        # 模拟数据收集
        collected_data = {
            "topic": topic,
            "sources": ["source1", "source2", "source3"],
            "raw_data": f"关于{topic}的原始数据..."
        }
        
        return collected_data
    
    async def research_and_analyze(self, topic: str) -> Dict:
        """研究并委托分析"""
        print(f"\n=== 开始协作流程: {topic} ===\n")
        
        # 步骤1: 自己收集数据
        collected = self._handle_research_topic({"topic": topic})
        print(f"[ResearchAgent] 数据收集完成")
        
        # 步骤2: 查找分析Agent
        analysis_agents = self.find_agents_by_capability("data_analysis")
        if not analysis_agents:
            print("[ResearchAgent] 未找到分析Agent，返回原始数据")
            return collected
        
        analysis_agent = analysis_agents[0]
        print(f"[ResearchAgent] 找到分析Agent: {analysis_agent.agent_id}")
        
        # 步骤3: 委托分析任务
        result = await self.transport.delegate_task(
            to_agent_id=analysis_agent.agent_id,
            task_type="analyze_data",
            payload={
                "raw_data": collected,
                "analysis_type": "summary"
            },
            priority="high"
        )
        
        print(f"[ResearchAgent] 分析任务已委托")
        return {
            "research_result": collected,
            "delegation_result": result
        }


class AnalysisAgent(ACPAgent):
    """分析Agent - 负责数据分析"""
    
    def __init__(self, registry: ACPRegistry):
        super().__init__(
            agent_id="analysis_agent_001",
            agent_type="analysis",
            capabilities=["data_analysis", "report_generation", "insight_extraction"],
            endpoint="http://localhost:8082",
            registry=registry
        )
        
        # 注册自己的处理器
        self.register_handler("analyze_data", self._handle_analyze_data)
        self.register_handler("generate_report", self._handle_generate_report)
    
    def _handle_analyze_data(self, payload: Dict) -> Dict:
        """处理数据分析任务"""
        raw_data = payload.get("raw_data", {})
        analysis_type = payload.get("analysis_type", "summary")
        
        print(f"[AnalysisAgent] 开始分析数据，类型: {analysis_type}")
        
        # 模拟分析过程
        topic = raw_data.get("topic", "")
        sources = raw_data.get("sources", [])
        
        analysis_result = {
            "topic": topic,
            "key_insights": [
                f"关于{topic}的关键发现1",
                f"关于{topic}的关键发现2",
                f"基于{len(sources)}个来源的综合分析"
            ],
            "sentiment": "positive",
            "confidence": 0.85,
            "recommendations": [
                "建议1: 进一步深入研究",
                "建议2: 关注相关动态"
            ]
        }
        
        print(f"[AnalysisAgent] 分析完成")
        return analysis_result
    
    def _handle_generate_report(self, payload: Dict) -> Dict:
        """处理报告生成任务"""
        analysis_data = payload.get("analysis_data", {})
        
        print(f"[AnalysisAgent] 生成报告")
        
        report = {
            "title": f"{analysis_data.get('topic', '')} 分析报告",
            "generated_at": "2026-02-27T04:00:00Z",
            "sections": [
                {"title": "执行摘要", "content": "..."},
                {"title": "详细分析", "content": "..."},
                {"title": "结论与建议", "content": "..."}
            ]
        }
        
        return report


async def demo_collaboration():
    """演示Agent协作"""
    
    # 创建共享注册中心
    registry = ACPRegistry()
    
    # 创建Agent实例
    research_agent = ResearchAgent(registry)
    analysis_agent = AnalysisAgent(registry)
    
    print("=" * 60)
    print("Agent Collaboration Protocol (ACP) v0.2.0 演示")
    print("=" * 60)
    print(f"\n已注册Agent:")
    for agent in registry.list_agents():
        print(f"  - {agent.agent_id} ({agent.agent_type}): {agent.capabilities}")
    
    # 演示1: 直接任务处理
    print("\n" + "-" * 40)
    print("演示1: ResearchAgent直接处理研究任务")
    print("-" * 40)
    
    result = research_agent._handle_research_topic({"topic": "人工智能发展趋势"})
    print(f"结果: {result}")
    
    # 演示2: 任务委托
    print("\n" + "-" * 40)
    print("演示2: AnalysisAgent处理分析任务")
    print("-" * 40)
    
    analysis_result = analysis_agent._handle_analyze_data({
        "raw_data": result,
        "analysis_type": "summary"
    })
    print(f"分析结果: {analysis_result}")
    
    # 演示3: 消息传递
    print("\n" + "-" * 40)
    print("演示3: Agent间消息传递")
    print("-" * 40)
    
    # 创建任务请求消息
    task_msg = research_agent.create_task_request(
        to_agent="analysis_agent_001",
        task_type="analyze_data",
        payload={
            "raw_data": result,
            "analysis_type": "detailed"
        }
    )
    print(f"任务请求消息:\n{task_msg.to_json()}")
    
    # AnalysisAgent处理消息
    response = analysis_agent.handle_message(task_msg)
    if response:
        print(f"\n响应消息:\n{response.to_json()}")
    
    # 演示4: 能力发现
    print("\n" + "-" * 40)
    print("演示4: 能力发现")
    print("-" * 40)
    
    analysis_agents = research_agent.find_agents_by_capability("data_analysis")
    print(f"具有'data_analysis'能力的Agent: {[a.agent_id for a in analysis_agents]}")
    
    research_agents = research_agent.find_agents_by_capability("web_search")
    print(f"具有'web_search'能力的Agent: {[a.agent_id for a in research_agents]}")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo_collaboration())
