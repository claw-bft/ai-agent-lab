"""
法律咨询查询模块 - 提供基础法律知识和法规查询
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re


class LegalDomain(Enum):
    """法律领域"""
    CIVIL = "民法"
    CRIMINAL = "刑法"
    LABOR = "劳动法"
    CONTRACT = "合同法"
    PROPERTY = "物权法"
    COMPANY = "公司法"
    IP = "知识产权"
    FAMILY = "婚姻家庭"
    TORT = "侵权责任"


@dataclass
class LegalArticle:
    """法律条文"""
    law_name: str
    article_number: str
    content: str
    domain: LegalDomain
    effective_date: Optional[str] = None
    keywords: List[str] = None


@dataclass
class LegalAdvice:
    """法律咨询结果"""
    question: str
    domain: LegalDomain
    relevant_articles: List[LegalArticle]
    analysis: str
    suggestions: List[str]
    disclaimer: str = "本建议仅供参考，不构成正式法律意见"


class LegalKnowledgeBase:
    """法律知识库"""
    
    def __init__(self):
        self.articles = self._load_articles()
        self.qa_patterns = self._load_qa_patterns()
    
    def _load_articles(self) -> List[LegalArticle]:
        """加载基础法律条文"""
        return [
            LegalArticle(
                law_name="劳动合同法",
                article_number="第十条",
                content="建立劳动关系，应当订立书面劳动合同。",
                domain=LegalDomain.LABOR,
                keywords=["劳动合同", "书面", "建立劳动关系"]
            ),
            LegalArticle(
                law_name="劳动合同法",
                article_number="第十九条",
                content="劳动合同期限三个月以上不满一年的，试用期不得超过一个月；一年以上不满三年的，试用期不得超过二个月；三年以上固定期限和无固定期限的，试用期不得超过六个月。",
                domain=LegalDomain.LABOR,
                keywords=["试用期", "期限", "劳动合同"]
            ),
            LegalArticle(
                law_name="劳动合同法",
                article_number="第三十八条",
                content="用人单位有下列情形之一的，劳动者可以解除劳动合同：（一）未按照劳动合同约定提供劳动保护或者劳动条件的；（二）未及时足额支付劳动报酬的；（三）未依法为劳动者缴纳社会保险费的...",
                domain=LegalDomain.LABOR,
                keywords=["解除合同", "劳动者", "用人单位", "社保", "工资"]
            ),
            LegalArticle(
                law_name="劳动合同法",
                article_number="第四十七条",
                content="经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。",
                domain=LegalDomain.LABOR,
                keywords=["经济补偿", "赔偿金", "N+1", "离职补偿"]
            ),
            LegalArticle(
                law_name="民法典合同编",
                article_number="第五百七十七条",
                content="当事人一方不履行合同义务或者履行合同义务不符合约定的，应当承担继续履行、采取补救措施或者赔偿损失等违约责任。",
                domain=LegalDomain.CONTRACT,
                keywords=["违约", "违约责任", "赔偿"]
            ),
            LegalArticle(
                law_name="消费者权益保护法",
                article_number="第二十四条",
                content="经营者提供的商品或者服务不符合质量要求的，消费者可以依照国家规定、当事人约定退货。",
                domain=LegalDomain.CIVIL,
                keywords=["退货", "消费者权益", "质量问题"]
            ),
            LegalArticle(
                law_name="消费者权益保护法",
                article_number="第五十五条",
                content="经营者提供商品或者服务有欺诈行为的，应当按照消费者的要求增加赔偿其受到的损失，增加赔偿的金额为消费者购买商品的价款或者接受服务的费用的三倍。",
                domain=LegalDomain.CIVIL,
                keywords=["欺诈", "退一赔三", "赔偿", "消费者"]
            ),
        ]
    
    def _load_qa_patterns(self) -> Dict[str, Any]:
        """加载问答模式"""
        return {
            "试用期": {
                "domain": LegalDomain.LABOR,
                "keywords": ["试用期", "试用"],
                "answers": {
                    "最长多久": "根据劳动合同法第十九条，试用期最长不得超过六个月。",
                    "工资": "试用期工资不得低于本单位相同岗位最低档工资的80%，且不得低于当地最低工资标准。"
                }
            },
            "离职补偿": {
                "domain": LegalDomain.LABOR,
                "keywords": ["离职", "补偿", "N+1", "赔偿"],
                "answers": {
                    "N+1": "N指工作年限，每满一年支付一个月工资；+1指代通知金。",
                    "违法解除": "用人单位违法解除劳动合同，应按经济补偿标准的二倍支付赔偿金（即2N）。"
                }
            },
            "加班费": {
                "domain": LegalDomain.LABOR,
                "keywords": ["加班", "加班费"],
                "answers": {
                    "怎么算": "平日加班1.5倍工资，休息日加班2倍，法定节假日加班3倍。"
                }
            },
        }
    
    def search_articles(self, keyword: str, domain: Optional[LegalDomain] = None) -> List[LegalArticle]:
        """搜索法律条文"""
        results = []
        keyword_lower = keyword.lower()
        
        for article in self.articles:
            if domain and article.domain != domain:
                continue
            
            # 检查关键词匹配
            if article.keywords and any(kw in keyword_lower or keyword_lower in kw for kw in article.keywords):
                results.append(article)
            elif keyword_lower in article.content.lower() or keyword_lower in article.law_name.lower():
                results.append(article)
        
        return results
    
    def query(self, question: str) -> LegalAdvice:
        """回答法律咨询"""
        question_lower = question.lower()
        
        # 确定领域
        domain = self._detect_domain(question_lower)
        
        # 搜索相关条文
        relevant_articles = self.search_articles(question, domain)
        
        # 生成分析
        analysis = self._generate_analysis(question, relevant_articles)
        
        # 生成建议
        suggestions = self._generate_suggestions(question, domain)
        
        return LegalAdvice(
            question=question,
            domain=domain,
            relevant_articles=relevant_articles,
            analysis=analysis,
            suggestions=suggestions
        )
    
    def _detect_domain(self, question: str) -> LegalDomain:
        """检测法律领域"""
        domain_keywords = {
            LegalDomain.LABOR: ["劳动", "工作", "工资", "加班", "离职", "辞退", "社保", "试用期", "合同"],
            LegalDomain.CONTRACT: ["合同", "违约", "定金", "违约金", "履行"],
            LegalDomain.CIVIL: ["消费", "退货", "退款", "买家", "卖家"],
            LegalDomain.TORT: ["侵权", "伤害", "赔偿", "事故"],
            LegalDomain.FAMILY: ["离婚", "结婚", "抚养", "继承", "财产分割"],
        }
        
        scores = {domain: 0 for domain in LegalDomain}
        for domain, keywords in domain_keywords.items():
            scores[domain] = sum(1 for kw in keywords if kw in question)
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else LegalDomain.CIVIL
    
    def _generate_analysis(self, question: str, articles: List[LegalArticle]) -> str:
        """生成法律分析"""
        if not articles:
            return "根据您的问题，未找到完全匹配的法律条文。建议咨询专业律师获取针对性建议。"
        
        analysis = f"根据您的咨询，涉及以下法律规定：\n"
        for article in articles[:3]:  # 最多显示3条
            analysis += f"\n【{article.law_name}第{article.article_number}条】\n{article.content[:100]}..."
        
        return analysis
    
    def _generate_suggestions(self, question: str, domain: LegalDomain) -> List[str]:
        """生成建议"""
        suggestions = [
            "保留相关证据材料（合同、聊天记录、付款凭证等）",
            "与对方协商解决，协商不成再考虑法律途径",
            "咨询专业律师获取针对性法律意见"
        ]
        
        if domain == LegalDomain.LABOR:
            suggestions.extend([
                "可向当地劳动监察部门投诉",
                "劳动争议可申请劳动仲裁（免费）"
            ])
        elif domain == LegalDomain.CIVIL:
            suggestions.extend([
                "可向消费者协会投诉",
                "金额较小的纠纷可考虑小额诉讼程序"
            ])
        
        return suggestions


if __name__ == "__main__":
    kb = LegalKnowledgeBase()
    
    # 测试查询
    result = kb.query("试用期最长可以约定多久？")
    print(f"问题: {result.question}")
    print(f"领域: {result.domain.value}")
    print(f"分析: {result.analysis[:200]}...")
    print(f"建议: {result.suggestions}")
