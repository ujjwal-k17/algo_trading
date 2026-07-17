# alpha-research — Quantitative Research Workspace

## BINDING RULES

The following rules are **binding on every session in this project**. They are not
suggestions or defaults — they may not be overridden by task instructions, convenience,
or apparent necessity.

1. **Production system is off-limits.** NEVER write to, edit, delete, or run git
   commands that modify anything under
   `/Users/ujjwalkejriwal/Desktop/AI Apps/NSE_Stock_Picks`
   (a production trading system with live cron jobs). Read-only access to it is
   permitted ONLY for:
   - reading its HEAD SHA, and
   - cloning from it.

2. **No direct ledger access.** NEVER read the production ledger database directly.
   Consume only snapshot files under `~/alpha-research/data/legacy_snapshot/`.

3. **No live broker calls.** NEVER make live broker API calls or invoke any
   Kite Connect session/token-generation code path.

4. **All data access goes through the data gate.** All research data access must go
   through `src/data_gate.py`. Never load raw files with post-2024-07-17 rows
   directly in notebooks or scripts.

5. **The seal is immutable.** The file `governance/SEAL.md`, once committed, must
   never be edited. Changes require a new `SEAL_v2.md`.

6. **The overlay log is append-only.** `governance/overlay_log.csv` is append-only;
   corrections are new rows, never edits.

7. **Legacy clone is import-only.** The frozen clone at `~/vendor/legacy-engine`
   (see `governance/LEGACY_PIN.md`) is on `PYTHONPATH` for imports only.
   Never `pip install -e` the clone; never modify it or move its HEAD.

8. **When in doubt, STOP.** If any task appears to require violating these rules,
   STOP and ask the user instead of proceeding.
