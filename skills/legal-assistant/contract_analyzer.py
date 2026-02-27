"""
合同分析器 - 识别合同中的风险条款和潜在问题
"""
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskFinding:
    """风险发现"""
    category: str
    level: RiskLevel
    description: str
    clause_text: str
    suggestion: str
    line_number: Optional[int] = None


@dataclass
class ContractAnalysis:
    """合同分析结果"""
    contract_type: str
    total_clauses: int
    risk_findings: List[RiskFinding] = field(default_factory=list)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)


class ContractAnalyzer:
    """合同分析器"""
    
    # 风险条款模式库
    RISK_PATTERNS = {
        "unfair_terms": {
            "patterns": [
                r"最终解释权归.*所有",
                r".*有权随时修改.*无需另行通知",
                r".*不承担任何责任.*",
                r"违约金.*超过.*%",
            ],
            "level": RiskLevel.HIGH,
            "category": "不公平条款"
        },
        "vague_terms": {
            "patterns": [
                r"合理期限",
                r"适当补偿",
                r"必要时",
                r"根据实际情况",
                r"等.*情形",
            ],
            "level": RiskLevel.MEDIUM,
            "category": "模糊条款"
        },
        "liability_issues": {
            "patterns": [
                r"免责.*全部责任",
                r"不承担.*间接损失",
                r"赔偿上限.*不超过.*",
            ],
            "level": RiskLevel.HIGH,
            "category": "责任限制"
        }
    }
    
    # 合同类型检测关键词
    CONTRACT_TYPE_KEYWORDS = {
        "employment": ["劳动合同", "聘用", "工资", "社保", "试用期"],
        "service": ["服务合同", "委托服务", "技术服务", "咨询服务"],
        "sales": ["买卖合同", "购销", "货物", "交付", "验收"],
        "lease": ["租赁合同", "房屋", "租金", "押金", "租期"],
        "loan": ["借款合同", "贷款", "利息", "还款", "担保"],
        "nda": ["保密协议", "NDA", "机密信息", "保密义务"],
        "partnership": ["合伙协议", "合作", "股权", "分红", "出资"]
    }
    
    def __init__(self):
        self.risk_db = self._load_risk_database()
    
    def _load_risk_database(self) -> Dict[str, Any]:
        """加载风险数据库"""
        return {
            "employment": {
                "required_clauses": [
                    "工作内容", "工作地点", "工作时间", "劳动报酬",
                    "社会保险", "劳动保护", "试用期", "合同期限"
                ],
                "risk_keywords": {
                    "试用期超过6个月": RiskLevel.HIGH,
                    "竞业限制超过2年": RiskLevel.HIGH,
                    "工资低于最低工资": RiskLevel.CRITICAL,
                }
            },
            "sales": {
                "required_clauses": [
                    "标的物", "数量", "质量", "价款", "履行期限",
                    "履行地点", "验收标准", "违约责任"
                ],
                "risk_keywords": {
                    "验收期过短": RiskLevel.MEDIUM,
                    "付款方式不明确": RiskLevel.HIGH,
                    "质保期缺失": RiskLevel.MEDIUM,
                }
            },
            "lease": {
                "required_clauses": [
                    "租赁物", "租期", "租金", "支付方式", "维修责任",
                    "押金", "续租条件", "解除条件"
                ],
                "risk_keywords": {
                    "押金超过3个月": RiskLevel.MEDIUM,
                    "单方解除权不对等": RiskLevel.HIGH,
                }
            }
        }
    
    def detect_contract_type(self, text: str) -> str:
        """检测合同类型"""
        text_lower = text.lower()
        scores = {}
        
        for contract_type, keywords in self.CONTRACT_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[contract_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        return "general"
    
    def analyze(self, text: str, contract_type: Optional[str] = None) -> ContractAnalysis:
        """分析合同文本"""
        if not contract_type:
            contract_type = self.detect_contract_type(text)
        
        findings = []
        findings.extend(self._detect_unfair_terms(text))
        findings.extend(self._detect_vague_terms(text))
        findings.extend(self._detect_missing_clauses(text, contract_type))
        findings.extend(self._detect_liability_issues(text))
        
        summary = self._generate_summary(findings, contract_type)
        recommendations = self._generate_recommendations(findings)
        
        return ContractAnalysis(
            contract_type=contract_type,
            total_clauses=self._count_clauses(text),
            risk_findings=findings,
            summary=summary,
            recommendations=recommendations
        )
    
    def _detect_unfair_terms(self, text: str) -> List[RiskFinding]:
        """检测不公平条款"""
        findings = []
        patterns = self.RISK_PATTERNS["unfair_terms"]
        
        for pattern in patterns["patterns"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                findings.append(RiskFinding(
                    category=patterns["category"],
                    level=patterns["level"],
                    description="发现可能违反公平原则的单方优势条款",
                    clause_text=match.group(0),
                    suggestion="建议修改为双方协商确定或删除此条款"
                ))
        return findings
    
    def _detect_vague_terms(self, text: str) -> List[RiskFinding]:
        """检测模糊条款"""
        findings = []
        patterns = self.RISK_PATTERNS["vague_terms"]
        
        for pattern in patterns["patterns"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                findings.append(RiskFinding(
                    category=patterns["category"],
                    level=patterns["level"],
                    description=f"发现模糊表述: {match.group(0)}",
                    clause_text=match.group(0),
                    suggestion=f"建议明确定义具体标准"
                ))
        return findings
    
    def _detect_missing_clauses(self, text: str, contract_type: str) -> List[RiskFinding]:
        """检测缺失条款"""
        findings = []
        
        if contract_type in self.risk_db:
            required = self.risk_db[contract_type].get("required_clauses", [])
            for clause in required:
                if clause not in text:
                    findings.append(RiskFinding(
                        category="缺失条款",
                        level=RiskLevel.HIGH,
                        description=f"缺少必要的'{clause}'条款",
                        clause_text="",
                        suggestion=f"建议补充{clause}相关条款"
                    ))
        return findings
    
    def _detect_liability_issues(self, text: str) -> List[RiskFinding]:
        """检测责任限制问题"""
        findings = []
        patterns = self.RISK_PATTERNS["liability_issues"]
        
        for pattern in patterns["patterns"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                findings.append(RiskFinding(
                    category=patterns["category"],
                    level=patterns["level"],
                    description="发现可能不合理的责任限制条款",
                    clause_text=match.group(0),
                    suggestion="建议审查责任限制条款的合理性"
                ))
        return findings
    
    def _count_clauses(self, text: str) -> int:
        """统计条款数量"""
        # 简单统计：按第X条、X.、X、等模式
        patterns = [
            r'第[一二三四五六七八九十\d]+条',
            r'^\d+[、\.\s]',
            r'[\n\r]\d+[、\.\s]'
        ]
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text, re.MULTILINE))
        return max(count, 1)
    
    def _generate_summary(self, findings: List[RiskFinding], contract_type: str) -> str:
        """生成分析摘要"""
        if not findings:
            return f"合同类型: {contract_type}，未发现明显风险条款"
        
        risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in findings:
            risk_counts[f.level.value] += 1
        
        return f"合同类型: {contract_type}，发现 {len(findings)} 处风险：严重{risk_counts['critical']}处、高{risk_counts['high']}处、中{risk_counts['medium']}处、低{risk_counts['low']}处"
    
    def _generate_recommendations(self, findings: List[RiskFinding]) -> List[str]:
        """生成建议列表"""
        if not findings:
            return ["合同整体规范，建议保留备份并按时履行"]
        
        recommendations = []
        critical_high = [f for f in findings if f.level in (RiskLevel.CRITICAL, RiskLevel.HIGH)]
        
        if critical_high:
            recommendations.append(f"优先处理 {len(critical_high)} 处严重/高风险条款")
        
        categories = set(f.category for f in findings)
        for cat in categories:
            cat_findings = [f for f in findings if f.category == cat]
            recommendations.append(f"{cat}: 发现 {len(cat_findings)} 处问题需关注")
        
        recommendations.append("建议咨询专业律师进行最终审核")
        return recommendations


if __name__ == "__main__":
    # 测试示例
    sample_contract = """
    劳动合同
    
    甲方：某某公司
    乙方：张三
    
    第一条 工作内容
    乙方同意根据甲方工作需要，担任软件开发岗位。
    
    第二条 试用期
    试用期为6个月，自入职之日起计算。
    
    第三条 劳动报酬
    甲方每月支付乙方工资，具体金额根据考核确定。
    
    第四条 最终解释权
    本合同最终解释权归甲方所有。
    """
    
    analyzer = ContractAnalyzer()
    result = analyzer.analyze(sample_contract)
    print(f"合同类型: {result.contract_type}")
    print(f"条款数: {result.total_clauses}")
    print(f"风险发现: {len(result.risk_findings)}")
    for finding in result.risk_findings:
        print(f"  [{finding.level.value}] {finding.category}: {finding.description}")
