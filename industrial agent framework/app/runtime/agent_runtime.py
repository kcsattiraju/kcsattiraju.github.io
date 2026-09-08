from langchain.agents import create_agent

from app.models.llm_factory import create_llm
from app.tools.tool_registry import get_tools


def build_runtime_agent(
    agent_definition,
    tool_names: list[str],
):
    """
    Build a synchronous LangChain runtime agent.

    Current demo behavior:
    - Agent config comes from PostgreSQL.
    - Assigned tool names come from PostgreSQL.
    - Executable local tools come from tool_registry.py.
    - MCP server definitions remain in tool_registry.json
      but are not executed yet.
    """

    llm = create_llm(
        model_name=agent_definition.model_name
    )

    tools = get_tools(
        tool_names
    )

    system_prompt = f"""
You are an AI agent running inside
an Agentic AI Platform.

Agent Name:
{agent_definition.name}

Purpose:
{agent_definition.purpose}

Goal:
{agent_definition.goal}

Instructions:
{agent_definition.system_prompt}

Rules:

1. Understand the user's request.

2. Work toward the configured goal.

3. Use an assigned tool when appropriate.

4. Only use the tools provided to you.

5. Never claim that you used a tool
   unless you actually executed it.

6. If you do not have the capability
   required by the user, explain that
   clearly.

7. Respond naturally and clearly.
"""

    runtime_agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )

    return runtime_agent