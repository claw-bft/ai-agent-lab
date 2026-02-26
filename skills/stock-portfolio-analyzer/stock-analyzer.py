#!/usr/bin/env python3
"""
Stock Portfolio Analyzer - 股票持仓分析系统
多Agent协作完成新闻收集、技术面分析、报告生成和部署
"""

import os
import sys
import json
import re
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import quote

# 配置路径
SKILLS_DIR = Path("/root/.openclaw/workspace/skills")
SHARED_DIR = Path("/root/.openclaw/shared")
INCOMING_DIR = SHARED_DIR / "incoming"
REPORTS_DIR = SHARED_DIR / "reports"

# 确保目录存在
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class StockInfo:
    """股票信息"""
    name: str
    symbol: str
    price: float
    news: List[Dict] = None
    technical: Dict = None
    score: int = 0
    recommendation: str = ""

@dataclass
class AnalysisReport:
    """分析报告"""
    report_id: str
    timestamp: str
    stocks: List[StockInfo]
    summary: Dict
    overall_recommendation: str

class NewsAgent:
    """新闻收集Agent"""
    
    def __init__(self):
        self.name = "NewsAgent"
    
    def collect_news(self, symbol: str, name: str) -> List[Dict]:
        """收集股票相关新闻"""
        # 使用 kimi_search 获取新闻
        try:
            # 这里模拟搜索结果，实际应调用搜索API
            news_items = [
                {
                    "title": f"{name}({symbol}) 最新市场动态",
                    "source": "财经新闻",
                    "sentiment": "neutral",
                    "impact": "medium",
                    "summary": f"{name}近期表现平稳，市场关注度一般。"
                },
                {
                    "title": f"{name}技术面分析",
                    "source": "技术分析",
                    "sentiment": "positive",
                    "impact": "high",
                    "summary": f"技术指标显示{name}处于关键位置。"
                }
            ]
            return news_items
        except Exception as e:
            return [{"title": "新闻获取失败", "error": str(e)}]

class StockAgent:
    """技术分析Agent"""
    
    def __init__(self):
        self.name = "StockAgent"
    
    def analyze(self, symbol: str, name: str) -> Dict:
        """技术分析"""
        # 模拟技术分析结果
        return {
            "symbol": symbol,
            "name": name,
            "indicators": {
                "MACD": {"signal": "bullish", "value": "金叉"},
                "KDJ": {"signal": "neutral", "value": "50"},
                "RSI": {"signal": "neutral", "value": "52"},
                "MA": {"signal": "bullish", "value": "站上20日线"}
            },
            "support": "10.50",
            "resistance": "12.80",
            "score": 65,
            "recommendation": "观望"
        }

