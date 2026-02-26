#!/usr/bin/env python3
"""
快速任务模板解析器
检测用户输入，匹配预定义模板
"""

import json
import re

# 模板定义
TEMPLATES = {
    'morning_report': {
        'keywords': ['早报', 'morning report', '日报'],
        'description': '生成股市早报',
        'handler': 'stock-portfolio-analyzer',
        'params': []
    },
    'stock_analysis': {
        'keywords': ['分析股票', 'analyze stock', '股票分析'],
        'description': '分析指定股票',
        'handler': 'stock-portfolio-analyzer',
        'params': ['symbol']
    },
    'deploy': {
        'keywords': ['部署', 'deploy', '上线'],
        'description': '部署项目到Vercel',
        'handler': 'vercel-deploy',
        'params': ['path']
    },
    'search': {
        'keywords': ['搜索', 'search', '查一下'],
        'description': '网络搜索',
        'handler': 'kimi_search',
        'params': ['query']
    },
    'code_review': {
        'keywords': ['审查代码', 'code review', 'review'],
        'description': '代码审查',
        'handler': 'coding-pro',
        'params': ['file_path']
    },
    'status': {
        'keywords': ['状态', 'status', '任务状态'],
        'description': '查看任务状态',
        'handler': 'internal',
        'params': []
    },
    'help': {
        'keywords': ['帮助', 'help', '怎么用'],
        'description': '显示帮助信息',
        'handler': 'internal',
        'params': []
    }
}

def match_template(user_input):
    """匹配用户输入到模板"""
    user_input = user_input.strip().lower()
    
    for template_id, template in TEMPLATES.items():
        for keyword in template['keywords']:
            if keyword.lower() in user_input:
                # 提取参数（关键词后的内容）
                params = {}
                keyword_pos = user_input.find(keyword.lower())
                if keyword_pos >= 0:
                    after_keyword = user_input[keyword_pos + len(keyword):].strip()
                    if template['params'] and after_keyword:
                        params[template['params'][0]] = after_keyword
                
                return {
                    'template_id': template_id,
                    'template': template,
                    'params': params,
                    'matched_keyword': keyword
                }
    
    return None

def get_help_text():
    """生成帮助文本"""
    lines = ['📋 快速任务模板\n']
    for template_id, template in TEMPLATES.items():
        keywords = ' / '.join(template['keywords'][:2])
        lines.append(f"• {keywords} - {template['description']}")
    return '\n'.join(lines)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
        result = match_template(user_input)
        
        if result:
            print(f"✅ 匹配模板: {result['template_id']}")
            print(f"   描述: {result['template']['description']}")
            print(f"   处理器: {result['template']['handler']}")
            print(f"   参数: {result['params']}")
        else:
            print("❌ 未匹配到模板")
            print(get_help_text())
    else:
        print(get_help_text())
