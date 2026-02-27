#!/usr/bin/env python3
"""
Legal Assistant CLI - 法律助手命令行工具
"""
import argparse
import sys
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from contract_analyzer import ContractAnalyzer, RiskLevel
from legal_query import LegalKnowledgeBase
from document_parser import DocumentParser


def format_risk_level(level: RiskLevel) -> str:
    """格式化风险等级"""
    colors = {
        RiskLevel.LOW: "🟢",
        RiskLevel.MEDIUM: "🟡",
        RiskLevel.HIGH: "🟠",
        RiskLevel.CRITICAL: "🔴"
    }
    return f"{colors.get(level, '⚪')} {level.value.upper()}"


def cmd_review(args):
    """审查合同命令"""
    if not args.file:
        print("错误: 请提供合同文件路径 (--file)")
        return 1
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"错误: 文件不存在: {file_path}")
        return 1
    
    # 读取文件
    try:
        text = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"错误: 无法读取文件: {e}")
        return 1
    
    # 解析文档
    parser = DocumentParser()
    doc = parser.parse(text)
    
    print(f"📄 文档分析: {doc.title}")
    print(f"   类型: {doc.doc_type}")
    print(f"   当事人: {', '.join(doc.parties) if doc.parties else '未识别'}")
    print()
    
    # 分析合同
    analyzer = ContractAnalyzer()
    contract_type = args.type or doc.doc_type
    result = analyzer.analyze(text, contract_type)
    
    print(f"🔍 合同审查结果")
    print(f"   合同类型: {result.contract_type}")
    print(f"   条款数量: {result.total_clauses}")
    print(f"   风险发现: {len(result.risk_findings)} 处")
    print()
    
    if result.risk_findings:
        print("⚠️  风险详情:")
        for i, finding in enumerate(result.risk_findings, 1):
            print(f"\n   [{i}] {format_risk_level(finding.level)} - {finding.category}")
            print(f"       描述: {finding.description}")
            if finding.clause_text:
                print(f"       原文: {finding.clause_text[:100]}...")
            print(f"       建议: {finding.suggestion}")
    else:
        print("✅ 未发现明显风险条款")
    
    print(f"\n📝 总结: {result.summary}")
    
    if result.recommendations:
        print("\n💡 建议:")
        for rec in result.recommendations:
            print(f"   • {rec}")
    
    # 输出JSON格式
    if args.json:
        output = {
            "contract_type": result.contract_type,
            "total_clauses": result.total_clauses,
            "risk_count": len(result.risk_findings),
            "findings": [
                {
                    "category": f.category,
                    "level": f.level.value,
                    "description": f.description,
                    "suggestion": f.suggestion
                }
                for f in result.risk_findings
            ],
            "summary": result.summary,
            "recommendations": result.recommendations
        }
        print("\n" + "="*50)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    
    return 0


def cmd_search(args):
    """法规查询命令"""
    kb = LegalKnowledgeBase()
    
    if args.keyword:
        print(f"🔍 搜索法规: {args.keyword}")
        articles = kb.search_articles(args.keyword)
        
        if articles:
            print(f"\n找到 {len(articles)} 条相关法规:\n")
            for article in articles:
                print(f"📋 {article.law_name} 第{article.article_number}条")
                print(f"   {article.content[:150]}...")
                print(f"   领域: {article.domain.value}")
                print()
        else:
            print("未找到相关法规")
    
    elif args.question:
        print(f"❓ 法律咨询: {args.question}")
        result = kb.query(args.question)
        
        print(f"\n📚 相关领域: {result.domain.value}")
        
        if result.relevant_articles:
            print(f"\n📋 相关法规:")
            for article in result.relevant_articles:
                print(f"   • {article.law_name} 第{article.article_number}条")
                print(f"     {article.content[:120]}...")
        
        print(f"\n📝 分析:\n{result.analysis}")
        
        print(f"\n💡 建议:")
        for suggestion in result.suggestions:
            print(f"   • {suggestion}")
        
        print(f"\n⚠️  {result.disclaimer}")
    
    else:
        print("错误: 请提供搜索关键词 (--keyword) 或问题 (--question)")
        return 1
    
    return 0


def cmd_parse(args):
    """解析文档命令"""
    if not args.file:
        print("错误: 请提供文档文件路径 (--file)")
        return 1
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"错误: 文件不存在: {file_path}")
        return 1
    
    try:
        text = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"错误: 无法读取文件: {e}")
        return 1
    
    parser = DocumentParser()
    doc = parser.parse(text)
    
    print(f"📄 文档解析结果")
    print(f"   标题: {doc.title}")
    print(f"   类型: {doc.doc_type}")
    print(f"   字数: {doc.metadata.get('word_count', 0)}")
    print()
    
    if doc.parties:
        print(f"👥 当事人: {', '.join(doc.parties)}")
    
    if doc.key_dates:
        print(f"📅 日期: {', '.join(doc.key_dates)}")
    
    if doc.monetary_values:
        print(f"💰 金额: {', '.join(doc.monetary_values[:5])}")
    
    print(f"\n📑 章节结构 ({len(doc.sections)} 个章节):")
    for section in doc.sections[:10]:  # 最多显示10个
        print(f"   {section['number']}: {section.get('title', section['content'][:50])}")
    
    if len(doc.sections) > 10:
        print(f"   ... 还有 {len(doc.sections) - 10} 个章节")
    
    # 提取关键条款
    key_clauses = parser.extract_key_clauses(text)
    if key_clauses:
        print(f"\n🔑 关键条款:")
        for clause_type, content in list(key_clauses.items())[:5]:
            print(f"   【{clause_type}】{content[:80]}...")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog='legal-assistant',
        description='法律助手 - 合同审查、法规查询、文档解析'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # review 命令
    review_parser = subparsers.add_parser('review', help='审查合同')
    review_parser.add_argument('--file', '-f', required=True, help='合同文件路径')
    review_parser.add_argument('--type', '-t', help='合同类型 (employment/sales/lease等)')
    review_parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='法规查询')
    search_parser.add_argument('--keyword', '-k', help='搜索关键词')
    search_parser.add_argument('--question', '-q', help='咨询问题')
    
    # parse 命令
    parse_parser = subparsers.add_parser('parse', help='解析文档')
    parse_parser.add_argument('--file', '-f', required=True, help='文档文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 执行对应命令
    commands = {
        'review': cmd_review,
        'search': cmd_search,
        'parse': cmd_parse,
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
