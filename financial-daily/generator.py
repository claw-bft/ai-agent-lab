#!/usr/bin/env python3
"""
财经资讯日报生成器
深度采集财经热点，生成日报推送到GitHub
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess

# 添加skill路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/research-pro')
sys.path.insert(0, '/root/.openclaw/workspace/skills/finance-pro')

class FinancialNewsDaily:
    """财经资讯日报"""
    
    def __init__(self):
        self.output_dir = "/root/.openclaw/workspace/financial-daily"
        self.github_repo = "claw-bft/ai-agent-lab"
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/reports", exist_ok=True)
        os.makedirs(f"{self.output_dir}/data", exist_ok=True)
    
    def collect_news(self) -> List[Dict]:
        """采集财经新闻热点"""
        # 使用research-pro搜索功能
        try:
            from research_pro import DeepResearchEngine
            engine = DeepResearchEngine()
            
            # 搜索财经热点
            queries = [
                "今日股市热点 A股",
                "财经新闻 重大事件",
                "宏观经济 政策",
                "行业动态 科技 金融"
            ]
            
            all_results = []
            for query in queries:
                results = engine.search(query, max_results=5)
                all_results.extend(results)
            
            return all_results
        except Exception as e:
            print(f"采集新闻失败: {e}")
            return []
    
    def analyze_market(self) -> Dict:
        """分析市场行情"""
        try:
            from data_adapter import FinanceDataAdapter
            adapter = FinanceDataAdapter()
            
            # 获取主要指数
            indices = ['000001.SH', '399001.SZ', '399006.SZ']  # 上证、深证、创业板
            market_data = {}
            
            for idx in indices:
                try:
                    quote = adapter.get_stock_quote(idx)
                    if quote and 'error' not in quote:
                        market_data[idx] = quote
                except:
                    pass
            
            return market_data
        except Exception as e:
            print(f"市场分析失败: {e}")
            return {}
    
    def generate_report(self, news: List[Dict], market: Dict) -> str:
        """生成日报"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        report = f"""# 财经资讯日报 - {today}

## 📊 市场概览

"""
        # 添加市场行情
        if market:
            for idx, data in market.items():
                name = data.get('name', idx)
                price = data.get('price', 'N/A')
                change = data.get('change_percent', 'N/A')
                report += f"- **{name}**: {price} ({change}%)\n"
        else:
            report += "- 市场数据获取中...\n"
        
        report += "\n## 🔥 热点资讯\n\n"
        
        # 添加新闻
        if news:
            for i, item in enumerate(news[:10], 1):
                title = item.get('title', '无标题')
                source = item.get('source', '未知来源')
                url = item.get('url', '')
                report += f"{i}. **{title}**\n   - 来源: {source}\n"
                if url:
                    report += f"   - 链接: {url}\n"
                report += "\n"
        else:
            report += "- 资讯采集中...\n"
        
        report += f"""
## 📈 分析摘要

*基于采集的{len(news)}条资讯和{len(market)}个市场指数*

---
*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*数据来源: 公开财经资讯*
"""
        
        return report
    
    def save_and_push(self, report: str) -> bool:
        """保存报告并推送到GitHub"""
        today = datetime.now().strftime("%Y%m%d")
        filename = f"financial-daily-{today}.md"
        filepath = f"{self.output_dir}/reports/{filename}"
        
        # 保存报告
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 更新最新报告链接
        latest_link = f"{self.output_dir}/reports/LATEST.md"
        with open(latest_link, 'w', encoding='utf-8') as f:
            f.write(f"# 最新财经日报\n\n[查看今日报告](./{filename})\n")
        
        # 推送到GitHub
        try:
            os.chdir("/root/.openclaw/workspace/github-setup")
            
            # 复制报告到github-setup目录
            subprocess.run(["cp", filepath, "./financial-daily/"], check=False)
            
            # Git操作
            subprocess.run(["git", "add", "."], check=False)
            subprocess.run(["git", "commit", "-m", f"[daily] 财经资讯日报 {today}"], check=False)
            subprocess.run(["git", "push", "origin", "master"], check=False, timeout=60)
            
            print(f"✅ 报告已推送: {filename}")
            return True
        except Exception as e:
            print(f"⚠️ Git推送失败: {e}")
            return False
    
    def run(self):
        """运行日报生成"""
        print(f"🚀 开始生成财经日报 - {datetime.now()}")
        
        # 采集数据
        news = self.collect_news()
        market = self.analyze_market()
        
        # 生成报告
        report = self.generate_report(news, market)
        
        # 保存并推送
        success = self.save_and_push(report)
        
        if success:
            print("✅ 财经日报生成完成")
        else:
            print("⚠️ 日报生成完成，但推送失败")
        
        return success

if __name__ == "__main__":
    daily = FinancialNewsDaily()
    daily.run()
