"""Walk-forward engine for SPEC-52WH-01 (Stage 5, plan_52wh.md).

THIS IS THE CONTAMINATION BOUNDARY. Stages 1-3 are features-only by
construction; this module is where returns are joined to signals. It therefore
refuses to run without a provenance stamp from ``spec_guard.preflight`` — a
frozen-spec hash match plus a pre-registered trial row. Importing it is free;
running it is a registered trial.

What it measures (spec §3): the effect of the NEGATIVE SCREEN on a naive
equal-weighted band book — screened vs unscreened, same universe, same dates,
same costs. The unscreened book is the control, not a strawman; the claim is
strictly the increment.

Conventions, all deliberate and all reportable:

* Signal is computed on the rebalance date; the trade executes at the close of
  the NEXT trading session (spec §5, no same-bar look-ahead). Costs hit that
  session's return; new weights apply from the session after.
* Weights DRIFT between rebalances (buy-and-hold). Turnover is measured against
  the drifted book, not the previous target — measuring target-to-target would
  understate churn and flatter the cost line.
* A held symbol with no price on a day is FROZEN at a 0% return and force-exited
  at the next rebalance. Delistings in this panel skew toward the far-from-high
  bucket the screen excludes, so freezing at zero is conservative for the
  UNSCREENED control (it should have taken the loss) — i.e. it understates the
  screen's benefit. Counted in ``diagnostics['frozen_symbol_days']`` and it must
  be reported, not buried.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src import costs_in, pit_universe, rebalance, screen_52wh, signal_52wh

LOOKBACK = 252  # trading days of highs the nearness expression needs
PIT_FIRST_SAFE = pd.Timestamp("2018-01-25")  # earliest announce-safe PIT date (A1)
DEFAULT_BOOK_VALUE = 1e7  # ₹1 Cr nominal; only the flat DP charge is size-sensitive


@dataclass
class BacktestResult:
    """One arm of the comparison (screened or unscreened)."""

    label: str
    gross_returns: pd.Series
    net_returns: pd.Series
    turnover: pd.Series           # one-way, per rebalance
    costs: pd.Series              # cost as a fraction of book value, per rebalance
    n_holdings: pd.Series         # per rebalance
    diagnostics: dict = field(default_factory=dict)

    @property
    def annual_turnover(self) -> float:
        """One-way turnover annualized over the realised span (spec §5 budget)."""
        if self.turnover.empty:
            return 0.0
        span_days = (self.turnover.index[-1] - self.turnover.index[0]).days
        years = max(span_days / 365.25, 1e-9)
        return float(self.turnover.sum()) / years


def _require_stamp(stamp) -> dict:
    """Re-verify rather than trust: a hand-built dict must not open this door."""
    from src import spec_guard

    if not isinstance(stamp, dict) or "spec_id" not in stamp or "trial_id" not in stamp:
        raise spec_guard.SpecGuardError(
            "backtest requires a provenance stamp from spec_guard.preflight() — "
            "returns may not be joined to signals outside a registered trial "
            "(CONTAMINATION_POLICY.md AMENDMENT A)."
        )
    fresh = spec_guard.preflight(stamp["spec_id"], stamp["trial_id"])
    if stamp.get("spec_sha256") not in (None, fresh["spec_sha256"]):
        raise spec_guard.SpecGuardError("stamp hash does not match the frozen spec")
    return fresh


def _wide(panel: pd.DataFrame, col: str) -> pd.DataFrame:
    return panel.pivot_table(index="date", columns="symbol", values=col, aggfunc="last")


def _cost_fraction(deltas: pd.Series, book_value: float, slippage_per_side: float) -> float:
    """Rupee cost of one rebalance, expressed as a fraction of book value."""
    buy_value = float(deltas[deltas > 0].sum()) * book_value
    sell_value = float(-deltas[deltas < 0].sum()) * book_value
    if buy_value <= 0 and sell_value <= 0:
        return 0.0
    n_scrips_sold = int((deltas < 0).sum())
    total = 0.0
    if buy_value > 0:
        total += costs_in.delivery_leg("buy", buy_value)["total"]
    if sell_value > 0:
        total += costs_in.delivery_leg("sell", sell_value,
                                       dp_scrip_days=n_scrips_sold)["total"]
    total += slippage_per_side * (buy_value + sell_value)
    return total / book_value


def _target_weights(
    signal: pd.DataFrame,
    tradeable: list[str],
    *,
    screened: bool,
    exclude_buckets: tuple[str, ...],
    unranked_policy: str,
) -> pd.Series:
    if not tradeable:
        return pd.Series(dtype=float)
    ew = pd.Series(1.0 / len(tradeable), index=sorted(tradeable))
    if not screened:
        return ew
    out = screen_52wh.screen_book(
        signal, ew, exclude_buckets=exclude_buckets, unranked_policy=unranked_policy
    )
    return out.loc[out["weight_out"] > 0, "weight_out"]


def _simulate(
    label: str,
    dates: pd.DatetimeIndex,
    returns_wide: pd.DataFrame,
    targets: dict,
    *,
    book_value: float,
    slippage_per_side: float,
) -> BacktestResult:
    """Daily loop over one arm. ``targets`` maps execution date -> target weights."""
    weights = pd.Series(dtype=float)
    gross, net = {}, {}
    turnover_log, cost_log, holdings_log = {}, {}, {}
    frozen_symbol_days = 0

    for day in dates:
        # 1. Earn the day on the book held at the open of this session.
        if weights.empty:
            r_gross = 0.0
        else:
            r = returns_wide.loc[day].reindex(weights.index)
            frozen_symbol_days += int(r.isna().sum())
            r = r.fillna(0.0)  # frozen: no price today, position held flat
            r_gross = float((weights * r).sum())
            grown = weights * (1.0 + r)
            total = float(grown.sum())
            weights = grown / total if total > 0 else grown

        # 2. Rebalance at this session's close, if scheduled.
        cost = 0.0
        if day in targets:
            target = targets[day]
            deltas = rebalance.trades(weights if not weights.empty else None, target)
            cost = _cost_fraction(deltas, book_value, slippage_per_side)
            turnover_log[day] = rebalance.turnover(
                weights if not weights.empty else None, target
            )
            cost_log[day] = cost
            holdings_log[day] = int(len(target))
            weights = target.copy()

        gross[day] = r_gross
        net[day] = r_gross - cost

    return BacktestResult(
        label=label,
        gross_returns=pd.Series(gross, name=f"{label}_gross").sort_index(),
        net_returns=pd.Series(net, name=f"{label}_net").sort_index(),
        turnover=pd.Series(turnover_log, name="turnover", dtype=float).sort_index(),
        costs=pd.Series(cost_log, name="cost_frac", dtype=float).sort_index(),
        n_holdings=pd.Series(holdings_log, name="n_holdings", dtype="Int64").sort_index(),
        diagnostics={"frozen_symbol_days": frozen_symbol_days},
    )


def run_walk_forward(
    panel: pd.DataFrame,
    pit_store: pd.DataFrame,
    *,
    stamp: dict,
    band: str = "201-1000",
    freq: str = "Q",
    exclude_buckets: tuple[str, ...] = ("Q1",),
    unranked_policy: str = "keep",
    n_buckets: int = signal_52wh.N_BUCKETS,
    weighting: str = "EW",
    book_value: float = DEFAULT_BOOK_VALUE,
    slippage_per_side: float = costs_in.SLIPPAGE_FLOOR_PER_SIDE,
    verbose: bool = True,
) -> dict:
    """Run the screened-vs-unscreened walk-forward. Returns both arms + a schedule.

    ``panel`` must already have passed ``data_gate.load`` (the caller's job —
    the runner does it). ``stamp`` comes from ``spec_guard.preflight``.
    """
    _require_stamp(stamp)

    if weighting.upper() == "MW":
        raise NotImplementedError(
            "market-cap weighting needs ABSOLUTE mcap, which the PIT store does "
            "not carry — data/reference/pit/staging kept mcap_rank only, dropping "
            "the AMFI average-mcap column. Re-ingest that column before claiming "
            "the spec §7 EW-vs-MW sensitivity; a rank-derived proxy would be an "
            "invented number."
        )
    if weighting.upper() != "EW":
        raise ValueError(f"weighting must be 'EW' (or 'MW', blocked), got {weighting!r}")

    close = _wide(panel, "close")
    returns_wide = close.pct_change()
    nearness = signal_52wh.nearness_panel(panel)  # computed ONCE, sliced per date
    dates = close.index.sort_values()

    all_rebal = rebalance.rebalance_dates(dates, freq)
    warmup_ok = dates[LOOKBACK - 1] if len(dates) >= LOOKBACK else None
    if warmup_ok is None:
        raise ValueError(f"panel has < {LOOKBACK} sessions — nearness never defined")
    floor = max(warmup_ok, PIT_FIRST_SAFE)
    rebal_dates = [d for d in all_rebal if d >= floor and d in nearness.index]
    if not rebal_dates:
        raise ValueError(f"no rebalance dates at/after {floor.date()}")

    targets_screened, targets_unscreened = {}, {}
    schedule = []
    for t in rebal_dates:
        pos = dates.get_loc(t)
        if pos + 1 >= len(dates):
            continue  # no next session to execute in; drop the final stub
        exec_day = dates[pos + 1]

        universe = pit_universe.universe_as_of(pit_store, t, band)
        signal = signal_52wh.rank_row(nearness.loc[t], universe, n_buckets=n_buckets)
        # Tradeable = in the PIT band AND priced on the execution day.
        priced = set(close.loc[exec_day].dropna().index)
        tradeable = sorted(set(universe) & priced)

        targets_unscreened[exec_day] = _target_weights(
            signal, tradeable, screened=False,
            exclude_buckets=exclude_buckets, unranked_policy=unranked_policy,
        )
        targets_screened[exec_day] = _target_weights(
            signal, tradeable, screened=True,
            exclude_buckets=exclude_buckets, unranked_policy=unranked_policy,
        )
        schedule.append({
            "signal_date": t,
            "exec_date": exec_day,
            "pit_universe": len(universe),
            "ranked": int(len(signal)),
            "tradeable": len(tradeable),
            "screened_holdings": int(len(targets_screened[exec_day])),
        })
        if verbose:
            print(f"  {t.date()} -> exec {exec_day.date()}: PIT {len(universe)}, "
                  f"ranked {len(signal)}, tradeable {len(tradeable)}, "
                  f"screened {len(targets_screened[exec_day])}")

    if not schedule:
        raise ValueError("no executable rebalances")

    sim_dates = dates[dates >= schedule[0]["exec_date"]]
    arms = {}
    for label, targets in (("unscreened", targets_unscreened), ("screened", targets_screened)):
        arms[label] = _simulate(
            label, sim_dates, returns_wide, targets,
            book_value=book_value, slippage_per_side=slippage_per_side,
        )

    return {
        "arms": arms,
        "schedule": pd.DataFrame(schedule),
        "params": {
            "band": band, "freq": freq, "exclude_buckets": list(exclude_buckets),
            "unranked_policy": unranked_policy, "n_buckets": n_buckets,
            "weighting": weighting, "book_value": book_value,
            "slippage_per_side": slippage_per_side,
            "first_exec": str(schedule[0]["exec_date"].date()),
            "last_date": str(sim_dates[-1].date()),
        },
    }
