#!/usr/bin/env python3
"""
实时网络延迟监控器
监控 GitHub/Google/百度 的延迟并生成可视化报告
"""

import subprocess
import time
import json
import os
from datetime import datetime
from collections import defaultdict
import statistics

# 监控目标
TARGETS = {
    "GitHub": "github.com",
    "Google": "google.com",
    "Baidu": "baidu.com"
}

# 数据存储
DATA_FILE = "latency_data.json"
REPORT_FILE = "latency_report.html"

def ping_host(host, count=4):
    """Ping 主机并返回延迟统计"""
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), "-W", "2", host],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            return {"status": "failed", "error": "Host unreachable"}
        
        # 解析 ping 输出
        lines = result.stdout.strip().split('\n')
        times = []
        
        for line in lines:
            if "time=" in line:
                # 提取时间值
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

def load_data():
    """加载历史数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return defaultdict(list)

def save_data(data):
    """保存数据"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def collect_latency():
    """收集所有目标的延迟数据"""
    timestamp = datetime.now().isoformat()
    results = {}
    
    print(f"[{timestamp}] 开始监控...")
    
    for name, host in TARGETS.items():
        print(f"  正在测试 {name} ({host})...", end=" ")
        result = ping_host(host)
        results[name] = result
        
        if result["status"] == "success":
            print(f"✓ 平均延迟: {result['avg']}ms")
        else:
            print(f"✗ 失败: {result.get('error', 'Unknown')}")
    
    return {"timestamp": timestamp, "data": results}

def generate_html_report(all_data):
    """生成 HTML 可视化报告"""
    
    # 准备图表数据
    chart_data = defaultdict(lambda: {"timestamps": [], "avg": [], "min": [], "max": []})
    
    for entry in all_data[-50:]:  # 最近50条记录
        ts = entry["timestamp"][:19].replace("T", " ")
        for name, data in entry["data"].items():
            chart_data[name]["timestamps"].append(ts)
            if data["status"] == "success":
                chart_data[name]["avg"].append(data["avg"])
                chart_data[name]["min"].append(data["min"])
                chart_data[name]["max"].append(data["max"])
            else:
                chart_data[name]["avg"].append("null")
                chart_data[name]["min"].append("null")
                chart_data[name]["max"].append("null")
    
    # 计算统计信息
    stats = {}
    for name in TARGETS.keys():
        all_avgs = []
        for entry in all_data:
            if entry["data"][name]["status"] == "success":
                all_avgs.append(entry["data"][name]["avg"])
        
        if all_avgs:
            stats[name] = {
                "avg": round(statistics.mean(all_avgs), 2),
                "min": round(min(all_avgs), 2),
                "max": round(max(all_avgs), 2),
                "count": len(all_avgs)
            }
        else:
            stats[name] = {"avg": "N/A", "min": "N/A", "max": "N/A", "count": 0}
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网络延迟监控报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-card h2 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-detail {{
            color: #666;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .chart-container h3 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
        }}
        .timestamp {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 20px;
            font-size: 0.9em;
        }}
        .status-good {{ color: #28a745; }}
        .status-warn {{ color: #ffc107; }}
        .status-bad {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 网络延迟监控报告</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h2>🐙 GitHub</h2>
                <div class="stat-value">{stats["GitHub"]["avg"]}<small style="font-size:0.5em">ms</small></div>
                <div class="stat-detail">
                    最小: {stats["GitHub"]["min"]}ms | 最大: {stats["GitHub"]["max"]}ms<br>
                    样本数: {stats["GitHub"]["count"]}
                </div>
            </div>
            <div class="stat-card">
                <h2>🔍 Google</h2>
                <div class="stat-value">{stats["Google"]["avg"]}<small style="font-size:0.5em">ms</small></div>
                <div class="stat-detail">
                    最小: {stats["Google"]["min"]}ms | 最大: {stats["Google"]["max"]}ms<br>
                    样本数: {stats["Google"]["count"]}
                </div>
            </div>
            <div class="stat-card">
                <h2>🇨🇳 百度</h2>
                <div class="stat-value">{stats["Baidu"]["avg"]}<small style="font-size:0.5em">ms</small></div>
                <div class="stat-detail">
                    最小: {stats["Baidu"]["min"]}ms | 最大: {stats["Baidu"]["max"]}ms<br>
                    样本数: {stats["Baidu"]["count"]}
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>📊 延迟趋势图 (最近50次测试)</h3>
            <canvas id="latencyChart"></canvas>
        </div>
        
        <div class="timestamp">
            报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
            数据来源: 实时Ping测试
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('latencyChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {chart_data["GitHub"]["timestamps"]},
                datasets: [
                    {{
                        label: 'GitHub',
                        data: {chart_data["GitHub"]["avg"]},
                        borderColor: '#6f42c1',
                        backgroundColor: 'rgba(111, 66, 193, 0.1)',
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'Google',
                        data: {chart_data["Google"]["avg"]},
                        borderColor: '#4285f4',
                        backgroundColor: 'rgba(66, 133, 244, 0.1)',
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'Baidu',
                        data: {chart_data["Baidu"]["avg"]},
                        borderColor: '#de0a19',
                        backgroundColor: 'rgba(222, 10, 25, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}
                ]
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
    
    print(f"\n✓ 报告已生成: {REPORT_FILE}")
    return REPORT_FILE

def main():
    """主函数"""
    print("=" * 50)
    print("  实时网络延迟监控器")
    print("=" * 50)
    
    # 加载历史数据
    data = load_data()
    if "records" not in data:
        data["records"] = []
    
    # 收集当前延迟数据
    result = collect_latency()
    data["records"].append(result)
    
    # 保存数据
    save_data(data)
    print(f"✓ 数据已保存 ({len(data['records'])} 条记录)")
    
    # 生成报告
    report_file = generate_html_report(data["records"])
    
    print("\n" + "=" * 50)
    print("监控完成!")
    print(f"数据文件: {DATA_FILE}")
    print(f"报告文件: {report_file}")
    print("=" * 50)
    
    return data, report_file

if __name__ == "__main__":
    main()
