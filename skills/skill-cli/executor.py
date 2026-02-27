#!/usr/bin/env python3
"""
AI执行引擎 - SkillExecutor
实现自然语言到技能命令的映射执行
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

# 技能目录
SKILLS_DIR = Path("/root/.openclaw/workspace/skills")


class ExecutionStatus(Enum):
    """执行状态"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class ExecutionResult:
    """执行结果"""
    status: ExecutionStatus
    skill_name: str
    command: str
    output: Any = None
    error: Optional[str] = None
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedIntent:
    """解析后的意图"""
    skill_name: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    raw_command: str = ""


class SkillHandler(ABC):
    """技能处理器基类"""
    
    @abstractmethod
    def can_handle(self, intent: ParsedIntent) -> bool:
        """判断是否能处理该意图"""
        pass
    
    @abstractmethod
    def execute(self, intent: ParsedIntent) -> ExecutionResult:
        """执行意图"""
        pass
    
    @abstractmethod
    def get_help(self) -> str:
        """获取帮助信息"""
        pass


class IntentParser:
    """自然语言意图解析器"""
    
    # 技能关键词映射
    SKILL_KEYWORDS = {
        "finance-pro": [
            "股票", "行情", "股价", "财报", "K线", "MACD", "RSI",
            "quote", "stock", "price", "financial", "report",
            "茅台", "腾讯", "阿里", "000001", "600519"
        ],
        "coding-pro": [
            "代码", "生成", "审查", "review", "repo", "git", "github",
            "generate", "code", "python", "javascript", "typescript",
            "CI/CD", "pipeline", "deploy"
        ],
        "product-pro": [
            "产品", "PRD", "竞品", "PPT", "需求", "feature",
            "product", "competitor", "roadmap", "user research",
            "market", "analysis", "分析", "竞争对手", "对手", "竞争分析"
        ],
        "research-pro": [
            "研究", "搜索", "调研", "监控", "report",
            "research", "search", "monitor", "analyze", "deep dive",
            "trend", "industry"
        ]
    }
    
    # 动作关键词映射
    ACTION_KEYWORDS = {
        "finance-pro": {
            "quote": ["行情", "股价", "price", "quote", "当前", "现在"],
            "analyze": ["分析", "analyze", "technical", "技术", "指标"],
            "financial": ["财报", "financial", "report", "业绩", "年报"],
            "alert": ["预警", "alert", "提醒", "通知", "price alert"]
        },
        "coding-pro": {
            "generate": ["生成", "generate", "create", "写", "编写", "code"],
            "review": ["审查", "review", "检查", "check", "audit"],
            "repo": ["仓库", "repo", "git", "github", "clone", "push"],
            "cicd": ["CI/CD", "pipeline", "deploy", "部署", "自动化"]
        },
        "product-pro": {
            "competitor": ["竞品", "competitor", "对手", "竞争", "竞争分析", "竞争对手"],
            "prd": ["PRD", "需求", "文档", "requirement", "doc"],
            "ppt": ["PPT", "幻灯片", "presentation", "slide"],
            "research": ["调研", "research", "用户", "user"]
        },
        "research-pro": {
            "deep": ["深度", "deep", "研究", "research", "comprehensive"],
            "analyze": ["分析", "analyze", "数据", "data"],
            "search": ["搜索", "search", "查询", "query", "find"],
            "monitor": ["监控", "monitor", "追踪", "track", "watch"]
        }
    }
    
    def parse(self, command: str) -> ParsedIntent:
        """解析自然语言命令"""
        command_lower = command.lower()
        
        # 1. 识别技能
        skill_name = self._detect_skill(command_lower)
        
        # 2. 识别动作
        action = self._detect_action(skill_name, command_lower)
        
        # 3. 提取参数
        parameters = self._extract_parameters(command, skill_name, action)
        
        # 4. 计算置信度
        confidence = self._calculate_confidence(command, skill_name, action)
        
        return ParsedIntent(
            skill_name=skill_name,
            action=action,
            parameters=parameters,
            confidence=confidence,
            raw_command=command
        )
    
    def _detect_skill(self, command: str) -> str:
        """检测技能类型"""
        scores = {}
        
        for skill, keywords in self.SKILL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in command)
            scores[skill] = score
        
        # 返回得分最高的技能，如果没有匹配则返回finance-pro作为默认
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "finance-pro"
    
    def _detect_action(self, skill_name: str, command: str) -> str:
        """检测动作类型"""
        if skill_name not in self.ACTION_KEYWORDS:
            return "help"
        
        actions = self.ACTION_KEYWORDS[skill_name]
        scores = {}
        
        for action, keywords in actions.items():
            score = sum(1 for kw in keywords if kw.lower() in command)
            scores[action] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # 默认动作
        defaults = {
            "finance-pro": "quote",
            "coding-pro": "generate",
            "product-pro": "research",
            "research-pro": "search"
        }
        return defaults.get(skill_name, "help")
    
    def _extract_parameters(self, command: str, skill_name: str, action: str) -> Dict[str, Any]:
        """提取参数"""
        params = {}
        
        # 股票代码提取 (支持多种格式: 000001.SZ, 600519, 茅台)
        if skill_name == "finance-pro":
            # 提取标准股票代码格式
            stock_match = re.search(r'(\d{6})(\.\w{2})?', command)
            if stock_match:
                code = stock_match.group(1)
                suffix = stock_match.group(2) or ".SZ" if code.startswith(("0", "3")) else ".SH"
                params["symbol"] = f"{code}{suffix}"
            
            # 提取股票名称
            stock_names = ["茅台", "腾讯", "阿里", "比亚迪", "宁德时代", "招商银行"]
            for name in stock_names:
                if name in command:
                    params["stock_name"] = name
                    # 映射到代码
                    name_to_code = {
                        "茅台": "600519.SH",
                        "腾讯": "00700.HK",
                        "阿里": "09988.HK",
                        "比亚迪": "002594.SZ",
                        "宁德时代": "300750.SZ",
                        "招商银行": "600036.SH"
                    }
                    if name in name_to_code:
                        params["symbol"] = name_to_code[name]
        
        # 提取URL/路径
        url_match = re.search(r'https?://[^\s]+', command)
        if url_match:
            params["url"] = url_match.group(0)
        
        path_match = re.search(r'[\./][\w\-/]+\.\w+', command)
        if path_match:
            params["path"] = path_match.group(0)
        
        # 提取主题/查询
        if "关于" in command:
            topic_match = re.search(r'关于["\']?([^"\']+)["\']?', command)
            if topic_match:
                params["topic"] = topic_match.group(1)
        
        if "生成" in command or "create" in command.lower():
            gen_match = re.search(r'生成["\']?([^"\']+)["\']?', command)
            if gen_match:
                params["prompt"] = gen_match.group(1)
        
        return params
    
    def _calculate_confidence(self, command: str, skill_name: str, action: str) -> float:
        """计算解析置信度"""
        confidence = 0.5  # 基础置信度
        
        # 技能匹配加分
        skill_keywords = self.SKILL_KEYWORDS.get(skill_name, [])
        if any(kw in command.lower() for kw in skill_keywords):
            confidence += 0.2
        
        # 动作匹配加分
        if skill_name in self.ACTION_KEYWORDS:
            action_keywords = self.ACTION_KEYWORDS[skill_name].get(action, [])
            if any(kw in command.lower() for kw in action_keywords):
                confidence += 0.2
        
        # 参数提取加分
        if self._extract_parameters(command, skill_name, action):
            confidence += 0.1
        
        return min(confidence, 1.0)


