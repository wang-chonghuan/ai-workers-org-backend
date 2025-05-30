from agno.playground import Playground, serve_playground_app
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from agents import all_agents

# 加载.env文件中的环境变量
load_dotenv()

# 从环境变量读取是否允许localhost CORS的标志
ALLOW_LOCALHOST_CORS = os.getenv("ALLOW_LOCALHOST_CORS", "false").lower() == "true"

app = Playground(
    agents=all_agents
).get_app()

# 构建允许的源列表
allowed_origins = [
    "https://ai-workers.org",
    "https://www.ai-workers.org",
    "https://finley2-ui.pages.dev/",
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