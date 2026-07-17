# Legacy Engine Pin

Read-only bridge to the production system's code, frozen at a fixed commit.

| Field | Value |
|---|---|
| Source repo | `/Users/ujjwalkejriwal/Desktop/AI Apps/NSE_Stock_Picks` |
| Pinned SHA | `ee7ad13228244f4f27e3d2d839baf70897ff24fe` |
| Pinned commit subject | `prereg: fill commit-at-registration hash (dcee923)` |
| Clone location | `~/vendor/legacy-engine` (detached HEAD at pinned SHA) |
| Clone date | 2026-07-17 |
| Clone method | `git clone --no-hardlinks` (no shared inodes with production) |
| Freeze method | `chmod -R a-w ~/vendor/legacy-engine` (whole tree incl. `.git`) |

## Usage rules

- Import-only: the clone is on `PYTHONPATH` via `.venv/bin/activate`.
  **Never `pip install -e` the clone** — no install hooks, no egg-links, imports only.
- Never edit, pull, or re-checkout the clone. To move to a newer production
  commit, delete the clone, re-clone, update this file with the new SHA, and
  commit the change.
- The production repo itself remains off-limits per CLAUDE.md rule 1.
