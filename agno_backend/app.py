from agno.models.openai import OpenAILike
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.tools.mcp import MCPTools

# Create the Agent
agno_agent = Agent(
    name="Agno Agent",
    model=OpenAILike(
        id="Pro/moonshotai/Kimi-K2-Thinking",
        api_key="sk-vnotauwtuxlymyzczpyoqoussinsphsvyjmeumcg",
        base_url="https://api.siliconflow.cn/v1",
    ),
    # Add a database to the Agent
    db=SqliteDb(db_file="agno.db"),
    # Add the Agno MCP server to the Agent
    tools=[MCPTools(transport="streamable-http", url="https://docs.agno.com/mcp")],
    # Add the previous session history to the context
    add_history_to_context=True,
    markdown=True,
    stream=True,
    store_events=True,
)


# Create the AgentOS
agent_os = AgentOS(agents=[agno_agent])
# Get the FastAPI app for the AgentOS
app = agent_os.get_app()

if __name__ == '__main__':
    # Default port is 7777; change with port=...
    agent_os.serve(app="my_os:app")