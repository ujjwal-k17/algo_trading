# PRE-REGISTRATION — Legacy Book A/B (Recommended vs Executed)

Registered 2026-07-18, before the legacy live window closes. Machinery:
`src/overlay_alpha.py` (decision-time vs RECONSTRUCTED provenance enforced in
code), `data/derived/paper_leg.parquet` (recommended leg), overlay log.

**Read date: 2026-09-27** (90 days from live-window start 2026-06-29).
Peeking before the read date is permitted; **acting, re-tuning, or
re-registering because of a peek is a protocol breach and must be logged as
one.**

## The four analyses

1. **Recommended-leg NAV alpha.** Daily paper-leg NAV vs the appropriate
   midcap **TRI**, net of SOP-fill costs.
   H0: alpha = 0.
   **Evidential ceiling:** a statistically significant result (t ≥ 2) earns
   exactly ONE pre-registered forward re-test of the family — it does NOT
   overturn the design-level cost verdict (statutory cost at the system's
   turnover exceeds gross alpha; the kill is arithmetic, not statistical).

2. **Overlay-alpha, decision-time scope only.** Executed − recommended,
   per-trade ΔR and daily NAV difference.
   H0: overlay adds 0.
   RECONSTRUCTED scope is reported separately and NEVER merged (enforced:
   `weekly_summary` raises on mixed provenance). Overlay is veto/reduce only;
   any analysis implying added trades or up-sizing is out of protocol.

3. **Veto quality.** Distribution of recommended-leg outcomes on vetoed recs
   vs executed recs.
   H0: vetoed recs' paper outcomes are not worse than executed recs' —
   i.e. the veto filter adds nothing.

4. **Reduce efficacy.** R saved per unit of size reduction on REDUCE rows.
   H0: reduction sizing is uninformative (R saved = 0 per unit reduced).

## Scope discipline

- Executed-leg evidence is evidence about the OVERLAY, never about the system.
- The recommended (paper) leg is the system's only clean forward evidence.
- The 16-day green tape at registration time is luck-compatible and is cited
  as evidence of nothing.
- Analyses 2–4 require decision-time overlay rows; n = 0 until logging starts.
  Reconstruction cannot substitute (zero inferable vetoes — see DECISIONS.md).
