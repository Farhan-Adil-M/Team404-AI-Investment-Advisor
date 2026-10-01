# DESIGN.md — Team404 AI Investment Advisor (P2 artifact)

**Stack:** Streamlit 1.64 + yfinance 1.7 + pandas 3.0 + plotly 7 · Python 3.14 · venv `.venv`
**Runtime AI:** deterministic rule-engine (RULES #18 — no LLM key, demo-safe). "AI" = data-driven
analysis + templated natural-language explanations. Real market data via yfinance everywhere.

## Problem-step traceability (RULES #6)

| Problem Step | Module | File |
|---|---|---|
| 1 Profile input | rich intake (age/income/goals/willingness + budget/experience/background/loss) | `app.py` (step 1) → `engine/planner.py` rules |
| 2 AI background & loss analysis | `loss_analyzer` — detect cause from market data | `engine/loss_analyzer.py` |
| 3 Risk assessment | Yes/No + capacity-vs-willingness binding (`min()` rule) | `app.py` (step 3) + `planner.risk_profile` |
| 4 Personalized recommendation | `planner` (recommended + custom dual plan) / `recommender` (high-risk) / `sip_planner` (low-risk) | `engine/planner.py`, `engine/recommender.py`, `engine/sip.py` |
| 5 Ongoing optimizer | `optimizer` — monthly signals from live data | `engine/optimizer.py` |

**Planner rules (R5 research):** 110−age equity glide (clamp 30–90%) · goal buckets
(<3y / 3-7y / 7-15y / 15y+) · SIP capacity 20–40% of income · emergency-fund gate (3/6 months,
fund-before-invest) · risk binding = min(capacity, willingness) · custom-plan guard warnings ·
illustrative rates equity 12% / debt 8% / gold 9% / crypto 15% / cash 6% (labeled assumptions).

## Data layer (`engine/market.py`)
- `fetch(sym, period)` → DataFrame, 3-retry w/ backoff; on total failure → returns `None` and UI
  shows **"simulated"**-labeled deterministic fallback (RULES #5).
- Verified tickers (P0 probe, all live): SPY, QQQ, AAPL, NVDA, GC=F (gold), BTC-USD, ETH-USD,
  ^NSEI, RELIANCE.NS, GLD, BIL (safe), ^TNX (yield).
- Signals computed: drawdown%, annualized vol, CAGR, "bought-at-peak" (buy price vs 90d max),
  "panic-sold" (sell vs prior 30d drawdown), concentration (share of one asset in history).

## Loss analysis (Step 2) — taxonomy
`PEAK_BUY` · `PANIC_SELL` · `CONCENTRATION` · `HYPE_CHASE` · `HOLD_THROUGH_CRASH` · `MISMATCH_RISK`
→ each yields: detected? + evidence numbers + beginner-friendly explanation string.
Experience dial: Beginner → shorter sentences + glossary; Experienced → numbers-first.

## Risk router (Steps 3–4)
- **Yes (high-risk):** aggressive allocation scaled by experience
  (Beginner 50/25/10/15, Intermediate 60/20/15/5, Experienced 70/15/10/5 → equity/gold/crypto/safe),
  top picks from live momentum + volatility stats, each with reasoning + disclaimer.
- **No (low-risk):** SIP plan — lumpsum + monthly amount, conservative 9% / moderate 12% scenarios,
  3/5/10y projections (FV formula), best-month/day-to-invest from historical month returns,
  monthly reminder text.

## Optimizer (Step 5)
Recompute monthly: market dip >5% since last check → "invest more" top-up signal · allocation drift
>5pp → rebalance · vol spike → hold recommendation. All from live fetch at app start (cached 1h).

## UI flow (5 screens, session-state wizard)
`1 Profile → 2 Loss analysis (if any) → 3 Risk question → 4 Plan (tabbed: High-risk | SIP) → 5 Optimizer`
+ sidebar: data freshness stamp, "live vs simulated" badge, disclaimer footer (Impact points).

## Gates
- P3 build order: `market.py` → `loss_analyzer.py` → `recommender.py`+`sip.py` → `optimizer.py` → `app.py`
- Each module RUN-OR-BAN tested standalone before next.
- P4: 3 personas end-to-end at 3:00 PM gate.
