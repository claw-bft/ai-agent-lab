"""
Example: Multi-Agent Stock Analysis Workflow

Demonstrates ACP usage with news-agent → analyzer-agent → deploy-agent pipeline
"""
import asyncio
from acp import Agent, InMemoryMessageBus, TaskRequest, Workflow


# Shared message bus
bus = InMemoryMessageBus()


# ============ News Agent ============
news_agent = Agent(
    name="news-agent",
    capabilities=["fetch_news", "fetch_market_data"],
    message_bus=bus
)

@news_agent.handler("fetch_news")
async def handle_fetch_news(request: TaskRequest):
    symbol = request.parameters["symbol"]
    # Simulate news fetching
    return {
        "symbol": symbol,
        "headlines": [
            f"{symbol} reports strong Q4 earnings",
            f"Analysts upgrade {symbol} price target"
        ],
        "sentiment": "positive"
    }


# ============ Analyzer Agent ============
analyzer_agent = Agent(
    name="analyzer-agent", 
    capabilities=["stock_analysis", "sentiment_analysis"],
    message_bus=bus
)

@analyzer_agent.handler("stock_analysis")
async def handle_stock_analysis(request: TaskRequest):
    symbol = request.parameters["symbol"]
    news_data = request.parameters.get("fetch_news_result", {})
    
    # Simulate analysis
    sentiment = news_data.get("sentiment", "neutral")
    recommendation = "buy" if sentiment == "positive" else "hold"
    
    return {
        "symbol": symbol,
        "recommendation": recommendation,
        "confidence": 0.85,
        "sentiment": sentiment,
        "target_price": 180.0
    }


# ============ Deploy Agent ============
deploy_agent = Agent(
    name="deploy-agent",
    capabilities=["deploy_report", "send_notification"],
    message_bus=bus
)

@deploy_agent.handler("deploy_report")
async def handle_deploy_report(request: TaskRequest):
    analysis_result = request.parameters.get("analyze_stock_result", {})
    
    # Simulate deployment
    return {
        "status": "deployed",
        "url": f"https://reports.example.com/{analysis_result.get('symbol', 'UNKNOWN')}",
        "timestamp": "2026-02-27T03:20:00Z"
    }


async def main():
    """Run the multi-agent workflow"""
    
    # Start agents
    agents = [news_agent, analyzer_agent, deploy_agent]
    for agent in agents:
        asyncio.create_task(agent.start())
    
    # Create workflow
    workflow = Workflow("stock-analysis-pipeline")
    workflow.agents = {
        "news-agent": news_agent,
        "analyzer-agent": analyzer_agent,
        "deploy-agent": deploy_agent
    }
    
    # Add steps
    workflow.add_step(
        name="fetch_news",
        agent="news-agent",
        task_type="fetch_news",
        parameters={"symbol": "AAPL"}
    )
    
    workflow.add_step(
        name="analyze_stock",
        agent="analyzer-agent",
        task_type="stock_analysis",
        parameters={"symbol": "AAPL"},
        depends_on=["fetch_news"]
    )
    
    workflow.add_step(
        name="deploy_report",
        agent="deploy-agent",
        task_type="deploy_report",
        depends_on=["analyze_stock"]
    )
    
    # Execute
    print("Starting stock analysis workflow...")
    results = await workflow.execute()
    
    print("\n=== Workflow Results ===")
    for step_name, response in results.items():
        print(f"\n{step_name}:")
        print(f"  Status: {response.status.value}")
        print(f"  Result: {response.result}")
        if response.execution_time_ms:
            print(f"  Execution time: {response.execution_time_ms}ms")
    
    # Stop agents
    for agent in agents:
        agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
