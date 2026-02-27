import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from contract_analyzer import ContractAnalyzer, RiskLevel
from legal_query import LegalKnowledgeBase, LegalDomain
from document_parser import DocumentParser


class TestContractAnalyzer(unittest.TestCase):
    """测试合同分析器"""
    
    def setUp(self):
        self.analyzer = ContractAnalyzer()
    
    def test_detect_contract_type_employment(self):
        text = "这是一份劳动合同，约定工资和试用期"
        result = self.analyzer.detect_contract_type(text)
        self.assertEqual(result, "employment")
    
    def test_detect_contract_type_sales(self):
        text = "买卖合同，标的物为货物，交付验收"
        result = self.analyzer.detect_contract_type(text)
        self.assertEqual(result, "sales")
    
    def test_detect_unfair_terms(self):
        text = "本合同最终解释权归甲方所有"
        findings = self.analyzer._detect_unfair_terms(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].category, "不公平条款")
    
    def test_detect_vague_terms(self):
        text = "甲方应在合理期限内完成支付"
        findings = self.analyzer._detect_vague_terms(text)
        self.assertTrue(len(findings) >= 1)
    
    def test_full_analysis(self):
        text = """
        劳动合同
        甲方：公司
        乙方：员工
        试用期为6个月
        最终解释权归甲方所有
        """
        result = self.analyzer.analyze(text)
        self.assertEqual(result.contract_type, "employment")
        self.assertTrue(len(result.risk_findings) > 0)


class TestLegalKnowledgeBase(unittest.TestCase):
    """测试法律知识库"""
    
    def setUp(self):
        self.kb = LegalKnowledgeBase()
    
    def test_search_articles(self):
        results = self.kb.search_articles("试用期")
        self.assertTrue(len(results) > 0)
        self.assertTrue(any("试用" in a.content for a in results))
    
    def test_detect_domain_labor(self):
        question = "加班费怎么计算？"
        domain = self.kb._detect_domain(question)
        self.assertEqual(domain, LegalDomain.LABOR)
    
    def test_query(self):
        result = self.kb.query("试用期最长多久？")
        self.assertEqual(result.question, "试用期最长多久？")
        self.assertTrue(len(result.suggestions) > 0)
        self.assertIn("仅供参考", result.disclaimer)


class TestDocumentParser(unittest.TestCase):
    """测试文档解析器"""
    
    def setUp(self):
        self.parser = DocumentParser()
    
    def test_detect_doc_type_contract(self):
        text = "甲方：张三，乙方：李四，签订合同"
        result = self.parser._detect_doc_type(text)
        self.assertEqual(result, "contract")
    
    def test_extract_parties(self):
        text = "甲方：科技有限公司 乙方：张三"
        parties = self.parser._extract_parties(text)
        self.assertTrue(len(parties) >= 1)
    
    def test_extract_dates(self):
        text = "合同日期2024年1月1日，到期2024年12月31日"
        dates = self.parser._extract_dates(text)
        self.assertTrue(len(dates) >= 2)
    
    def test_parse_full_document(self):
        text = """
        房屋租赁合同
        甲方（出租方）：张三
        乙方（承租方）：李四
        租赁期自2024年1月1日至2024年12月31日
        月租金5000元
        """
        doc = self.parser.parse(text)
        self.assertEqual(doc.doc_type, "contract")
        self.assertTrue("张三" in doc.parties or "李四" in doc.parties)


if __name__ == '__main__':
    unittest.main()
