#!/usr/bin/env python3
"""
技能路由器 - Skill Router
根据意图匹配最佳技能包
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

from intent_parser import Intent, IntentType

@dataclass
class SkillRoute:
    """路由结果"""
    skill_name: str
    command: str
    args: List[str]
    confidence: float
    reason: str

class SkillRouter:
    """技能路由器 - 将意图映射到具体技能命令"""
    
    # 意图到技能的映射
    INTENT_SKILL_MAP = {
        IntentType.GET_QUOTE: ("finance-pro", "quote"),
        IntentType.ANALYZE_STOCK: ("finance-pro", "analyze"),
        IntentType.SET_ALERT: ("finance-pro", "alert"),
        IntentType.GENERATE_CODE: ("coding-pro", "generate"),
        IntentType.REVIEW_CODE: ("coding-pro", "review"),
        IntentType.RESEARCH: ("research-pro", "deep"),
        IntentType.ANALYZE_DATA: ("research-pro", "analyze"),
        IntentType.CREATE_PRD: ("product-pro", "prd"),
        IntentType.COMPETITOR_ANALYSIS: ("product-pro", "competitor"),
    }
    
    # 技能别名映射
    SKILL_ALIASES = {
        "finance-pro": ["finance", "stock", "股票", "金融", "财务"],
        "coding-pro": ["coding", "code", "dev", "开发", "代码", "编程"],
        "product-pro": ["product", "pm", "产品", "prd"],
        "research-pro": ["research", "study", "研究", "调研", "分析"],
    }
    
    def __init__(self, skills_dir: str = "/root/.openclaw/workspace/skills"):
        self.skills_dir = Path(skills_dir)
        self.available_skills = self._discover_skills()
    
    def _discover_skills(self) -> List[str]:
        """发现可用技能"""
        if not self.skills_dir.exists():
            return []
        return [d.name for d in self.skills_dir.iterdir() 
                if d.is_dir() and (d / "SKILL.md").exists()]
    
    def route(self, intent: Intent) -> SkillRoute:
        """
        根据意图路由到具体技能
        
        Args:
            intent: 解析后的意图
            
        Returns:
            SkillRoute对象
        """
        # 1. 尝试直接映射
        if intent.type in self.INTENT_SKILL_MAP:
            skill, cmd = self.INTENT_SKILL_MAP[intent.type]
            args = self._build_args(intent, skill, cmd)
            
            return SkillRoute(
                skill_name=skill,
                command=cmd,
                args=args,
                confidence=intent.confidence * 0.9,
                reason=f"意图'{intent.type.value}'直接映射到{skill}/{cmd}"
            )
        
        # 2. 使用技能提示
        if intent.skill_hint and intent.skill_hint in self.available_skills:
            args = self._build_args_from_entities(intent.entities)
            return SkillRoute(
                skill_name=intent.skill_hint,
                command="help",
                args=args,
                confidence=intent.confidence * 0.7,
                reason=f"基于关键词匹配到技能'{intent.skill_hint}'"
            )
        
        # 3. 尝试智能匹配
        best_skill = self._smart_match(intent)
        if best_skill:
            return SkillRoute(
                skill_name=best_skill,
                command="help",
                args=[],
                confidence=0.4,
                reason=f"智能匹配到技能'{best_skill}'，建议查看帮助"
            )
        
        # 4. 默认返回research-pro作为通用分析工具
        return SkillRoute(
            skill_name="research-pro",
            command="deep",
            args=["--topic", intent.raw_text],
            confidence=0.3,
            reason="未匹配到明确技能，使用research-pro进行通用研究"
        )
    
    def _build_args(self, intent: Intent, skill: str, cmd: str) -> List[str]:
        """根据意图构建命令参数"""
        args = []
        entities = intent.entities
        
        if skill == "finance-pro":
            if cmd == "quote" and "symbol" in entities:
                args = ["--symbol", entities["symbol"]]
            elif cmd == "analyze" and "symbol" in entities:
                args = ["--symbol", entities["symbol"]]
                if "indicators" in entities:
                    args.extend(["--indicators", entities["indicators"]])
            elif cmd == "alert":
                if "symbol" in entities:
                    args = ["--symbol", entities["symbol"]]
                if "condition" in entities:
                    args.extend(["--condition", entities["condition"]])
                    
        elif skill == "coding-pro":
            if cmd == "generate":
                if "prompt" in entities:
                    args = ["--prompt", entities["prompt"]]
                if "language" in entities:
                    args.extend(["--language", entities["language"]])
            elif cmd == "review" and "path" in entities:
                args = ["--path", entities["path"]]
                
        elif skill == "research-pro":
            if cmd == "deep" and "topic" in entities:
                args = ["--topic", entities["topic"]]
            elif cmd == "analyze":
                if "file" in entities:
                    args = ["--file", entities["file"]]
                if "query" in entities:
                    args.extend(["--query", entities["query"]])
                    
        elif skill == "product-pro":
            if cmd == "prd" and "feature" in entities:
                args = ["--feature", entities["feature"]]
            elif cmd == "competitor" and "product" in entities:
                args = ["--product", entities["product"]]
        
        return args
    
    def _build_args_from_entities(self, entities: Dict[str, Any]) -> List[str]:
        """从实体构建参数"""
        args = []
        for key, value in entities.items():
            if value:
                args.extend([f"--{key}", str(value)])
        return args
    
    def _smart_match(self, intent: Intent) -> Optional[str]:
        """智能匹配技能"""
        text = intent.raw_text.lower()
        
        # 检查别名匹配
        for skill, aliases in self.SKILL_ALIASES.items():
            for alias in aliases:
                if alias.lower() in text:
                    return skill
        
        return None
    
    def get_skill_info(self, skill_name: str) -> Dict[str, Any]:
        """获取技能信息"""
        skill_path = self.skills_dir / skill_name / "SKILL.md"
        if not skill_path.exists():
            return {"exists": False}
        
        content = skill_path.read_text(encoding='utf-8')
        return {
            "exists": True,
            "name": skill_name,
            "size": len(content),
            "path": str(skill_path)
        }
    
    def list_available_skills(self) -> List[Dict[str, str]]:
        """列出所有可用技能"""
        skills = []
        for name in self.available_skills:
            info = self.get_skill_info(name)
            skills.append({
                "name": name,
                "path": info.get("path", "")
            })
        return skills


# 测试代码
if __name__ == "__main__":
    from intent_parser import IntentParser
    
    parser = IntentParser()
    router = SkillRouter()
    
    test_cases = [
        "查询一下茅台股票",
        "分析一下600519的走势",
        "帮我写一个Python爬虫",
        "研究一下AI发展趋势",
        "分析竞品情况",
    ]
    
    for text in test_cases:
        intent = parser.parse(text)
        route = router.route(intent)
        print(f"\n输入: {text}")
        print(f"意图: {intent.type.value}")
        print(f"路由: {route.skill_name} {route.command}")
        print(f"参数: {route.args}")
        print(f"置信度: {route.confidence:.2f}")
        print(f"原因: {route.reason}")
