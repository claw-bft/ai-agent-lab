#!/usr/bin/env python3
"""
Product Pro 核心实现
产品经理专业技能包 - 市场洞察、产品落地、数据驱动决策
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

def competitor_analysis(product: str, output_file: str) -> Dict[str, Any]:
    """
    竞品分析
    
    Args:
        product: 产品名称
        output_file: 输出文件路径
    """
    # 生成竞品分析框架
    analysis = {
        "product": product,
        "analysis_date": datetime.now().isoformat(),
        "sections": {
            "market_overview": {
                "title": "市场概览",
                "content": f"{product}所在市场的整体规模、增长趋势、主要玩家分析。"
            },
            "competitor_list": [
                {
                    "name": "主要竞品A",
                    "strengths": ["功能完善", "用户基础大"],
                    "weaknesses": ["价格较高", "学习曲线陡峭"],
                    "market_share": "35%"
                },
                {
                    "name": "主要竞品B",
                    "strengths": ["性价比高", "易用性好"],
                    "weaknesses": ["功能相对简单", "品牌知名度低"],
                    "market_share": "25%"
                },
                {
                    "name": "新兴竞品C",
                    "strengths": ["技术创新", "AI能力"],
                    "weaknesses": ["市场验证不足", "资源有限"],
                    "market_share": "10%"
                }
            ],
            "differentiation_opportunities": [
                "针对特定垂直场景的定制化功能",
                "更好的用户体验设计",
                "更具竞争力的定价策略",
                "更强的本地化支持"
            ],
            "recommendations": [
                "聚焦差异化功能，避免正面竞争",
                "建立用户社区，提升粘性",
                "持续监控竞品动态，快速响应"
            ]
        }
    }
    
    # 生成报告文件
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    report_content = generate_competitor_report(analysis)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return {
        "success": True,
        "product": product,
        "output_file": str(output_path),
        "competitors_analyzed": len(analysis["sections"]["competitor_list"]),
        "analysis": analysis
    }

def generate_competitor_report(analysis: Dict) -> str:
    """生成竞品分析报告"""
    sections = analysis["sections"]
    
    report = f"""# 竞品分析报告: {analysis['product']}

**分析日期**: {analysis['analysis_date']}

---

## 1. 市场概览

{sections['market_overview']['content']}

## 2. 主要竞品分析

"""
    
    for comp in sections['competitor_list']:
        report += f"""### {comp['name']}

- **市场份额**: {comp['market_share']}
- **优势**: {', '.join(comp['strengths'])}
- **劣势**: {', '.join(comp['weaknesses'])}

"""
    
    report += """## 3. 差异化机会

"""
    for i, opp in enumerate(sections['differentiation_opportunities'], 1):
        report += f"{i}. {opp}\n"
    
    report += """
## 4. 策略建议

"""
    for i, rec in enumerate(sections['recommendations'], 1):
        report += f"{i}. {rec}\n"
    
    return report

def create_prd(feature: str, template: str = "standard") -> Dict[str, Any]:
    """
    创建产品需求文档(PRD)
    
    Args:
        feature: 功能特性描述
        template: 模板类型
    """
    prd_templates = {
        "standard": generate_standard_prd,
        "minimal": generate_minimal_prd,
        "detailed": generate_detailed_prd
    }
    
    generator = prd_templates.get(template, generate_standard_prd)
    prd_content = generator(feature)
    
    # 保存PRD文件
    filename = f"PRD-{feature.replace(' ', '-').replace('/', '-')}.md"
    output_path = Path(filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prd_content)
    
    return {
        "success": True,
        "feature": feature,
        "template": template,
        "output_file": str(output_path),
        "content_preview": prd_content[:500] + "..."
    }

def generate_standard_prd(feature: str) -> str:
    """生成标准PRD"""
    return f"""# PRD: {feature}

## 1. 背景与目标

### 1.1 背景
描述为什么需要这个功能，解决了什么问题。

