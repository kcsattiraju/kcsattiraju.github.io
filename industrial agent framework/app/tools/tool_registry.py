import ast
import json
import operator
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool


# ---------------------------------------------------
# Registry configuration file
# ---------------------------------------------------

REGISTRY_FILE = (
    Path(__file__).parent
    / "tool_registry.json"
)


# ---------------------------------------------------
# Load registry
# ---------------------------------------------------

def load_tool_registry() -> dict:
    """
    Load tool registry configuration.
    """

    with open(
        REGISTRY_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ===================================================
# LOCAL TOOLS
# ===================================================


@tool
def calculator(expression: str) -> str:
    """
    Perform a mathematical calculation.

    Example:
    125 * 24
    """

    try:
        return str(
            _safe_calculate(expression)
        )

    except Exception as error:

        return (
            f"Unable to calculate "
            f"'{expression}': {error}"
        )


@tool
def current_datetime() -> str:
    """
    Return the current local date and time.
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ---------------------------------------------------
# Safe calculator implementation
# ---------------------------------------------------

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_calculate(
    expression: str,
):
    """
    Safely evaluate a basic mathematical expression.
    """

    parsed = ast.parse(
        expression,
        mode="eval",
    )

    return _evaluate_node(
        parsed.body
    )


def _evaluate_node(node):

    if isinstance(
        node,
        ast.Constant,
    ):

        if isinstance(
            node.value,
            (int, float),
        ):

            return node.value

    if isinstance(
        node,
        ast.BinOp,
    ):

        operator_function = (
            _OPERATORS.get(
                type(node.op)
            )
        )

        if operator_function is None:
            raise ValueError(
                "Unsupported operator."
            )

        return operator_function(
            _evaluate_node(node.left),
            _evaluate_node(node.right),
        )

    if isinstance(
        node,
        ast.UnaryOp,
    ):

        operator_function = (
            _OPERATORS.get(
                type(node.op)
            )
        )

        if operator_function is None:
            raise ValueError(
                "Unsupported operator."
            )

        return operator_function(
            _evaluate_node(
                node.operand
            )
        )

    raise ValueError(
        "Unsupported expression."
    )


# ---------------------------------------------------
# Executable local tool map
# ---------------------------------------------------

LOCAL_TOOL_REGISTRY = {
    "calculator": calculator,
    "current_datetime": current_datetime,
}


def get_tools(
    tool_names: list[str],
):
    """
    Return executable local LangChain tools.

    This keeps the Phase 1 demo working.
    """

    return [
        LOCAL_TOOL_REGISTRY[name]
        for name in tool_names
        if name in LOCAL_TOOL_REGISTRY
    ]


def get_local_tool_definitions() -> list[dict]:
    """
    Return local tool metadata from JSON registry.
    """

    registry = load_tool_registry()

    return registry.get(
        "local_tools",
        [],
    )


# ===================================================
# MCP SERVER REGISTRY
# ===================================================


def get_servers() -> list[dict]:
    """
    Return configured MCP servers.
    """

    registry = load_tool_registry()

    return registry.get(
        "servers",
        [],
    )


def get_server(
    server_name: str,
) -> dict | None:
    """
    Find MCP server by name.
    """

    for server in get_servers():

        if (
            server.get("name")
            == server_name
        ):
            return server

    return None


def get_enabled_tools(
    server_name: str,
) -> list[str]:
    """
    Return enabled tools for an MCP server.
    """

    server = get_server(
        server_name
    )

    if server is None:
        return []

    return server.get(
        "enabled_tools",
        [],
    )


def find_server_for_tool(
    tool_name: str,
) -> dict | None:
    """
    Determine which MCP server provides
    the requested tool.
    """

    for server in get_servers():

        enabled_tools = (
            server.get(
                "enabled_tools",
                [],
            )
        )

        if tool_name in enabled_tools:
            return server

    return None