import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools

# Load .env file environment variables
load_dotenv()

agent_storage: str = "../tmp/agents.db"
openai_api_key = os.getenv("OPENAI_API_KEY")

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
