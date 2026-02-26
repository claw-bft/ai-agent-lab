#!/usr/bin/env python3
"""
实时网络延迟监控器 v2.0
监控 GitHub/Google/百度 的延迟并生成可视化报告

改进点：
- 异步并发测试，速度提升3倍
- 支持更多监控目标
- 添加网络质量评级系统
- 历史数据分析与趋势预测
- 告警阈值机制
"""

import subprocess
import time
import json
import os
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from typing import Dict, List, Optional

# 监控目标配置
TARGETS = {
    "GitHub": {"host": "github.com", "threshold": 200, "importance": "high"},
    "Baidu": {"host": "baidu.com", "threshold": 50, "importance": "high"},
    "Cloudflare": {"host": "cloudflare.com", "threshold": 100, "importance": "medium"},
}

# 数据存储
DATA_FILE = "latency_data.json"
REPORT_FILE = "latency_report.html"
ALERT_LOG_FILE = "latency_alerts.log"

# 质量评级阈值
QUALITY_THRESHOLDS = {
    "excellent": {"max": 50, "color": "#28a745", "label": "优秀"},
    "good": {"max": 100, "color": "#6f42c1", "label": "良好"},
    "fair": {"max": 200, "color": "#ffc107", "label": "一般"},
    "poor": {"max": float('inf'), "color": "#dc3545", "label": "较差"}
}


def get_quality_rating(latency: float) -> Dict:
    """根据延迟获取质量评级"""
    for quality, config in QUALITY_THRESHOLDS.items():
        if latency <= config["max"]:
            return {"level": quality, **config}
    return {"level": "poor", **QUALITY_THRESHOLDS["poor"]}


def ping_host_sync(host: str, count: int = 4) -> Dict:
    """同步Ping主机"""
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), "-W", "2", host],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            return {"status": "failed", "error": "Host unreachable"}
        
        lines = result.stdout.strip().split('\n')
        times = []
        
        for line in lines:
            if "time=" in line:
                time_part = line.split("time=")[1].split()[0]
                times.append(float(time_part))
        
        if not times:
            return {"status": "failed", "error": "No valid ping data"}
        
        return {
            "status": "success",
            "min": round(min(times), 2),
            "max": round(max(times), 2),
            "avg": round(statistics.mean(times), 2),
            "loss": round((1 - len(times) / count) * 100, 1)
        }
    
    except subprocess.TimeoutExpired:
        return {"status": "failed", "error": "Timeout"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


async def ping_host_async(name: str, config: Dict) -> tuple:
    """异步Ping主机"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, ping_host_sync, config["host"])
    return name, config, result


async def collect_latency_async() -> Dict:
    """并发收集所有目标的延迟数据"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] 开始并发监控...")
    
    tasks = [ping_host_async(name, config) for name, config in TARGETS.items()]
    results = await asyncio.gather(*tasks)
    
    data = {}
    for name, config, result in results:
        data[name] = result
        if result["status"] == "success":
            quality = get_quality_rating(result["avg"])
            print(f"  ✓ {name}: {result['avg']}ms ({quality['label']})")
        else:
            print(f"  ✗ {name}: {result.get('error', 'Unknown')}")
    
    return {"timestamp": timestamp, "data": data}


def load_data() -> Dict:
    """加载历史数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"records": [], "alerts": []}


def save_data(data: Dict):
    """保存数据"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def check_alerts(record: Dict, data: Dict) -> List[Dict]:
    """检查是否需要告警"""
    alerts = []
    timestamp = record["timestamp"]
    
    for name, result in record["data"].items():
        config = TARGETS[name]
        
        if result["status"] == "failed":
            alert = {
                "timestamp": timestamp,
                "target": name,
                "type": "unreachable",
                "message": f"{name} 无法访问",
                "severity": "high" if config["importance"] == "high" else "medium"
            }
            alerts.append(alert)
        elif result["status"] == "success":
            if result["avg"] > config["threshold"]:
                alert = {
                    "timestamp": timestamp,
                    "target": name,
                    "type": "high_latency",
                    "message": f"{name} 延迟过高: {result['avg']}ms (阈值: {config['threshold']}ms)",
                    "severity": "medium"
                }
                alerts.append(alert)
            
            if result["loss"] > 10:
                alert = {
                    "timestamp": timestamp,
                    "target": name,
                    "type": "packet_loss",
                    "message": f"{name} 丢包严重: {result['loss']}%",
                    "severity": "high"
                }
                alerts.append(alert)
    
    return alerts


