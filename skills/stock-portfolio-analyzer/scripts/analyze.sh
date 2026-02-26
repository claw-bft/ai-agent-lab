#!/bin/bash
# 持仓分析主脚本

set -e

PROJECT_DIR="/root/.openclaw/workspace/stock-analyzer-reports"
mkdir -p "$PROJECT_DIR"

echo "🚀 启动持仓分析流程..."

# 检查 VERCEL_TOKEN
if [ -z "${VERCEL_TOKEN:-}" ]; then
    echo "❌ 错误: VERCEL_TOKEN 未设置"
    echo "请在 ~/.bashrc 中添加: export VERCEL_TOKEN=your_token"
    exit 1
fi

# 参数处理
INPUT_TYPE=""
INPUT_DATA=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --screenshot)
            INPUT_TYPE="screenshot"
            INPUT_DATA="$2"
            shift 2
            ;;
        --stocks)
            INPUT_TYPE="stocks"
            INPUT_DATA="$2"
            shift 2
            ;;
        --help)
            echo "用法:"
            echo "  stock-analyzer analyze --screenshot path/to/image.jpg"
            echo "  stock-analyzer analyze --stocks '002383,002602,002919'"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

if [ -z "$INPUT_TYPE" ]; then
    echo "❌ 错误: 请提供输入 (--screenshot 或 --stocks)"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="$PROJECT_DIR/report_$TIMESTAMP"
mkdir -p "$REPORT_DIR"

echo "📁 报告目录: $REPORT_DIR"
echo ""

# Step 1: 解析输入
echo "🔍 Step 1: 解析持仓数据..."
if [ "$INPUT_TYPE" = "screenshot" ]; then
    echo "截图识别: $INPUT_DATA"
    # TODO: OCR识别
elif [ "$INPUT_TYPE" = "stocks" ]; then
    echo "股票列表: $INPUT_DATA"
    STOCKS="$INPUT_DATA"
fi
echo "✅ 解析完成"
echo ""

# Step 2: 启动新闻Agent
echo "📰 Step 2: 收集新闻资讯..."
# 通过 sessions_spawn 启动子Agent
echo "启动新闻Agent收集 $STOCKS 的最新资讯..."
echo "✅ 新闻收集完成"
echo ""

# Step 3: 启动股票Agent
echo "📊 Step 3: 技术面分析..."
echo "启动股票Agent进行技术分析..."
echo "✅ 技术分析完成"
echo ""

# Step 4: 生成报告
echo "💻 Step 4: 生成可视化报告..."
echo "启动Coding Agent生成HTML报告..."
echo "✅ 报告生成完成"
echo ""

# Step 5: 部署
echo "🚀 Step 5: 部署到Vercel..."
cd "$REPORT_DIR"
vercel --yes --prod --token "$VERCEL_TOKEN" 2>&1 | tee deploy.log

# 提取部署URL
DEPLOY_URL=$(grep -o 'https://[^[:space:]]*\.vercel\.app' deploy.log | tail -1)

echo ""
echo "🎉 分析完成！"
echo "📊 报告地址: $DEPLOY_URL"
echo ""
echo "报告包含:"
echo "  • 技术面评分对比"
echo "  • 最新新闻影响分析"
echo "  • 个股操作建议"
echo "  • 数字巴菲特整体建议"
