"""Minimal expression evaluator over gate-emitted frames (SPEC-52WH-01 Stage 2).

qlib lesson (plan_52wh.md B1): signal rules are expression STRINGS, not prose —
the string is the artifact that gets hashed into the frozen spec. This module
is the only interpreter those strings run through.

Grammar (anything else is a hard ``ExprError`` — no silent prose rules):
- field names — columns of the input panel (e.g. ``close``, ``high``);
- ``ref(x, n)`` — value of ``x`` n periods ago (per symbol);
- ``rolling_max(x, n)`` / ``rolling_min(x, n)`` — trailing n-period extreme,
  full window required (NaN until n observations exist);
- ``cs_rank(x)`` — cross-sectional percentile rank (0, 1] per date;
- ``+ - * /``, unary minus, numeric literals, parentheses.

Input is a long panel (one row per date x symbol); evaluation happens on wide
frames (index = date, columns = symbol) and returns one.
"""

from __future__ import annotations

import ast

import pandas as pd


class ExprError(ValueError):
    """Raised for any token, syntax, or field outside the closed grammar."""


def _ref(x: pd.DataFrame, n: int) -> pd.DataFrame:
    return x.shift(n)


def _rolling_max(x: pd.DataFrame, n: int) -> pd.DataFrame:
    return x.rolling(n, min_periods=n).max()


def _rolling_min(x: pd.DataFrame, n: int) -> pd.DataFrame:
    return x.rolling(n, min_periods=n).min()


def _cs_rank(x: pd.DataFrame) -> pd.DataFrame:
    return x.rank(axis=1, pct=True)


# name -> (callable, number of frame args, number of int args)
_FUNCS = {
    "ref": (_ref, 1, 1),
    "rolling_max": (_rolling_max, 1, 1),
    "rolling_min": (_rolling_min, 1, 1),
    "cs_rank": (_cs_rank, 1, 0),
}

_BINOPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
}


def evaluate(
    expr: str,
    panel: pd.DataFrame,
    *,
    date_col: str = "date",
    symbol_col: str = "symbol",
) -> pd.DataFrame:
    """Evaluate ``expr`` over a long panel; return a wide (date x symbol) frame.

    Field names resolve to pivoted panel columns. Duplicate (date, symbol)
    rows, unknown fields, unknown functions, and any syntax outside the
    closed grammar raise ``ExprError``.
    """
    for col in (date_col, symbol_col):
        if col not in panel.columns:
            raise ExprError(f"panel is missing required column {col!r}")
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ExprError(f"unparseable expression {expr!r}: {e}") from e

    fields: dict[str, pd.DataFrame] = {}

    def field(name: str) -> pd.DataFrame:
        if name not in fields:
            if name not in panel.columns or name in (date_col, symbol_col):
                raise ExprError(f"unknown field {name!r} in expression {expr!r}")
            if panel.duplicated([date_col, symbol_col]).any():
                raise ExprError("panel has duplicate (date, symbol) rows")
            wide = panel.pivot(index=date_col, columns=symbol_col, values=name)
            fields[name] = wide.sort_index()
        return fields[name]

    def walk(node: ast.AST):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Name):
            return field(node.id)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise ExprError(f"non-numeric literal {node.value!r}")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -walk(node.operand)
        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            return _BINOPS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _FUNCS:
                raise ExprError(f"unknown function in expression {expr!r}")
            if node.keywords:
                raise ExprError("keyword arguments are not in the grammar")
            fn, n_frames, n_ints = _FUNCS[node.func.id]
            args = [walk(a) for a in node.args]
            if len(args) != n_frames + n_ints:
                raise ExprError(
                    f"{node.func.id} takes {n_frames + n_ints} args, got {len(args)}"
                )
            for a in args[:n_frames]:
                if not isinstance(a, pd.DataFrame):
                    raise ExprError(f"{node.func.id}: expected a field expression arg")
            for a in args[n_frames:]:
                if not isinstance(a, int):
                    raise ExprError(f"{node.func.id}: window/periods arg must be an int")
            return fn(*args)
        raise ExprError(
            f"disallowed syntax {type(node).__name__} in expression {expr!r}"
        )

    result = walk(tree)
    if not isinstance(result, pd.DataFrame):
        raise ExprError(f"expression {expr!r} reduces to a scalar, not a panel")
    return result