class ReportAgent:
    """报告生成Agent"""
    
    def __init__(self):
        self.name = "ReportAgent"
    
    def generate_html(self, report: AnalysisReport) -> str:
        """生成HTML报告"""
        
        html_parts = []
        
        # Header
        html_parts.append(self._generate_header(report))
        
        # Summary
        html_parts.append(self._generate_summary(report))
        
        # Stock cards
        for stock in report.stocks:
            html_parts.append(self._generate_stock_card(stock))
        
        # Footer
        html_parts.append(self._generate_footer(report))
        
        return "\n".join(html_parts)
    
    def _generate_header(self, report: AnalysisReport) -> str:
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>持仓分析报告 #{report.report_id}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 16px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .header .meta {{ opacity: 0.9; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: white; padding: 24px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .summary-card .label {{ color: #666; font-size: 0.9em; margin-bottom: 8px; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .stock-card {{ background: white; padding: 24px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px; }}
        .stock-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
        .stock-name {{ font-size: 1.4em; font-weight: bold; }}
        .stock-symbol {{ color: #666; margin-left: 8px; }}
        .score {{ font-size: 1.5em; font-weight: bold; padding: 8px 16px; border-radius: 20px; }}
        .score-high {{ background: #d4edda; color: #155724; }}
        .score-medium {{ background: #fff3cd; color: #856404; }}
        .score-low {{ background: #f8d7da; color: #721c24; }}
        .indicators {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 16px 0; }}
        .indicator {{ text-align: center; padding: 12px; background: #f8f9fa; border-radius: 8px; }}
        .indicator-name {{ font-size: 0.85em; color: #666; margin-bottom: 4px; }}
        .indicator-value {{ font-weight: bold; }}
        .news-list {{ margin-top: 16px; }}
        .news-item {{ padding: 12px; border-left: 3px solid #667eea; background: #f8f9fa; margin-bottom: 8px; border-radius: 0 8px 8px 0; }}
        .news-title {{ font-weight: 500; margin-bottom: 4px; }}
        .news-meta {{ font-size: 0.85em; color: #666; }}
        .recommendation {{ margin-top: 16px; padding: 16px; background: #e7f3ff; border-radius: 8px; border-left: 4px solid #0066cc; }}
        .footer {{ text-align: center; padding: 40px; color: #666; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 持仓分析报告</h1>
            <div class="meta">报告编号: #{report.report_id} | 生成时间: {report.timestamp}</div>
        </div>
"""
    
    def _generate_summary(self, report: AnalysisReport) -> str:
        total = len(report.stocks)
        avg_score = sum(s.score for s in report.stocks) / total if total > 0 else 0
        
        return f"""
        <div class="summary">
            <div class="summary-card">
                <div class="label">持仓数量</div>
                <div class="value">{total}</div>
            </div>
            <div class="summary-card">
                <div class="label">平均评分</div>
                <div class="value">{avg_score:.0f}</div>
            </div>
            <div class="summary-card">
                <div class="label">整体建议</div>
                <div class="value" style="font-size: 1.2em;">{report.overall_recommendation}</div>
            </div>
        </div>
"""
    
    def _generate_stock_card(self, stock: StockInfo) -> str:
        score_class = "score-high" if stock.score >= 70 else "score-medium" if stock.score >= 50 else "score-low"
        
        indicators_html = ""
        if stock.technical:
            for name, data in stock.technical.get("indicators", {}).items():
                indicators_html += f'<div class="indicator"><div class="indicator-name">{name}</div><div class="indicator-value">{data.get("value", "-")}</div></div>'
        
        news_html = ""
        if stock.news:
            for news in stock.news[:3]:
                news_html += f'''
                <div class="news-item">
                    <div class="news-title">{news.get("title", "")}</div>
                    <div class="news-meta">{news.get("source", "")} | {news.get("sentiment", "")}</div>
                </div>'''
        
        return f"""
        <div class="stock-card">
            <div class="stock-header">
                <div>
                    <span class="stock-name">{stock.name}</span>
                    <span class="stock-symbol">{stock.symbol}</span>
                </div>
                <div class="score {score_class}">{stock.score}分</div>
            </div>
            <div class="indicators">{indicators_html}</div>
            <div class="news-list">{news_html}</div>
            <div class="recommendation">
                <strong>操作建议:</strong> {stock.recommendation}
            </div>
        </div>
"""
    
    def _generate_footer(self, report: AnalysisReport) -> str:
        return f"""
        <div class="footer">
            <p>由 AI Agent 自动生成 | 仅供参考，不构成投资建议</p>
            <p style="margin-top: 8px; font-size: 0.9em;">claw-bft/ai-agent-lab</p>
        </div>
    </div>
</body>
</html>
"""

class DeployAgent:
    """部署Agent"""
    
    def __init__(self):
        self.name = "DeployAgent"
    
    def deploy_to_vercel(self, html_content: str, report_id: str) -> Dict:
        """部署到Vercel"""
        try:
            # 创建临时项目目录
            deploy_dir = Path(f"/tmp/stock-report-{report_id}")
            deploy_dir.mkdir(parents=True, exist_ok=True)
            
            # 写入HTML文件
            index_file = deploy_dir / "index.html"
            index_file.write_text(html_content, encoding='utf-8')
            
            # 检查vercel CLI
            result = subprocess.run(
                ["vercel", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Vercel CLI未安装或未配置",
                    "local_path": str(deploy_dir)
                }
            
            # 部署
            result = subprocess.run(
                ["vercel", "--yes", "--prod"],
                cwd=deploy_dir,
                capture_output=True,
                text=True,
                env={**os.environ, "VERCEL_TOKEN": os.environ.get("VERCEL_TOKEN", "")}
            )
            
            if result.returncode == 0:
                # 提取URL
                url_match = re.search(r'https?://[^\s]+\.vercel\.app', result.stdout)
                url = url_match.group(0) if url_match else "部署成功但URL提取失败"
                
                return {
                    "success": True,
                    "url": url,
                    "report_id": report_id
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "local_path": str(deploy_dir)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class StockAnalyzer:
    """主分析器 - 协调各Agent"""
    
    def __init__(self):
        self.news_agent = NewsAgent()
        self.stock_agent = StockAgent()
        self.report_agent = ReportAgent()
        self.deploy_agent = DeployAgent()
    
    def parse_stocks(self, input_data: str) -> List[StockInfo]:
        """解析股票输入"""
        stocks = []
        
        # 尝试JSON解析
        try:
            data = json.loads(input_data)
            if isinstance(data, list):
                for item in data:
                    stocks.append(StockInfo(
                        name=item.get("name", ""),
                        symbol=item.get("symbol", ""),
                        price=float(item.get("price", 0))
                    ))
                return stocks
        except:
            pass
        
        # 文本解析: "名称 - 代码 - 价格"
        lines = input_data.strip().split('\n')
        for line in lines:
            parts = line.split('-')
            if len(parts) >= 2:
                name = parts[0].strip()
                symbol = parts[1].strip()
                price = float(parts[2].strip()) if len(parts) > 2 else 0
                stocks.append(StockInfo(name=name, symbol=symbol, price=price))
        
        return stocks
    
    def analyze(self, stocks_input: str) -> AnalysisReport:
        """执行完整分析流程"""
        
        # 1. 解析股票
        stocks = self.parse_stocks(stocks_input)
        
        # 2. 收集新闻和技术分析
        for stock in stocks:
            stock.news = self.news_agent.collect_news(stock.symbol, stock.name)
            stock.technical = self.stock_agent.analyze(stock.symbol, stock.name)
            stock.score = stock.technical.get("score", 50)
            stock.recommendation = stock.technical.get("recommendation", "观望")
        
        # 3. 生成报告
        report_id = datetime.now().strftime("%Y%m%d%H%M%S")
        report = AnalysisReport(
            report_id=report_id,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            stocks=stocks,
            summary={"total": len(stocks)},
            overall_recommendation="分散持仓，关注技术面突破"
        )
        
        return report
    
    def generate_and_deploy(self, report: AnalysisReport) -> Dict:
        """生成报告并部署"""
        
        # 生成HTML
        html_content = self.report_agent.generate_html(report)
        
        # 保存本地副本
        local_file = REPORTS_DIR / f"report-{report.report_id}.html"
        local_file.write_text(html_content, encoding='utf-8')
        
        # 部署到Vercel
        deploy_result = self.deploy_agent.deploy_to_vercel(html_content, report.report_id)
        
        return {
            "report_id": report.report_id,
            "local_file": str(local_file),
            "deploy": deploy_result
        }

def main():
    parser = argparse.ArgumentParser(description="股票持仓分析系统")
    parser.add_argument("command", choices=["analyze", "list", "help"], help="命令")
    parser.add_argument("--input", "-i", help="输入文件或股票列表")
    parser.add_argument("--stocks", "-s", help="股票代码列表，逗号分隔")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--deploy", "-d", action="store_true", help="部署到Vercel")
    parser.add_argument("--json", "-j", action="store_true", help="JSON格式输出")
    
    args = parser.parse_args()
    
    analyzer = StockAnalyzer()
    
    if args.command == "help":
        print("""Stock Portfolio Analyzer - 股票持仓分析系统

用法:
  stock-analyzer analyze --input stocks.txt    分析持仓文件
  stock-analyzer analyze --stocks "002383,002602"  分析指定股票
  stock-analyzer list                          列出历史报告
  stock-analyzer help                          显示帮助

输入文件格式:
  股票名称 - 代码 - 现价
  例如:
  合众思壮 - 002383 - 11.34
  世纪华通 - 002602 - 18.76
""")
        return
    
    if args.command == "list":
        reports = sorted(REPORTS_DIR.glob("report-*.html"), key=lambda x: x.stat().st_mtime, reverse=True)
        print(f"历史报告 ({len(reports)}个):")
        for r in reports[:10]:
            print(f"  {r.name}")
        return
    
    if args.command == "analyze":
        # 获取输入
        if args.input:
            stocks_input = Path(args.input).read_text(encoding='utf-8')
        elif args.stocks:
            stocks_input = args.stocks
        else:
            # 检查incoming目录
            task_files = list(INCOMING_DIR.glob("*.json"))
            if task_files:
                latest = max(task_files, key=lambda x: x.stat().st_mtime)
                stocks_input = latest.read_text(encoding='utf-8')
            else:
                print("错误: 请提供 --input 或 --stocks 参数")
                sys.exit(1)
        
        # 执行分析
        print("开始分析...")
        report = analyzer.analyze(stocks_input)
        
        # 生成并部署
        if args.deploy:
            result = analyzer.generate_and_deploy(report)
            
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"✓ 报告已生成: {result['report_id']}")
                print(f"✓ 本地文件: {result['local_file']}")
                if result['deploy'].get('success'):
                    print(f"✓ 在线报告: {result['deploy']['url']}")
                else:
                    print(f"✗ 部署失败: {result['deploy'].get('error', '未知错误')}")
        else:
            # 仅生成本地报告
            html_content = analyzer.report_agent.generate_html(report)
            local_file = REPORTS_DIR / f"report-{report.report_id}.html"
            local_file.write_text(html_content, encoding='utf-8')
            
            if args.json:
                print(json.dumps({
                    "report_id": report.report_id,
                    "stocks_analyzed": len(report.stocks),
                    "local_file": str(local_file)
                }, indent=2, ensure_ascii=False))
            else:
                print(f"✓ 分析报告已生成: {local_file}")
                print(f"  分析股票: {len(report.stocks)}只")
                for s in report.stocks:
                    print(f"    - {s.name}({s.symbol}): {s.score}分 - {s.recommendation}")

if __name__ == "__main__":
    main()
