#!/bin/bash
# OpenClaw 技能安装脚本 - 根据 Kimi 报告实现彻底进化
# 金融投资 + 程序员 + 产品经理 + 通用技能

cd /root/.openclaw/workspace

echo "=== 安装金融投资技能 ==="
clawhub install stock-analysis --force
clawhub install stock-monitor-skill --force
clawhub install tushare-finance --force
clawhub install finnhub-pro --force
clawhub install a-stock-monitor --force

echo "=== 安装程序员技能 ==="
clawhub install github --force
clawhub install openclaw-github-assistant --force
clawhub install devops --force
clawhub install senior-devops --force
clawhub install database-operations --force
clawhub install sql-toolkit --force
clawhub install coding --force
clawhub install openclaw-kirocli-coding-agent --force

echo "=== 安装产品经理技能 ==="
clawhub install deepresearch-conversation --force
clawhub install research-cog --force
clawhub install data-analysis --force
clawhub install data-analyst --force

echo "=== 安装通用技能 ==="
clawhub install tavily-search --force
clawhub install tavily --force
clawhub install web-search-plus --force

echo "=== 安装完成 ==="
clawhub list
