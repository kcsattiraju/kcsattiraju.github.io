from app.tools.tool_registry import get_tools


print("\n================================")
print("TOOL REGISTRY TEST")
print("================================")


tool_names = [
    "search_documents"
]


tools = get_tools(
    tool_names
)


print(
    "\nRequested tools:",
    tool_names,
)

print(
    "Loaded tools:",
    [
        tool.name
        for tool in tools
    ],
)


if not tools:
    raise RuntimeError(
        "search_documents tool was not loaded."
    )


document_tool = tools[0]


question = (
    "What are possible causes "
    "of low pump pressure?"
)


result = document_tool.invoke(
    {
        "query": question
    }
)


print("\n================================")
print("RESULT")
print("================================")

print(result)


print(
    "\nCheckpoint 28 registry test completed."
)