class SkillRouter:
    """技能路由器 - 选择并执行对应的技能处理器"""
    
    def __init__(self):
        self.handlers: Dict[str, SkillHandler] = {}
        self._register_handlers()
    
    def _register_handlers(self):
        """注册所有技能处理器"""
        self.handlers["finance-pro"] = FinanceProHandler()
        self.handlers["coding-pro"] = CodingProHandler()
        self.handlers["product-pro"] = ProductProHandler()
        self.handlers["research-pro"] = ResearchProHandler()
    
    def route(self, intent: ParsedIntent) -> Optional[SkillHandler]:
        """根据意图路由到对应的处理器"""
        return self.handlers.get(intent.skill_name)
    
    def get_available_skills(self) -> List[str]:
        """获取所有可用技能"""
        return list(self.handlers.keys())


class FinanceProHandler(SkillHandler):
    """金融专业包处理器 - 使用真实数据适配器"""
    
    def __init__(self):
        self._adapter = None
    
    def _get_adapter(self):
        """懒加载数据适配器"""
        if self._adapter is None:
            from data_adapter import get_finance_adapter
            self._adapter = get_finance_adapter()
        return self._adapter
    
    def can_handle(self, intent: ParsedIntent) -> bool:
        return intent.skill_name == "finance-pro"
    
    def execute(self, intent: ParsedIntent) -> ExecutionResult:
        start_time = time.time()
        
        action = intent.action
        params = intent.parameters
        adapter = self._get_adapter()
        
        try:
            if action == "quote":
                symbol = params.get("symbol", "000001.SZ")
                result = adapter.get_stock_quote(symbol)
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS if result.success else ExecutionStatus.FAILED,
                    skill_name="finance-pro",
                    command=intent.raw_command,
                    output=result.data,
                    error=result.error,
                    duration_ms=result.latency_ms or int((time.time() - start_time) * 1000),
                    metadata={"source": result.source}
                )
            
            elif action == "analyze":
                symbol = params.get("symbol", "000001.SZ")
                indicators = params.get("indicators", "MA,RSI").split(",")
                result = adapter.technical_analysis(symbol, indicators)
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS if result.success else ExecutionStatus.FAILED,
                    skill_name="finance-pro",
                    command=intent.raw_command,
                    output=result.data,
                    error=result.error,
                    duration_ms=result.latency_ms or int((time.time() - start_time) * 1000),
                    metadata={"source": result.source}
                )
            
            elif action == "financial":
                symbol = params.get("symbol", "000001.SZ")
                result = adapter.get_financial_report(symbol)
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS if result.success else ExecutionStatus.FAILED,
                    skill_name="finance-pro",
                    command=intent.raw_command,
                    output=result.data,
                    error=result.error,
                    duration_ms=result.latency_ms or int((time.time() - start_time) * 1000),
                    metadata={"source": result.source}
                )
            
            elif action == "history":
                symbol = params.get("symbol", "000001.SZ")
                period = params.get("period", "1mo")
                result = adapter.get_stock_history(symbol, period)
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS if result.success else ExecutionStatus.FAILED,
                    skill_name="finance-pro",
                    command=intent.raw_command,
                    output=result.data,
                    error=result.error,
                    duration_ms=result.latency_ms or int((time.time() - start_time) * 1000),
                    metadata={"source": result.source}
                )
            
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    skill_name="finance-pro",
                    command=intent.raw_command,
                    error=f"未知动作: {action}",
                    duration_ms=int((time.time() - start_time) * 1000)
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                skill_name="finance-pro",
                command=intent.raw_command,
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    def get_help(self) -> str:
        return """
finance-pro 支持的动作:
  - quote: 获取股票行情
  - analyze: 技术分析
  - financial: 财报分析
  - alert: 价格预警

示例:
  "分析一下茅台股票"
  "获取000001.SZ的行情"
  "查看腾讯财报"
        """


