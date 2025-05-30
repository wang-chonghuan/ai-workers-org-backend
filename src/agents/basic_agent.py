import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
from infra.db import get_shared_db_engine

# Load .env file environment variables
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please ensure it is available.")

basic_agent = Agent(
    name="Basic Agent",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[],
    instructions=["Be a helpful assistant."],
    storage=PostgresAgentStorage(table_name="basic_agent", db_engine=get_shared_db_engine()),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
)