### 1.2 目标
- 目标1: 提升用户体验
- 目标2: 增加用户留存
- 目标3: 提高转化率

## 2. 需求范围

### 2.1 功能清单
1. 核心功能A
2. 核心功能B
3. 辅助功能C

### 2.2 非功能需求
- 性能: 页面加载时间 < 2秒
- 可用性: 99.9% SLA
- 安全: 符合数据保护法规

## 3. 用户故事

### 3.1 目标用户
- 用户类型A: 描述
- 用户类型B: 描述

### 3.2 用户场景
**场景1**: 作为[用户类型]，我希望[需求]，以便[价值]

## 4. 产品逻辑

### 4.1 流程图
```
[开始] -> [步骤1] -> [步骤2] -> [结束]
```

### 4.2 状态机
描述主要实体的状态流转。

## 5. 界面原型

### 5.1 页面结构
- 页面A: 功能描述
- 页面B: 功能描述

### 5.2 交互说明
详细描述关键交互逻辑。

## 6. 数据埋点

| 事件名 | 触发时机 | 属性 |
|--------|----------|------|
| event_1 | 用户操作时 | user_id, timestamp |

## 7. 发布计划

### 7.1 里程碑
- M1: 核心功能开发 (2周)
- M2: 测试与优化 (1周)
- M3: 灰度发布 (1周)

### 7.2 验收标准
- [ ] 功能完整实现
- [ ] 测试覆盖率 > 80%
- [ ] 性能指标达标

---

**文档版本**: 1.0  
**创建日期**: {datetime.now().strftime('%Y-%m-%d')}  
**负责人**: 产品经理
"""

def generate_minimal_prd(feature: str) -> str:
    """生成精简PRD"""
    return f"""# PRD: {feature}

## 问题
描述要解决的问题。

## 解决方案
简要描述解决方案。

## 验收标准
- [ ] 标准1
- [ ] 标准2

## 时间线
预计开发时间: X周
"""

def generate_detailed_prd(feature: str) -> str:
    """生成详细PRD"""
    return f"""# PRD: {feature}

## 1. 执行摘要

### 1.1 愿景
描述产品的长期愿景。

### 1.2 成功指标
- 指标1: 具体数值
- 指标2: 具体数值

## 2. 市场分析

### 2.1 目标市场
市场规模、增长趋势。

### 2.2 竞争格局
主要竞争对手分析。

## 3. 详细需求

### 3.1 功能需求
详细的功能规格说明。

### 3.2 技术需求
架构、性能、安全要求。

### 3.3 合规需求
法律、法规要求。

## 4. 设计规范

### 4.1 视觉设计
品牌、色彩、字体规范。

### 4.2 交互设计
详细的交互说明。

## 5. 实施计划

### 5.1 资源需求
人力、预算、时间。

### 5.2 风险评估
风险识别与缓解措施。