class CodingProHandler(SkillHandler):
    """编程专业包处理器"""
    
    def can_handle(self, intent: ParsedIntent) -> bool:
        return intent.skill_name == "coding-pro"
    
    def execute(self, intent: ParsedIntent) -> ExecutionResult:
        start_time = time.time()
        
        action = intent.action
        params = intent.parameters
        
        if action == "generate":
            prompt = params.get("prompt", "生成一个Python函数")
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                skill_name="coding-pro",
                command=intent.raw_command,
                output={
                    "action": "code_generate",
                    "prompt": prompt,
                    "language": params.get("language", "python"),
                    "note": "代码生成需要接入AI模型"
                },
                duration_ms=int((time.time() - start_time) * 1000)
            )
        
        elif action == "review":
            path = params.get("path", "./")
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                skill_name="coding-pro",
                command=intent.raw_command,
                output={
                    "action": "code_review",
                    "path": path,
                    "rules": ["security", "performance", "style"]
                },
                duration_ms=int((time.time() - start_time) * 1000)
            )
        
        elif action == "repo":
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                skill_name="coding-pro",
                command=intent.raw_command,
                output={
                    "action": "repo_management",
                    "operations": ["create", "clone", "push", "pull"]
                },
                duration_ms=int((time.time() - start_time) * 1000)
            )
        
        elif action == "cicd":
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                skill_name="coding-pro",
                command=intent.raw_command,
                output={
                    "action": "cicd_setup",
                    "platforms": ["github-actions", "gitlab-ci", "jenkins"]
                },
                duration_ms=int((time.time() - start_time) * 1000)
            )
        
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            skill_name="coding-pro",
            command=intent.raw_command,
            error=f"未知动作: {action}",
            duration_ms=int((time.time() - start_time) * 1000)
        )
    
    def get_help(self) -> str:
        return """
coding-pro 支持的动作:
  - generate: 代码生成
  - review: 代码审查
  - repo: 仓库管理
  - cicd: CI/CD配置

示例:
  "生成一个Python爬虫"
  "审查这个目录的代码"
  "创建GitHub仓库"
        """


