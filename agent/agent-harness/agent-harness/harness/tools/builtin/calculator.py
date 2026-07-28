"""Builtin tool: safe arithmetic calculator via an AST whitelist (no eval)."""
from __future__ import annotations

import ast
import operator
from typing import Callable

from harness.tools import tool

_BIN_OPS: dict[type, Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS: dict[type, Callable] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_MAX_POW_EXPONENT = 10_000


def _eval_node(node: ast.AST):
    """Recursively evaluate a whitelisted arithmetic AST node."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise ValueError(f"unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported operator: {type(node.op).__name__}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_POW_EXPONENT:
            raise ValueError("exponent too large")
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported unary operator: {type(node.op).__name__}")
        return op(_eval_node(node.operand))
    raise ValueError(f"unsupported expression element: {type(node).__name__}")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression and return the result.

    Supports numbers, the operators + - * / // % **, unary +/- and
    parentheses. Anything else is rejected.

    Args:
        expression: The arithmetic expression to evaluate, e.g. "6*7" or "(1+2)**3".
    """
    tree = ast.parse(expression, mode="eval")
    value = _eval_node(tree)
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)
