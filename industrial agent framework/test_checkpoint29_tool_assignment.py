from app.tools.tool_registry import get_tools


print("\n========================================")
print("CHECKPOINT 29")
print("AGENT TOOL ASSIGNMENT VERIFICATION")
print("========================================")


# --------------------------------------------------
# SIMULATE WHAT THE DATABASE RETURNS
# --------------------------------------------------
#
# Eventually ToolRepository.get_agent_tools(agent_id)
# will give the runtime these tool names.
#
# For this checkpoint test we first prove that the
# DB-style tool name can be dynamically resolved.

assigned_tool_names = [
    "search_documents"
]


print(
    "\nTools assigned to agent:",
    assigned_tool_names,
)


# --------------------------------------------------
# LOAD ACTUAL PYTHON TOOLS FROM REGISTRY
# --------------------------------------------------

tools = get_tools(
    assigned_tool_names
)


print(
    "\nRuntime tools loaded:",
    [
        tool.name
        for tool in tools
    ],
)


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

if not tools:
    raise RuntimeError(
        "No runtime tools were loaded."
    )


if tools[0].name != "search_documents":
    raise RuntimeError(
        "search_documents was not resolved correctly."
    )


print(
    "\nTool registry resolution: SUCCESS"
)


# --------------------------------------------------
# TEST THE RESOLVED TOOL
# --------------------------------------------------

question = (
    "What should I inspect when "
    "P-101 has low discharge pressure?"
)


print(
    "\nCalling dynamically loaded tool..."
)


result = tools[0].invoke(
    {
        "query": question
    }
)


print("\n========================================")
print("TOOL RESULT")
print("========================================")

print(result)


print(
    "\nCheckpoint 29 registry/runtime test passed."
)