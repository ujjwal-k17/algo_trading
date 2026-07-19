"""Acceptance tests for src/pit_universe.py (Stage 1, plan_52wh.md): as-of
queries return the pre-announcement state; synthetic look-ahead rows are
invisible; rows announced on/after the seal cutoff are gate-stripped."""

import pandas as pd
import pytest

from src import pit_universe


def corpus() -> pd.DataFrame:
    rows = [
        # symbol, field, effective, announce, value
        ("ALPHA", "mcap_rank", "2019-06-30", "2019-07-20", 150),
        ("BETA", "mcap_rank", "2019-06-30", "2019-07-20", 300),
        # H2-2019 list: announced 2020-01-20 — a look-ahead row for any
        # query date before that, despite the earlier effective date.
        ("ALPHA", "mcap_rank", "2019-12-31", "2020-01-20", 250),
        ("GAMMA", "mcap_rank", "2019-12-31", "2020-01-20", 800),
        # Announced after the seal cutoff: research-invisible forever.
        ("BETA", "mcap_rank", "2024-06-30", "2024-07-20", 50),
        # Index membership add then drop.
        ("DELTA", "index_member:NIFTY500", "2019-09-30", "2019-08-23", 1),
        ("DELTA", "index_member:NIFTY500", "2020-03-31", "2020-02-21", 0),
    ]
    return pd.DataFrame(
        rows, columns=["symbol", "field", "effective_date", "announce_date", "value"]
    ).assign(source="synthetic")


def test_pre_announcement_state_returned():
    # 2020-01-10: H2 list already effective (2019-12-31) but not yet
    # announced (2020-01-20) — the H1 state must come back.
    snap = pit_universe.snapshot_as_of(corpus(), "2020-01-10", "mcap_rank")
    assert snap["ALPHA"] == 150
    assert "GAMMA" not in snap.index


def test_look_ahead_row_invisible_then_visible():
    assert pit_universe.universe_as_of(corpus(), "2020-01-10", (201, 1000)) == ["BETA"]
    assert pit_universe.universe_as_of(corpus(), "2020-02-01", (201, 1000)) == [
        "ALPHA", "BETA", "GAMMA",
    ]


def test_string_band_equals_tuple_band():
    assert pit_universe.universe_as_of(
        corpus(), "2020-02-01", "201-1000"
    ) == pit_universe.universe_as_of(corpus(), "2020-02-01", (201, 1000))


def test_sealed_announce_row_stripped_even_for_late_query():
    # Announced 2024-07-20 >= cutoff: invisible even as of 2025.
    snap = pit_universe.snapshot_as_of(corpus(), "2025-01-01", "mcap_rank")
    assert snap["BETA"] == 300


def test_final_test_env_opens_sealed_rows(monkeypatch, capsys):
    monkeypatch.setenv("FINAL_TEST", "1")
    snap = pit_universe.snapshot_as_of(corpus(), "2025-01-01", "mcap_rank")
    assert snap["BETA"] == 50
    assert "SEALED HOLDOUT IS OPEN" in capsys.readouterr().err


def test_index_membership_lifecycle():
    u = pit_universe.universe_as_of
    assert u(corpus(), "2019-09-15", "NIFTY500") == []  # announced, not effective
    assert u(corpus(), "2019-10-01", "NIFTY500") == ["DELTA"]
    assert u(corpus(), "2020-03-31", "NIFTY500") == []  # drop effective


def test_validate_rejects_bad_schema():
    with pytest.raises(ValueError, match="missing columns"):
        pit_universe.validate(pd.DataFrame({"symbol": ["A"]}))
    bad = corpus().assign(announce_date="not-a-date")
    with pytest.raises(Exception):
        pit_universe.validate(bad)


def test_empty_band_raises():
    with pytest.raises(ValueError, match="empty rank band"):
        pit_universe.universe_as_of(corpus(), "2020-02-01", (1000, 201))