---
**创建日期**: {datetime.now().strftime('%Y-%m-%d')}
"""

def generate_ppt(topic: str, slides: int) -> Dict[str, Any]:
    """
    生成PPT内容
    
    Args:
        topic: PPT主题
        slides: 幻灯片数量
    """
    # 生成PPT大纲
    outline = generate_ppt_outline(topic, slides)
    
    # 生成每页内容
    slides_content = []
    for i, slide in enumerate(outline, 1):
        content = generate_slide_content(slide, i, slides)
        slides_content.append({
            "number": i,
            "title": slide["title"],
            "type": slide["type"],
            "content": content
        })
    
    # 保存为Markdown格式(可转换为PPT)
    filename = f"PPT-{topic.replace(' ', '-').replace('/', '-')}.md"
    output_path = Path(filename)
    
    ppt_content = generate_ppt_markdown(topic, slides_content)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ppt_content)
    
    return {
        "success": True,
        "topic": topic,
        "slides": slides,
        "output_file": str(output_path),
        "outline": outline
    }

def generate_ppt_outline(topic: str, slides: int) -> List[Dict]:
    """生成PPT大纲"""
    outline = [
        {"title": f"{topic}", "type": "title"},
        {"title": "目录", "type": "toc"},
        {"title": "背景与现状", "type": "content"},
        {"title": "问题与挑战", "type": "content"},
        {"title": "解决方案", "type": "content"},
        {"title": "产品规划", "type": "content"},
        {"title": "市场分析", "type": "content"},
        {"title": "竞争优势", "type": "content"},
        {"title": "实施计划", "type": "content"},
        {"title": "预期收益", "type": "content"},
        {"title": "总结与展望", "type": "content"},
        {"title": "Q&A", "type": "end"}
    ]
    
    # 根据要求的幻灯片数量调整
    if slides < len(outline):
        outline = outline[:slides]
    elif slides > len(outline):
        # 添加更多内容页
        for i in range(len(outline), slides):
            outline.append({"title": f"补充内容 {i-len(outline)+1}", "type": "content"})
    
    return outline[:slides]

def generate_slide_content(slide: Dict, num: int, total: int) -> str:
    """生成单页幻灯片内容"""
    slide_type = slide["type"]
    
    if slide_type == "title":
        return """副标题：产品规划与战略

演讲人：[姓名]
日期：[日期]"""
    
    elif slide_type == "toc":
        return """1. 背景与现状
2. 问题与挑战
3. 解决方案
4. 产品规划
5. 市场分析
6. 竞争优势
7. 实施计划
8. 预期收益"""
    
    elif slide_type == "content":
        return """• 要点1：详细说明
• 要点2：详细说明
• 要点3：详细说明

关键数据：
- 数据1: 数值
- 数据2: 数值"""
    
    elif slide_type == "end":
        return """感谢聆听

联系方式：[邮箱/电话]"""
    
    return "内容待填充"

def generate_ppt_markdown(topic: str, slides: List[Dict]) -> str:
    """生成PPT Markdown格式"""
    content = f"""---
marp: true
theme: default
paginate: true
---

"""
    
    for slide in slides:
        content += f"""# {slide['title']}

{slide['content']}

---

"""
    
    return content

def main():
    parser = argparse.ArgumentParser(description="Product Pro - 产品经理专业技能包")
    parser.add_argument("command", choices=["competitor", "prd", "ppt"])
    parser.add_argument("--product", help="产品名称")
    parser.add_argument("--feature", help="功能特性")
    parser.add_argument("--topic", help="PPT主题")
    parser.add_argument("--output", default="competitor-report.md", help="输出文件")
    parser.add_argument("--template", default="standard", choices=["standard", "minimal", "detailed"])
    parser.add_argument("--slides", type=int, default=10, help="幻灯片数量")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    
    args = parser.parse_args()
    
    if args.command == "competitor":
        if not args.product:
            print("✗ 错误: --product 是必需的")
            sys.exit(1)
        result = competitor_analysis(args.product, args.output)
    
    elif args.command == "prd":
        if not args.feature:
            print("✗ 错误: --feature 是必需的")
            sys.exit(1)
        result = create_prd(args.feature, args.template)
    
    elif args.command == "ppt":
        if not args.topic:
            print("✗ 错误: --topic 是必需的")
            sys.exit(1)
        result = generate_ppt(args.topic, args.slides)
    
    else:
        result = {"success": False, "error": "未知命令"}
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("success"):
            print(f"✓ {result.get('message', '执行成功')}")
            if "output_file" in result:
                print(f"  输出文件: {result['output_file']}")
            if "competitors_analyzed" in result:
                print(f"  分析竞品: {result['competitors_analyzed']} 个")
            if "slides" in result:
                print(f"  幻灯片数: {result['slides']} 页")
        else:
            print(f"✗ 错误: {result.get('error', '未知错误')}")
            sys.exit(1)

if __name__ == "__main__":
    main()
