"""
法律文档解析器 - 支持多种格式的法律文档解析
"""
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParsedDocument:
    """解析后的文档"""
    title: str
    doc_type: str  # contract, law, case, etc.
    content: str
    sections: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parties: List[str] = field(default_factory=list)  # 合同当事人
    key_dates: List[str] = field(default_factory=list)
    monetary_values: List[str] = field(default_factory=list)


class DocumentParser:
    """文档解析器"""
    
    def __init__(self):
        self.section_patterns = {
            "chinese_number": r'第[一二三四五六七八九十百千万\d]+[章节条款]',
            "arabic_number": r'^\s*\d+[\.、\s]',
            "parenthesis": r'^[（(]\d+[)）]',
        }
    
    def parse(self, text: str, doc_type: Optional[str] = None) -> ParsedDocument:
        """解析文档"""
        if not doc_type:
            doc_type = self._detect_doc_type(text)
        
        title = self._extract_title(text)
        sections = self._extract_sections(text)
        parties = self._extract_parties(text) if doc_type == "contract" else []
        key_dates = self._extract_dates(text)
        monetary_values = self._extract_monetary_values(text)
        
        metadata = {
            "word_count": len(text),
            "section_count": len(sections),
            "party_count": len(parties),
            "date_count": len(key_dates),
        }
        
        return ParsedDocument(
            title=title,
            doc_type=doc_type,
            content=text,
            sections=sections,
            metadata=metadata,
            parties=parties,
            key_dates=key_dates,
            monetary_values=monetary_values
        )
    
    def _detect_doc_type(self, text: str) -> str:
        """检测文档类型"""
        text_lower = text.lower()
        
        # 合同类型关键词
        contract_keywords = ["合同", "协议", "甲方", "乙方", "双方", "签订"]
        if any(kw in text_lower for kw in contract_keywords):
            return "contract"
        
        # 法律法规
        law_keywords = ["法", "条例", "规定", "办法", "第一章", "总则"]
        if any(kw in text_lower for kw in law_keywords):
            return "law"
        
        # 判决书/案例
        case_keywords = ["判决书", "裁定书", "原告", "被告", "本院认为", "判决如下"]
        if any(kw in text_lower for kw in case_keywords):
            return "case"
        
        return "general"
    
    def _extract_title(self, text: str) -> str:
        """提取标题"""
        lines = text.strip().split('\n')
        
        # 第一行通常是标题
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 100:
                # 排除常见的非标题行
                if not line.startswith(('甲方', '乙方', '鉴于', '根据', '第')):
                    return line
        
        return "未识别标题"
    
    def _extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """提取章节结构"""
        sections = []
        
        # 匹配"第X条"模式
        article_pattern = r'(第[一二三四五六七八九十\d]+条)[\s:：]*(.*?)(?=第[一二三四五六七八九十\d]+条|$)'
        matches = re.findall(article_pattern, text, re.DOTALL)
        
        for match in matches:
            article_num = match[0]
            content = match[1].strip()
            if content:
                sections.append({
                    "type": "article",
                    "number": article_num,
                    "title": "",
                    "content": content[:200] + "..." if len(content) > 200 else content
                })
        
        # 如果没有匹配到，尝试其他模式
        if not sections:
            # 尝试数字编号
            num_pattern = r'^[\s]*(\d+)[\.、\s]+(.+?)(?=^[\s]*\d+[\.、\s]+|$)'
            matches = re.findall(num_pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                sections.append({
                    "type": "numbered",
                    "number": match[0],
                    "title": match[1].strip()[:50],
                    "content": match[1].strip()[:200]
                })
        
        return sections
    
    def _extract_parties(self, text: str) -> List[str]:
        """提取合同当事人"""
        parties = []
        
        # 匹配甲方乙方
        patterns = [
            r'甲方[（(]?(.*?)[)）]?[:：]\s*(\S+)',
            r'乙方[（(]?(.*?)[)）]?[:：]\s*(\S+)',
            r'丙方[（(]?(.*?)[)）]?[:：]\s*(\S+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                party_name = match[1] if len(match) > 1 else match[0]
                if party_name and len(party_name) < 50:
                    parties.append(party_name)
        
        return parties
    
    def _extract_dates(self, text: str) -> List[str]:
        """提取日期"""
        dates = []
        
        # 匹配各种日期格式
        patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{4}/\d{2}/\d{2}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return list(set(dates))  # 去重
    
    def _extract_monetary_values(self, text: str) -> List[str]:
        """提取金额"""
        values = []
        
        # 匹配金额
        patterns = [
            r'(\d+[\.,]?\d*)\s*[万亿]?元',
            r'人民币\s*(\d+[\.,]?\d*)',
            r'¥\s*(\d+[\.,]?\d*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            values.extend(matches)
        
        return list(set(values))
    
    def extract_key_clauses(self, text: str, clause_types: Optional[List[str]] = None) -> Dict[str, str]:
        """提取关键条款"""
        if clause_types is None:
            clause_types = ["违约", "解除", "保密", "争议解决", "付款", "交付"]
        
        clauses = {}
        
        for clause_type in clause_types:
            # 查找包含关键词的段落
            pattern = rf'([^{{。}}]*{clause_type}[^{{。}}]*。{{1,3}})'
            matches = re.findall(pattern, text)
            if matches:
                clauses[clause_type] = matches[0][:200]
        
        return clauses
    
    def summarize(self, doc: ParsedDocument, max_length: int = 500) -> str:
        """生成文档摘要"""
        summary_parts = [
            f"文档类型: {doc.doc_type}",
            f"标题: {doc.title}",
        ]
        
        if doc.parties:
            summary_parts.append(f"当事人: {', '.join(doc.parties)}")
        
        summary_parts.append(f"章节数: {doc.metadata.get('section_count', 0)}")
        
        if doc.key_dates:
            summary_parts.append(f"涉及日期: {', '.join(doc.key_dates[:3])}")
        
        # 添加前几个章节的内容预览
        if doc.sections:
            summary_parts.append("\n内容预览:")
            for section in doc.sections[:3]:
                summary_parts.append(f"  {section['number']}: {section['content'][:80]}...")
        
        summary = "\n".join(summary_parts)
        return summary[:max_length]


if __name__ == "__main__":
    parser = DocumentParser()
    
    sample = """
    房屋租赁合同
    
    甲方（出租方）：张三
    乙方（承租方）：李四
    
    根据《中华人民共和国民法典》及相关法律规定，甲乙双方经协商一致，订立本合同。
    
    第一条 租赁物
    甲方将位于北京市朝阳区的房屋出租给乙方使用。
    
    第二条 租赁期限
    租赁期自2024年1月1日至2024年12月31日。
    
    第三条 租金
    月租金为5000元，按月支付。
    
    第四条 违约责任
    任何一方违约，应向守约方支付相当于一个月租金的违约金。
    """
    
    doc = parser.parse(sample)
    print(f"标题: {doc.title}")
    print(f"类型: {doc.doc_type}")
    print(f"当事人: {doc.parties}")
    print(f"日期: {doc.key_dates}")
    print(f"金额: {doc.monetary_values}")
    print(f"\n摘要:\n{parser.summarize(doc)}")
