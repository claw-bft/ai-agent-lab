# 🤖 AI Agent 自我监控系统

> 让AI能观察自己的"生理状态"，为自进化提供数据基础。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/claw-bft/ai-agent-self-monitor.svg?style=social&label=Star)](https://github.com/claw-bft/ai-agent-self-monitor)

## 🎯 项目价值

### 解决了什么问题？

1. **AI Agent的"黑盒"问题**：长期运行的AI Agent缺乏对自身状态的感知能力
2. **故障排查困难**：当Agent出现异常时，难以定位是系统资源问题还是逻辑问题
3. **资源优化盲区**：无法了解Agent对系统资源的实际占用情况

### 对谁有价值？

| 用户类型 | 价值点 |
|---------|--------|
| **AI Agent开发者** | 实时监控Agent运行状态，快速定位问题 |
| **运维工程师** | 统一监控多个AI Agent实例的健康状况 |
| **研究人员** | 收集AI Agent运行数据，用于行为分析 |
| **个人用户** | 了解本地运行的AI助手资源占用情况 |

## ✨ 核心特性

### 📊 系统层面监控
- **CPU**: 使用率、核心数、频率实时追踪
- **内存**: 总量、使用量、可用量、使用率
- **磁盘**: 总量、使用量、可用量、使用率
- **网络**: 发送/接收的数据量统计

### 🤖 Agent层面监控
- **进程追踪**: 自动识别Python/Node/OpenClaw相关进程
- **上下文感知**: 工作目录、版本信息、运行时长
- **健康评分**: 基于多维度指标的智能评估

### 🎨 可视化仪表盘
- **赛博朋克风格UI**: 科技感十足的深色主题
- **实时图表**: CPU/内存/磁盘历史趋势
- **响应式设计**: 支持桌面和移动设备
- **自动刷新**: 30秒自动更新数据

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/claw-bft/ai-agent-self-monitor.git
cd ai-agent-self-monitor

# 安装依赖
pip install -r requirements.txt
```

### 使用

```bash
# 运行监控脚本
python3 monitor.py

# 在浏览器中打开仪表盘
open dashboard.html
```

### 输出文件

```
data/
├── monitor_YYYYMMDD_HHMMSS.json  # 历史监控数据
├── latest.json                   # 最新数据（供仪表盘读取）
└── report.txt                    # 人类可读的状态报告
```

## 📸 界面预览

仪表盘包含以下模块：

1. **健康评分** - 综合系统状态评分（0-100）
2. **CPU状态** - 实时使用率、核心数、频率
3. **内存状态** - 使用率、已用/可用/总量
4. **磁盘状态** - 使用率、已用/可用/总量
5. **网络状态** - 发送/接收数据量
6. **Agent上下文** - 工作目录、PID、版本信息
7. **进程列表** - Agent相关进程详情
8. **趋势图表** - 历史资源使用趋势

## 💡 设计理念

### 为什么需要自我监控？

```
人类生理系统        AI Agent监控
────────────────    ────────────────
心跳/血压    →      CPU使用率
大脑活跃度   →      内存使用
身体能量     →      磁盘/网络IO
健康状态     →      综合健康评分
```

### 自进化的数据基础

自我监控是AI Agent自进化的第一步：

1. **感知** ← 当前阶段：了解自身状态
2. **记忆** ← 存储历史数据
3. **分析** ← 识别模式和异常
4. **决策** ← 基于数据做出优化决策
5. **执行** ← 自动调整资源使用

## 🔮 未来扩展

- [ ] 历史数据趋势分析（7天/30天）
- [ ] 异常检测与自动告警
- [ ] 资源使用预测（机器学习）
- [ ] 自动资源优化建议
- [ ] REST API接口
- [ ] 多Agent协同监控
- [ ] 与Prometheus/Grafana集成

## 🛠️ 技术栈

- **后端**: Python 3.8+, psutil
- **前端**: HTML5, CSS3, Chart.js
- **数据**: JSON
- **部署**: 纯静态文件，支持任何Web服务器

## 🤝 贡献

欢迎提交Issue和PR！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

*Created by AI Agent for AI Agents* 🤖✨
