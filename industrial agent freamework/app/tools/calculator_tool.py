import ast
import operator

from langchain.tools import tool


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def evaluate_expression(node):

    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.BinOp):

        left = evaluate_expression(node.left)
        right = evaluate_expression(node.right)

        operation = OPERATORS.get(
            type(node.op)
        )

        if operation is None:
            raise ValueError(
                "Unsupported operator"
            )

        return operation(
            left,
            right
        )

    if isinstance(node, ast.UnaryOp):

        operand = evaluate_expression(
            node.operand
        )

        operation = OPERATORS.get(
            type(node.op)
        )

        if operation is None:
            raise ValueError(
                "Unsupported operator"
            )

        return operation(
            operand
        )

    raise ValueError(
        "Unsupported expression"
    )


@tool
def calculator(expression: str) -> str:
    """
    Perform mathematical calculations.

    Use this tool when the user asks
    for arithmetic calculations.
    """

    try:

        parsed = ast.parse(
            expression,
            mode="eval"
        )

        result = evaluate_expression(
            parsed.body
        )

        return str(result)

    except Exception as exc:

        return (
            f"Calculation failed: {exc}"
        )