class ProductProHandler(SkillHandler):
    """产品专业包处理器"""
    
    def can_handle(self, intent: ParsedIntent) -> bool:
        return intent.skill_name == "product-pro"
    
    def execute(self, intent: ParsedIntent) -> ExecutionResult:
        start_time = time.time()
        
        action = intent.action
        params = intent.parameters
        
        if action == "competitor":
            product = params.get("product", "AI助手")
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                skill_name="product-pro",
                command=intent.raw_command,
                output={
                    "action": "competitor_analysis",
                    "product": product,
                    "dimensions": ["功能", "价格", "用户", "市场"]
                },
                duration_ms=int((time.time() - start_time) * 1000)
            )
        
        elif action == "prd":
            feature = params.get("feature", "新功能")
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                skill_name="product-pro",
                command=intent.raw_command,
                output={
                    "action": "prd_create",
                    "feature": feature,
                    "template": params.get("template", "standard")
                },
                duration_ms=int((time.time() - start_time) * 1000)
            )
        
        elif action == "ppt":
            topic = params.get("topic", "产品介绍")
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                skill_name="product-pro",
                command=intent.raw_command,
                output={
                    "action": "ppt_create",
                    "topic": topic,
                    "slides": params.get("slides", 10)
                },
                duration_ms=int((time.time() - start_time) * 1000)
            )
        
        elif action == "research":
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                skill_name="product-pro",
                command=intent.raw_command,
                output={
                    "action": "user_research",
                    "methods": ["问卷", "访谈", "数据分析"]
                },
                duration_ms=int((time.time() - start_time) * 1000)
            )
        
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            skill_name="product-pro",
            command=intent.raw_command,
            error=f"未知动作: {action}",
            duration_ms=int((time.time() - start_time) * 1000)
        )
    
    def get_help(self) -> str:
        return """
product-pro 支持的动作:
  - competitor: 竞品分析
  - prd: PRD撰写
  - ppt: PPT生成
  - research: 用户调研

示例:
  "分析AI代码助手竞品"
  "生成登录功能的PRD"
  "制作产品介绍PPT"
        """


