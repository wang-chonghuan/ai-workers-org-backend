from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground, serve_playground_app
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.dalle import DalleTools
from agno.media import Image
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# 加载.env文件中的环境变量
load_dotenv()

agent_storage: str = "tmp/agents.db"

# 从环境变量获取OpenAI API密钥
openai_api_key = os.getenv("OPENAI_API_KEY")

# 从环境变量读取是否允许localhost CORS的标志
ALLOW_LOCALHOST_CORS = os.getenv("ALLOW_LOCALHOST_CORS", "false").lower() == "true"

web_agent = Agent(
    name="Web Agent",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[DuckDuckGoTools()],
    instructions=["Always include sources"],
    storage=SqliteAgentStorage(table_name="web_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
)

finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            company_info=True,
            company_news=True,
        )
    ],
    instructions=["Always use tables to display data"],
    storage=SqliteAgentStorage(table_name="finance_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
)

# 添加一个新的带有推理步骤的Agent - 基于文档正确配置
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
    storage=SqliteAgentStorage(table_name="reasoning_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    show_tool_calls=True,  # 显示工具调用
    reasoning=True,  # 启用推理功能
)

# 添加一个新的图片代理 - 可以处理图片输入和输出
image_agent = Agent(
    name="Image Agent",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[
        DuckDuckGoTools(),
        DalleTools(api_key=openai_api_key),  # 为DalleTools提供API密钥
    ],
    description="我是一个视觉图像专家，可以分析图片并生成新的图片。",
    instructions=[
        "当用户上传图片时，详细分析图片内容",
        "当被要求创建图片时，使用DALLE工具生成高质量图片",
        "提供详细、专业的图片解析",
        "使用markdown格式美化输出",
        "在回答中插入相关的生成图片",
    ],
    storage=SqliteAgentStorage(table_name="image_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    show_tool_calls=True,
)

app = Playground(
    agents=[web_agent, finance_agent, reasoning_agent, image_agent]
).get_app()

# 构建允许的源列表
allowed_origins = [
    "https://ai-workers.net",
    "https://www.ai-workers.net",
    "https://aiworkers-frontend.pages.dev",
]

if ALLOW_LOCALHOST_CORS:
    allowed_origins.append("http://localhost:5173")

# 添加CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """
    Health check endpoint that returns the first 10 characters of the OpenAI API key.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    return {"openai_api_key_prefix": api_key[:10]}

if __name__ == "__main__":
    serve_playground_app("main:app", reload=True)