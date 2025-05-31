import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from ..infra.db import get_shared_db_engine

# Load .env file environment variables
load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please ensure it is available.")

reasoning_agent = Agent(
    name="Reasoning Agent",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[
        DuckDuckGoTools(),
        YFinanceTools(
            stock_price=True,
            company_info=True,
        ),
    ],
    instructions=[
        "展示你的思考过程",
        "分步骤解决问题",
        "使用你的工具来获取信息",
        "使用表格和图表来展示数据",
    ],
    storage=PostgresAgentStorage(table_name="reasoning_agent", db_engine=get_shared_db_engine()),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    show_tool_calls=True,
    reasoning=True,
)
