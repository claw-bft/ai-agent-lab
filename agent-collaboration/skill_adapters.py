"""
技能包Agent适配器 - 将现有技能包接入协作协议

让 finance-pro, coding-pro, product-pro, research-pro 成为协作Agent
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_protocol import (
    CollaborationAgent, AgentRole, AgentMessage, MessageType,
    AgentRegistry, MessageBus, TaskOrchestrator
)
from typing import Dict, Any
import json

# Ensure typing imports are recognized
assert Dict or Any


class FinanceProAgent(CollaborationAgent):
    """Finance Pro 技能包 Agent"""

    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        super().__init__(
            agent_id="finance-pro",
            role=AgentRole.SPECIALIST,
            capabilities=["finance", "stock", "quote", "analysis", "portfolio"],
            registry=registry,
            message_bus=message_bus
        )
        self._load_finance_module()

    def _load_finance_module(self):
        """加载finance-pro模块"""
        try:
            sys.path.insert(0, "/root/.openclaw/workspace/skills/finance-pro")
            finance_pro = __import__("finance_pro")
            self.finance = finance_pro.FinancePro()
            self._available = True
        except Exception as e:
            print(f"FinancePro加载失败: {e}")
            self._available = False

    def _handle_task(self, message: AgentMessage):
        """处理金融任务"""
        if not self._available:
            self.send_error(
                message.payload.get("task_id"),
                "FinancePro模块不可用"
            )
            return

        task_type = message.payload.get("task_type", "")
        params = message.payload.get("parameters", {})
        task_id = message.payload.get("task_id")

        try:
            result = {}

            if "quote" in task_type:
                symbol = params.get("symbol", "")
                quote = self.finance.get_stock_quote(symbol)
                result = {"quote": quote}

            elif "analysis" in task_type:
                symbol = params.get("symbol", "")
                analysis = self.finance.analyze_stock(symbol)
                result = {"analysis": analysis}

            elif "portfolio" in task_type:
                symbols = params.get("symbols", [])
                portfolio = self.finance.analyze_portfolio(symbols)
                result = {"portfolio": portfolio}

            else:
                # 默认返回帮助信息
                result = {
                    "available_operations": [
                        "finance.quote - 获取股票报价",
                        "finance.analysis - 分析股票",
                        "finance.portfolio - 分析投资组合"
                    ]
                }

            self.send_result(task_id, result)

        except Exception as e:
            self.send_error(task_id, str(e))

    def _handle_query(self, message: AgentMessage):
        """处理查询"""
        query_type = message.payload.get("query_type", "")

        if query_type == "capabilities":
            response = AgentMessage(
                msg_type=MessageType.RESPONSE,
                sender=self.agent_id,
                receiver=message.sender,
                payload={
                    "capabilities": self.capabilities,
                    "available": self._available
                },
                correlation_id=message.correlation_id
            )
            self.message_bus.publish(response)


class CodingProAgent(CollaborationAgent):
    """Coding Pro 技能包 Agent"""

    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        super().__init__(
            agent_id="coding-pro",
            role=AgentRole.SPECIALIST,
            capabilities=["coding", "generate", "review", "debug", "refactor"],
            registry=registry,
            message_bus=message_bus
        )
        self._load_coding_module()

    def _load_coding_module(self):
        """加载coding-pro模块"""
        try:
            sys.path.insert(0, "/root/.openclaw/workspace/skills/coding-pro")
            ai_code_generator = __import__("ai_code_generator")
            self.coder = ai_code_generator.AICodeGenerator()
            self._available = True
        except Exception as e:
            print(f"CodingPro加载失败: {e}")
            self._available = False

    def _handle_task(self, message: AgentMessage):
        """处理编码任务"""
        if not self._available:
            self.send_error(
                message.payload.get("task_id"),
                "CodingPro模块不可用"
            )
            return

        task_type = message.payload.get("task_type", "")
        params = message.payload.get("parameters", {})
        task_id = message.payload.get("task_id")

        try:
            result = {}

            if "generate" in task_type:
                prompt = params.get("prompt", "")
                language = params.get("language", "python")
                code = self.coder.generate_code(prompt, language)
                result = {"code": code}

            elif "review" in task_type:
                code = params.get("code", "")
                review = self.coder.review_code(code)
                result = {"review": review}

            else:
                result = {
                    "available_operations": [
                        "coding.generate - 生成代码",
                        "coding.review - 代码审查",
                        "coding.debug - 调试代码",
                        "coding.refactor - 重构代码"
                    ]
                }

            self.send_result(task_id, result)

        except Exception as e:
            self.send_error(task_id, str(e))


class ProductProAgent(CollaborationAgent):
    """Product Pro 技能包 Agent"""

    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        super().__init__(
            agent_id="product-pro",
            role=AgentRole.SPECIALIST,
            capabilities=["product", "competitor", "prd", "roadmap", "strategy"],
            registry=registry,
            message_bus=message_bus
        )
        self._load_product_module()

    def _load_product_module(self):
        """加载product-pro模块"""
        try:
            sys.path.insert(0, "/root/.openclaw/workspace/skills/product-pro")
            product_manager = __import__("product_manager")
            self.pm = product_manager.ProductManager()
            self._available = True
        except Exception as e:
            print(f"ProductPro加载失败: {e}")
            self._available = False

    def _handle_task(self, message: AgentMessage):
        """处理产品任务"""
        if not self._available:
            self.send_error(
                message.payload.get("task_id"),
                "ProductPro模块不可用"
            )
            return

        task_type = message.payload.get("task_type", "")
        params = message.payload.get("parameters", {})
        task_id = message.payload.get("task_id")

        try:
            result = {}

            if "competitor" in task_type:
                product = params.get("product", "")
                analysis = self.pm.analyze_competitors(product)
                result = {"analysis": analysis}

            elif "prd" in task_type:
                feature = params.get("feature", "")
                prd = self.pm.generate_prd(feature)
                result = {"prd": prd}

            elif "roadmap" in task_type:
                goals = params.get("goals", [])
                roadmap = self.pm.create_roadmap(goals)
                result = {"roadmap": roadmap}

            else:
                result = {
                    "available_operations": [
                        "product.competitor - 竞品分析",
                        "product.prd - 生成PRD",
                        "product.roadmap - 创建路线图",
                        "product.strategy - 产品策略"
                    ]
                }

            self.send_result(task_id, result)

        except Exception as e:
            self.send_error(task_id, str(e))


class ResearchProAgent(CollaborationAgent):
    """Research Pro 技能包 Agent"""

    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        super().__init__(
            agent_id="research-pro",
            role=AgentRole.SPECIALIST,
            capabilities=["research", "search", "deep", "report", "synthesize"],
            registry=registry,
            message_bus=message_bus
        )
        self._load_research_module()

    def _load_research_module(self):
        """加载research-pro模块"""
        try:
            sys.path.insert(0, "/root/.openclaw/workspace/skills/research-pro")
            research_assistant = __import__("research_assistant")
            self.researcher = research_assistant.ResearchAssistant()
            self._available = True
        except Exception as e:
            print(f"ResearchPro加载失败: {e}")
            self._available = False

    def _handle_task(self, message: AgentMessage):
        """处理研究任务"""
        if not self._available:
            self.send_error(
                message.payload.get("task_id"),
                "ResearchPro模块不可用"
            )
            return

        task_type = message.payload.get("task_type", "")
        params = message.payload.get("parameters", {})
        task_id = message.payload.get("task_id")

        try:
            result = {}

            if "search" in task_type:
                query = params.get("query", "")
                results = self.researcher.search(query)
                result = {"results": results}

            elif "deep" in task_type:
                topic = params.get("topic", "")
                depth = params.get("depth", 3)
                report = self.researcher.deep_research(topic, depth)
                result = {"report": report}

            elif "synthesize" in task_type:
                sources = params.get("sources", [])
                synthesis = self.researcher.synthesize(sources)
                result = {"synthesis": synthesis}

            else:
                result = {
                    "available_operations": [
                        "research.search - 搜索信息",
                        "research.deep - 深度研究",
                        "research.report - 生成报告",
                        "research.synthesize - 综合信息"
                    ]
                }

            self.send_result(task_id, result)

        except Exception as e:
            self.send_error(task_id, str(e))


class MasterOrchestratorAgent(CollaborationAgent):
    """主编排Agent - 协调多个技能包完成复杂任务"""

    def __init__(self, registry: AgentRegistry, message_bus: MessageBus,
                 orchestrator: TaskOrchestrator):
        super().__init__(
            agent_id="master-orchestrator",
            role=AgentRole.ORCHESTRATOR,
            capabilities=["orchestrate", "coordinate", "plan"],
            registry=registry,
            message_bus=message_bus
        )
        self.orchestrator = orchestrator
        self._workflows = {}

    def create_stock_research_workflow(self, symbol: str) -> str:
        """创建股票研究工作流

        1. finance-pro 获取股票数据
        2. research-pro 研究行业背景
        3. product-pro 分析竞争格局 (如果是产品公司)
        4. 综合生成报告
        """
        workflow_id = f"stock-research-{symbol}"

        # 任务1: 获取股票报价
        task1 = self.orchestrator.create_task(
            task_type="finance.quote",
            description=f"获取{symbol}股票报价",
            parameters={"symbol": symbol},
            created_by=self.agent_id
        )

        # 任务2: 研究公司背景
        task2 = self.orchestrator.create_task(
            task_type="research.search",
            description=f"研究{symbol}公司背景",
            parameters={"query": f"{symbol} 公司分析 行业地位"},
            created_by=self.agent_id,
            dependencies=[task1.task_id]
        )

        # 任务3: 深度分析
        task3 = self.orchestrator.create_task(
            task_type="research.deep",
            description=f"深度研究{symbol}投资价值",
            parameters={"topic": f"{symbol} 投资分析", "depth": 2},
            created_by=self.agent_id,
            dependencies=[task2.task_id]
        )

        # 分配任务
        self.orchestrator.assign_task(task1.task_id, "finance-pro")
        self.orchestrator.assign_task(task2.task_id, "research-pro")
        self.orchestrator.assign_task(task3.task_id, "research-pro")

        self._workflows[workflow_id] = {
            "symbol": symbol,
            "tasks": [task1.task_id, task2.task_id, task3.task_id],
            "status": "running"
        }

        return workflow_id

    def create_product_development_workflow(self, product_idea: str) -> str:
        """创建产品开发工作流

        1. research-pro 市场调研
        2. product-pro 竞品分析 + PRD
        3. coding-pro 生成原型代码
        """
        workflow_id = f"product-dev-{product_idea[:20]}"

        # 任务1: 市场调研
        task1 = self.orchestrator.create_task(
            task_type="research.search",
            description=f"调研{product_idea}市场",
            parameters={"query": f"{product_idea} 市场分析 竞品"},
            created_by=self.agent_id
        )

        # 任务2: 竞品分析
        task2 = self.orchestrator.create_task(
            task_type="product.competitor",
            description=f"分析{product_idea}竞品",
            parameters={"product": product_idea},
            created_by=self.agent_id,
            dependencies=[task1.task_id]
        )

        # 任务3: 生成PRD
        task3 = self.orchestrator.create_task(
            task_type="product.prd",
            description=f"生成{product_idea}PRD",
            parameters={"feature": product_idea},
            created_by=self.agent_id,
            dependencies=[task2.task_id]
        )

        # 任务4: 生成原型代码
        task4 = self.orchestrator.create_task(
            task_type="coding.generate",
            description=f"生成{product_idea}原型",
            parameters={
                "prompt": f"基于{product_idea}生成最小可行产品代码",
                "language": "python"
            },
            created_by=self.agent_id,
            dependencies=[task3.task_id]
        )

        # 分配任务
        self.orchestrator.assign_task(task1.task_id, "research-pro")
        self.orchestrator.assign_task(task2.task_id, "product-pro")
        self.orchestrator.assign_task(task3.task_id, "product-pro")
        self.orchestrator.assign_task(task4.task_id, "coding-pro")

        self._workflows[workflow_id] = {
            "product": product_idea,
            "tasks": [task1.task_id, task2.task_id, task3.task_id, task4.task_id],
            "status": "running"
        }

        return workflow_id

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        if workflow_id not in self._workflows:
            return {"error": "工作流不存在"}

        workflow = self._workflows[workflow_id]
        task_statuses = []

        for task_id in workflow["tasks"]:
            status = self.orchestrator.get_task_status(task_id)
            task_statuses.append({
                "task_id": task_id,
                "status": status.name if status else "unknown"
            })

        all_completed = all(s["status"] == "COMPLETED" for s in task_statuses)
        any_failed = any(s["status"] == "FAILED" for s in task_statuses)

        return {
            "workflow_id": workflow_id,
            "overall_status": "completed" if all_completed else "failed" if any_failed else "running",
            "tasks": task_statuses
        }


def create_skill_agents() -> tuple:
    """创建所有技能包Agent"""
    from agent_protocol import create_collaboration_system

    registry, bus, orchestrator = create_collaboration_system()

    # 创建技能包Agent
    finance_agent = FinanceProAgent(registry, bus)
    coding_agent = CodingProAgent(registry, bus)
    product_agent = ProductProAgent(registry, bus)
    research_agent = ResearchProAgent(registry, bus)

    # 创建主编排Agent
    master = MasterOrchestratorAgent(registry, bus, orchestrator)

    agents = {
        "finance": finance_agent,
        "coding": coding_agent,
        "product": product_agent,
        "research": research_agent,
        "master": master
    }

    return agents, registry, bus, orchestrator


if __name__ == "__main__":
    # 测试
    agents, registry, bus, orchestrator = create_skill_agents()

    print("=== 技能包Agent协作系统 ===")
    print("\n已注册Agent:")
    for agent_info in registry.list_agents():
        print(f"  - {agent_info['agent_id']}: {agent_info['capabilities']}")

    print("\n=== 测试股票研究工作流 ===")
    workflow_id = agents["master"].create_stock_research_workflow("600519.SH")
    print(f"创建工作流: {workflow_id}")

    import time
    time.sleep(1)

    status = agents["master"].get_workflow_status(workflow_id)
    print(f"工作流状态: {status}")