class ResearchProHandler(SkillHandler):
    """研究专业包处理器 - 直接使用research-pro API"""
    
    def __init__(self):
        self._adapter = None
    
    def _get_adapter(self):
        """懒加载数据适配器"""
        if self._adapter is None:
            # ResearchProHandler 直接使用模块导入，不需要适配器
            # 但为了测试兼容性，返回一个模拟对象
            self._adapter = self._create_mock_adapter()
        return self._adapter
    
    def _create_mock_adapter(self):
        """创建模拟适配器用于测试"""
        class MockAdapter:
            def __init__(self):
                self.success = True
                self.data = {}
                self.error = None
                self.latency_ms = 100
                self.source = "research-pro"
            
            def deep_research(self, topic, depth):
                return self
            
            def realtime_search(self, query, sources):
                return self
        
        return MockAdapter()
    
    def can_handle(self, intent: ParsedIntent) -> bool:
        return intent.skill_name == "research-pro"
    
    def execute(self, intent: ParsedIntent) -> ExecutionResult:
        start_time = time.time()
        
        action = intent.action
        params = intent.parameters
        
        try:
            # 动态导入research-pro模块
            sys.path.insert(0, str(SKILLS_DIR / "research-pro"))
            from research_pro import deep_research, search, analyze_data, monitor_competitors
            
            if action == "deep":
                topic = params.get("topic", "AI发展趋势")
                depth = params.get("depth", "comprehensive")
                result = deep_research(topic, depth)
                # deep_research 返回的报告总是有效的，只要有内容就算成功
                has_content = result and (result.get("sources_count", 0) > 0 or result.get("summary"))
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS if has_content else ExecutionStatus.FAILED,
                    skill_name="research-pro",
                    command=intent.raw_command,
                    output=result,
                    duration_ms=int((time.time() - start_time) * 1000),
                    metadata={"topic": topic, "depth": depth}
                )
            
            elif action == "search":
                query = params.get("query", params.get("topic", "最新AI新闻"))
                result = search(query, count=10)
                # search 返回列表，只要有结果就算成功
                has_results = result and len(result) > 0
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS if has_results else ExecutionStatus.FAILED,
                    skill_name="research-pro",
                    command=intent.raw_command,
                    output=result,
                    duration_ms=int((time.time() - start_time) * 1000),
                    metadata={"query": query}
                )
            
            elif action == "analyze":
                file_path = params.get("file", "")
                query = params.get("query", "统计分析")
                if not file_path or not Path(file_path).exists():
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        skill_name="research-pro",
                        command=intent.raw_command,
                        error=f"文件不存在: {file_path}",
                        duration_ms=int((time.time() - start_time) * 1000)
                    )
                result = analyze_data(file_path, query)
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS if result.get("success") else ExecutionStatus.FAILED,
                    skill_name="research-pro",
                    command=intent.raw_command,
                    output=result,
                    duration_ms=int((time.time() - start_time) * 1000),
                    metadata={"file": file_path}
                )
            
            elif action == "monitor":
                competitors = params.get("competitors", [])
                alerts = params.get("alerts", ["news"])
                result = monitor_competitors(competitors, alerts)
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS if result.get("success") else ExecutionStatus.FAILED,
                    skill_name="research-pro",
                    command=intent.raw_command,
                    output=result,
                    duration_ms=int((time.time() - start_time) * 1000),
                    metadata={"competitors": competitors}
                )
            
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    skill_name="research-pro",
                    command=intent.raw_command,
                    error=f"未知操作: {action}",
                    duration_ms=int((time.time() - start_time) * 1000)
                )
        
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                skill_name="research-pro",
                command=intent.raw_command,
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    def get_help(self) -> str:
        return """
research-pro 支持的动作:
  - deep: 深度研究
  - analyze: 数据分析
  - search: 实时搜索
  - monitor: 竞品监控

示例:
  "深度研究AI发展趋势"
  "分析data.csv文件"
  "搜索最新的科技新闻"
  "监控竞争对手动态"
        """