def analyze_trends(records: List[Dict], target: str) -> Dict:
    """分析延迟趋势"""
    values = []
    for record in records[-20:]:
        if target in record["data"] and record["data"][target]["status"] == "success":
            values.append(record["data"][target]["avg"])
    
    if len(values) < 5:
        return {"trend": "insufficient_data", "change": 0}
    
    recent_avg = statistics.mean(values[-5:])
    older_avg = statistics.mean(values[:5])
    change = recent_avg - older_avg
    
    if change < -10:
        trend = "improving"
    elif change > 10:
        trend = "degrading"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "change": round(change, 2),
        "recent_avg": round(recent_avg, 2),
        "volatility": round(statistics.stdev(values), 2) if len(values) > 1 else 0
    }


def generate_html_report(data: Dict) -> str:
    """生成增强版 HTML 可视化报告"""
    records = data.get("records", [])
    alerts = data.get("alerts", [])
    
    if not records:
        return "<html><body><h1>暂无数据</h1></body></html>"
    
    chart_data = defaultdict(lambda: {"timestamps": [], "avg": [], "min": [], "max": []})
    
    for entry in records[-50:]:
        ts = entry["timestamp"][:19].replace("T", " ")
        for name in TARGETS.keys():
            chart_data[name]["timestamps"].append(ts)
            result = entry["data"].get(name, {"status": "failed"})
            if result["status"] == "success":
                chart_data[name]["avg"].append(result["avg"])
                chart_data[name]["min"].append(result["min"])
                chart_data[name]["max"].append(result["max"])
            else:
                chart_data[name]["avg"].append("null")
                chart_data[name]["min"].append("null")
                chart_data[name]["max"].append("null")
    
    stats = {}
    trends = {}
    for name in TARGETS.keys():
        all_avgs = []
        for entry in records:
            if name in entry["data"] and entry["data"][name]["status"] == "success":
                all_avgs.append(entry["data"][name]["avg"])
        
        if all_avgs:
            quality = get_quality_rating(statistics.mean(all_avgs))
            stats[name] = {
                "avg": round(statistics.mean(all_avgs), 2),
                "min": round(min(all_avgs), 2),
                "max": round(max(all_avgs), 2),
                "count": len(all_avgs),
                "quality": quality
            }
        else:
            stats[name] = {"avg": "N/A", "min": "N/A", "max": "N/A", "count": 0, "quality": None}
        
        trends[name] = analyze_trends(records, name)
    
    recent_alerts = alerts[-10:] if alerts else []
    alerts_html = ""
    if recent_alerts:
        alerts_html = "<div class='alerts-section'><h3>近期告警</h3><ul>"
        for alert in reversed(recent_alerts):
            severity_icon = "🔴" if alert["severity"] == "high" else "🟡"
            alerts_html += f"<li class='alert-{alert['severity']}'>{severity_icon} {alert['timestamp'][:19]} - {alert['message']}</li>"
        alerts_html += "</ul></div>"
    
    colors = {
        "GitHub": "#6f42c1",
        "Baidu": "#de0a19",
        "Cloudflare": "#f48120"
    }
    
    # Build stats cards HTML
    stats_cards = ""
    for name in TARGETS.keys():
        quality_badge = ""
        if stats[name]["quality"]:
            q = stats[name]["quality"]
            quality_badge = f'<span class="quality-badge" style="background:{q["color"]}">{q["label"]}</span>'
        
        trend_html = ""
        if trends[name]["trend"] != "insufficient_data":
            trend_icon = "📈" if trends[name]["trend"] == "improving" else "📉" if trends[name]["trend"] == "degrading" else "➡️"
            trend_class = f"trend-{trends[name]['trend']}"
            trend_html = f'<div class="trend-indicator {trend_class}">{trend_icon} {trends[name]["change"]:+.1f}ms</div>'
        
        stats_cards += f'''
        <div class="stat-card" style="border-left-color: {colors[name]}">
            <h2>{name} {quality_badge}</h2>
            <div class="stat-value" style="color: {colors[name]}">{stats[name]["avg"]}<small style="font-size:0.4em; color:#666">ms</small></div>
            <div class="stat-detail">
                最小: {stats[name]["min"]}ms | 最大: {stats[name]["max"]}ms<br>
                样本数: {stats[name]["count"]}
            </div>
            {trend_html}
        </div>
        '''
    
    # Build chart datasets
    datasets = []
    for name in TARGETS.keys():
        datasets.append({
            "label": name,
            "data": chart_data[name]["avg"],
            "borderColor": colors[name],
            "backgroundColor": colors[name] + "20",
            "tension": 0.4,
            "fill": False,
            "pointRadius": 3,
            "pointHoverRadius": 6
        })
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网络延迟监控报告 v2.0</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .subtitle {{
            text-align: center;
            color: rgba(255,255,255,0.7);
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: transform 0.3s, box-shadow 0.3s;
            border-left: 5px solid #667eea;
        }}
        .stat-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.4); }}
        .stat-card h2 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .quality-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
            margin-left: 10px;
        }}
        .stat-detail {{
            color: #666;
            margin-top: 10px;
            font-size: 0.9em;
            line-height: 1.6;
        }}
        .trend-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 0.85em;
            margin-top: 8px;
        }}
        .trend-improving {{ color: #28a745; }}
        .trend-degrading {{ color: #dc3545; }}
        .trend-stable {{ color: #6c757d; }}
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .chart-container h3 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
        }}
        .alerts-section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .alerts-section h3 {{
            color: #333;
            margin-bottom: 15px;
        }}
        .alerts-section ul {{
            list-style: none;
        }}
        .alerts-section li {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            background: #f8f9fa;
        }}
        .alert-high {{ border-left: 4px solid #dc3545; }}
        .alert-medium {{ border-left: 4px solid #ffc107; }}
        .timestamp {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 20px;
            font-size: 0.9em;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9em;
            color: white;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>网络延迟监控报告 v2.0</h1>
        <p class="subtitle">实时监控 · 趋势分析 · 智能告警</p>
        
        <div class="legend">
            <div class="legend-item"><div class="legend-color" style="background:#28a745"></div>优秀 (&lt;50ms)</div>
            <div class="legend-item"><div class="legend-color" style="background:#6f42c1"></div>良好 (50-100ms)</div>
            <div class="legend-item"><div class="legend-color" style="background:#ffc107"></div>一般 (100-200ms)</div>
            <div class="legend-item"><div class="legend-color" style="background:#dc3545"></div>较差 (&gt;200ms)</div>
        </div>
        
        <div class="stats-grid">
            {stats_cards}
        </div>
        
        {alerts_html}
        
        <div class="chart-container">
            <h3>延迟趋势图 (最近50次测试)</h3>
            <canvas id="latencyChart"></canvas>
        </div>
        
        <div class="timestamp">
            报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
            数据来源: 实时Ping测试 | 监控目标: {len(TARGETS)}个
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('latencyChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {chart_data["GitHub"]["timestamps"]},
                datasets: {json.dumps(datasets)}
            }},
            options: {{
                responsive: true,
                interaction: {{
                    mode: 'index',
                    intersect: false,
                }},
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    title: {{
                        display: true,
                        text: '平均延迟 (ms)'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '延迟 (ms)'
                        }},
                        grid: {{
                            color: 'rgba(0,0,0,0.1)'
                        }}
                    }},
                    x: {{
                        grid: {{
                            color: 'rgba(0,0,0,0.05)'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n报告已生成: {REPORT_FILE}")
    return REPORT_FILE


def log_alerts(alerts: List[Dict]):
    """记录告警到日志文件"""
    if not alerts:
        return
    
    with open(ALERT_LOG_FILE, 'a') as f:
        for alert in alerts:
            f.write(f"[{alert['timestamp']}] [{alert['severity'].upper()}] {alert['message']}\n")
    print(f"已记录 {len(alerts)} 条告警到 {ALERT_LOG_FILE}")


async def main():
    """主函数"""
    print("=" * 60)
    print("  实时网络延迟监控器 v2.0")
    print("  并发测试 · 趋势分析 · 智能告警")
    print("=" * 60)
    
    data = load_data()
    result = await collect_latency_async()
    data["records"].append(result)
    
    alerts = check_alerts(result, data)
    if alerts:
        data.setdefault("alerts", []).extend(alerts)
        log_alerts(alerts)
    
    save_data(data)
    print(f"数据已保存 ({len(data['records'])} 条记录)")
    
    report_file = generate_html_report(data)
    
    print("\n" + "=" * 60)
    print("监控完成!")
    print(f"数据文件: {DATA_FILE}")
    print(f"报告文件: {REPORT_FILE}")
    print(f"告警日志: {ALERT_LOG_FILE}")
    print("=" * 60)
    
    return data, report_file


if __name__ == "__main__":
    asyncio.run(main())
