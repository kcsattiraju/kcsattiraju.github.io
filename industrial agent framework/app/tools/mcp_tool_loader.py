from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
)

from app.tools.tool_registry import (
    get_servers,
)


def _build_mcp_connections() -> dict:
    """
    Convert our tool_registry.json format
    into the format expected by
    MultiServerMCPClient.
    """

    connections = {}

    for server in get_servers():

        server_name = server.get("name")
        transport = server.get("transport")
        url = server.get("url")

        if not server_name:
            continue

        if not url:
            continue

        # LangChain MCP adapter currently expects
        # "http" for streamable HTTP connections.
        if transport in (
            "streamable-http",
            "streamable_http",
        ):
            transport = "http"

        connections[server_name] = {
            "transport": transport,
            "url": url,
        }

    return connections


async def get_mcp_tools(
    requested_tool_names: list[str],
):
    """
    Load MCP tools and return only the tools
    assigned to the current agent.
    """

    if not requested_tool_names:
        return []

    connections = _build_mcp_connections()

    if not connections:
        return []

    client = MultiServerMCPClient(
        connections
    )

    # Discover executable tools from MCP servers
    discovered_tools = await client.get_tools()

    requested_names = set(
        requested_tool_names
    )

    return [
        tool
        for tool in discovered_tools
        if tool.name in requested_names
    ]