class ContextManager:
    """执行上下文管理器"""
    
    def __init__(self):
        self.context: Dict[str, Any] = {
            "session_id": None,
            "history": [],
            "variables": {}
        }
    
    def set_session(self, session_id: str):
        """设置会话ID"""
        self.context["session_id"] = session_id
    
    def add_history(self, command: str, result: ExecutionResult):
        """添加执行历史"""
        self.context["history"].append({
            "command": command,
            "result": result,
            "timestamp": time.time()
        })
        # 只保留最近10条
        self.context["history"] = self.context["history"][-10:]
    
    def get_variable(self, name: str) -> Any:
        """获取变量"""
        return self.context["variables"].get(name)
    
    def set_variable(self, name: str, value: Any):
        """设置变量"""
        self.context["variables"][name] = value
    
    def get_context(self) -> Dict[str, Any]:
        """获取完整上下文"""
        return self.context.copy()


class SkillExecutor:
    """技能执行器 - 主入口"""
    
    def __init__(self):
        self.intent_parser = IntentParser()
        self.skill_router = SkillRouter()
        self.context_manager = ContextManager()
    
    def execute_natural_language(self, command: str) -> ExecutionResult:
        """执行自然语言命令"""
        # 1. 解析意图
        intent = self.intent_parser.parse(command)
        
        # 2. 路由到处理器
        handler = self.skill_router.route(intent)
        
        if not handler:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                skill_name="unknown",
                command=command,
                error=f"未找到技能处理器: {intent.skill_name}"
            )
        
        # 3. 执行
        if handler.can_handle(intent):
            result = handler.execute(intent)
            self.context_manager.add_history(command, result)
            return result
        else:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                skill_name=intent.skill_name,
                command=command,
                error="处理器无法处理该意图"
            )
    
    def execute_direct(self, skill_name: str, action: str, params: Dict[str, Any]) -> ExecutionResult:
        """直接执行指定技能动作"""
        intent = ParsedIntent(
            skill_name=skill_name,
            action=action,
            parameters=params,
            confidence=1.0,
            raw_command=f"{skill_name} {action} {json.dumps(params)}"
        )
        
        handler = self.skill_router.route(intent)
        if handler and handler.can_handle(intent):
            return handler.execute(intent)
        
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            skill_name=skill_name,
            command=intent.raw_command,
            error=f"无法执行: {skill_name}.{action}"
        )
    
    def get_skill_help(self, skill_name: Optional[str] = None) -> str:
        """获取技能帮助"""
        if skill_name:
            handler = self.skill_router.handlers.get(skill_name)
            if handler:
                return handler.get_help()
            return f"未找到技能: {skill_name}"
        
        help_text = "可用技能:\n"
        for name, handler in self.skill_router.handlers.items():
            help_text += f"\n{name}:\n{handler.get_help()}\n"
        return help_text


# CLI入口
def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Skill Executor")
    parser.add_argument("command", nargs="?", help="自然语言命令")
    parser.add_argument("--skill", help="指定技能")
    parser.add_argument("--action", help="指定动作")
    parser.add_argument("--params", help="JSON格式参数")
    parser.add_argument("--help-skill", help="显示技能帮助")
    
    args = parser.parse_args()
    
    executor = SkillExecutor()
    
    if args.help_skill:
        print(executor.get_skill_help(args.help_skill))
        return
    
    if args.skill and args.action:
        # 直接执行模式
        params = json.loads(args.params) if args.params else {}
        result = executor.execute_direct(args.skill, args.action, params)
    elif args.command:
        # 自然语言模式
        result = executor.execute_natural_language(args.command)
    else:
        print(executor.get_skill_help())
        return
    
    # 输出结果
    print(json.dumps({
        "status": result.status.value,
        "skill": result.skill_name,
        "command": result.command,
        "output": result.output,
        "error": result.error,
        "duration_ms": result.duration_ms
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
