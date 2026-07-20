"""Minimal expression evaluator over gate-emitted frames (SPEC-52WH-01 Stage 2).

qlib lesson (plan_52wh.md B1): signal rules are expression STRINGS, not prose —
the string is the artifact that gets hashed into the frozen spec. This module
is the only interpreter those strings run through.

Grammar (anything else is a hard ``ExprError`` — no silent prose rules):
- field names — columns of the input panel (e.g. ``close``, ``high``);
- ``ref(x, n)`` — value of ``x`` n periods ago (per symbol);
- ``rolling_max(x, n)`` / ``rolling_min(x, n)`` — trailing n-period extreme,
  full window required (NaN until n observations exist);
- ``rolling_mean(x, n)`` / ``rolling_std(x, n)`` / ``rolling_sum(x, n)`` —
  trailing n-period moment, same full-window rule (SPEC-SRA-01 §6);
- ``cs_rank(x)`` — cross-sectional percentile rank (0, 1] per date;
- ``x > y``, ``<``, ``>=``, ``<=`` — indicator, 1.0/0.0, NaN-preserving;
- ``+ - * /``, unary minus, numeric literals, parentheses.

Input is a long panel (one row per date x symbol); evaluation happens on wide
frames (index = date, columns = symbol) and returns one.

NaN POLICY (deliberate, and the most important thing in this module)
--------------------------------------------------------------------
Every rolling primitive uses ``min_periods=n``: the full window is required and
the result is NaN until n observations exist. This is uniform across ALL rolling
functions — a partial-window value would silently change what a frozen spec's
expression string means depending on where in the sample it is evaluated.

The consequence is severe and was paid for once already (see CLAUDE.md TRAP 1):
a SINGLE NaN anywhere in the trailing window blocks the entire window. In
C1-52WH-0001, 132 holiday-placeholder rows (0.005% of the panel) NaN-poisoned the
wide pivot for every other symbol and starved three rebalances to zero ranked
names. The fix belongs UPSTREAM — ``build_price_panel.drop_non_trading_dates``
plus the signal-starvation hard stop in ``backtest_52wh`` — NOT here. Loosening
``min_periods`` would hide that class of defect instead of surfacing it, and
would silently alter the meaning of SPEC-52WH-01's already-frozen expression.

Comparisons preserve NaN rather than collapsing it to False. Plain pandas
``NaN > NaN`` is ``False``, which would convert missing data into a valid 0.0
observation — the same silent-corruption failure mode in a different costume. An
indicator over an unknown price is unknown, so it stays NaN and propagates.
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


def _rolling_mean(x: pd.DataFrame, n: int) -> pd.DataFrame:
    return x.rolling(n, min_periods=n).mean()


def _rolling_std(x: pd.DataFrame, n: int) -> pd.DataFrame:
    # ddof=1 (sample std), pinned explicitly rather than left to a pandas default
    # that could drift across versions and silently restate a frozen expression.
    return x.rolling(n, min_periods=n).std(ddof=1)


def _rolling_sum(x: pd.DataFrame, n: int) -> pd.DataFrame:
    return x.rolling(n, min_periods=n).sum()


def _cs_rank(x: pd.DataFrame) -> pd.DataFrame:
    return x.rank(axis=1, pct=True)


# name -> (callable, number of frame args, number of int args)
_FUNCS = {
    "ref": (_ref, 1, 1),
    "rolling_max": (_rolling_max, 1, 1),
    "rolling_min": (_rolling_min, 1, 1),
    "rolling_mean": (_rolling_mean, 1, 1),
    "rolling_std": (_rolling_std, 1, 1),
    "rolling_sum": (_rolling_sum, 1, 1),
    "cs_rank": (_cs_rank, 1, 0),
}

_BINOPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
}

_CMPOPS = {
    ast.Gt: lambda a, b: a > b,
    ast.Lt: lambda a, b: a < b,
    ast.GtE: lambda a, b: a >= b,
    ast.LtE: lambda a, b: a <= b,
}


def _compare(op, a, b):
    """Indicator 1.0/0.0 that PRESERVES NaN (see module NaN policy).

    ``NaN > NaN`` is False in pandas, which would turn a missing observation into
    a valid zero. Anywhere either operand is missing, the indicator is unknown,
    so the result is NaN and propagates to whatever consumes it.
    """
    a_df, b_df = isinstance(a, pd.DataFrame), isinstance(b, pd.DataFrame)
    if not (a_df or b_df):
        raise ExprError("comparison needs at least one field expression operand")
    try:
        res = op(a, b).astype("float64")
    except ValueError as e:  # differently-labeled frames
        raise ExprError(f"cannot compare misaligned frames: {e}") from e

    missing = None
    if a_df:
        missing = a.isna()
    if b_df:
        missing = b.isna() if missing is None else (missing | b.isna())
    # fill_value=True: anything the mask cannot speak for is treated as unknown.
    missing = missing.reindex(index=res.index, columns=res.columns, fill_value=True)
    return res.mask(missing)


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
        if isinstance(node, ast.Compare):
            if len(node.ops) != 1 or len(node.comparators) != 1:
                raise ExprError(
                    f"chained comparisons are not in the grammar: {expr!r}"
                )
            if type(node.ops[0]) not in _CMPOPS:
                raise ExprError(
                    f"unsupported comparison operator in expression {expr!r}"
                )
            return _compare(
                _CMPOPS[type(node.ops[0])], walk(node.left), walk(node.comparators[0])
            )
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
