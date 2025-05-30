import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.dalle import DalleTools

# Load .env file environment variables
load_dotenv()

agent_storage: str = "../tmp/agents.db"
openai_api_key = os.getenv("OPENAI_API_KEY")

image_agent = Agent(
    name="Image Agent",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[
        DuckDuckGoTools(),
        DalleTools(api_key=openai_api_key),
    ],
    description="我是一个视觉图像专家，可以分析图片并生成新的图片。",
    instructions=[
        "当用户上传图片时，详细分析图片内容",
        "当被要求创建图片时，使用DALLE工具生成高质量图片",
        "提供详细、专业的图片解析",
        "使用markdown格式美化输出",
        "当你使用DALLE工具生成图片后，请在文字描述中提及你已生成图片。框架会自动展示图片，你无需在回复中再次用markdown插入图片。",
    ],
    storage=SqliteAgentStorage(table_name="image_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    show_tool_calls=True,
)
