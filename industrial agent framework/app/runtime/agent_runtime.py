from langgraph.prebuilt import create_react_agent

from app.models.llm_factory import create_llm

from app.tools.tool_registry import (
    get_tools,
)


def build_runtime_agent(
    agent,
    tool_names: list[str],
):
    """
    Build an executable LangGraph agent
    using the configuration stored in PostgreSQL.
    """

    # -----------------------------------------
    # 1. Resolve actual Python tools
    # -----------------------------------------

    tools = get_tools(
        tool_names
    )

    print()
    print(
        "Runtime agent tools:",
        [
            tool.name
            for tool in tools
        ]
    )

    # -----------------------------------------
    # 2. Determine model
    # -----------------------------------------

    model_name = getattr(
        agent,
        "model_name",
        None
    )

    llm = create_llm(
        model_name
    )

    # -----------------------------------------
    # 3. Build system prompt
    # -----------------------------------------

    agent_name = getattr(
        agent,
        "name",
        "Industrial AI Agent"
    )

    description = getattr(
        agent,
        "description",
        ""
    ) or ""

    goal = getattr(
        agent,
        "goal",
        ""
    ) or ""

    system_prompt = getattr(
        agent,
        "system_prompt",
        ""
    ) or ""

    prompt = f"""
You are {agent_name}.

Description:
{description}

Goal:
{goal}

Instructions:
{system_prompt}

You have access to the tools assigned to you.

When a user's question requires information from
industrial manuals, technical documentation,
maintenance documentation, troubleshooting guides,
or equipment procedures, use the appropriate
document retrieval tool before answering.

Do not invent information that should come from
industrial documentation.

If retrieved documentation contains source or page
information, include it in your answer when useful.
"""

    # -----------------------------------------
    # 4. Create LangGraph ReAct agent
    # -----------------------------------------

    runtime_agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt,
    )

    return runtime_agent