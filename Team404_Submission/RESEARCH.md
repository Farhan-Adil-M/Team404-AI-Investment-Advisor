# RESEARCH.md — P1 findings (Team404 researcher agents R1/R2/R3)

Spawns: R1 `nemotron-3.5-lightning-free` (model comparison) · R2 `longcat-2.5-preview-free` (yfinance) ·
R3 `ling-3.0-flash-fin-free` → *provider outage* → re-spawned on `mimo-v2.6-flash-free` (RULES #17 log).
All free tier, zero cost. Orchestrator verified key claims against live data (P0 probe).

## R1 — Which free agent for which role (selector basis)

| Role | Top pick | Backup | Notes |
|---|---|---|---|
| Web/market research | **longcat-2.5-preview-free** (1M ctx) | nemotron-3.5-lightning-free (MMLU-Pro 81.94) | space-bunny free window may expire (~1 wk); anonymous model = transparency risk |
| Python code | **longcat-2.5-preview-free** | space-bunny-free | `mimo-v2.6-flash-free` rated weaker at coding — paid `mimo-v2.6-flash` ($0.14) preferred for code |
| Finance reasoning | **ling-3.0-flash-fin-free** (Ant Group, finance-tuned) | big-pickle (likely GLM-4.6) | ⚠ ling endpoint was down during our run — verify availability before relying on it |

All free tiers are "limited time" — no expiry guarantees. Heavy models remain banned (RULES #15).

## R2 — yfinance implementation facts (verified 2026-10-01)

- **yfinance 1.7.0** (installed) · use `history(period, interval, auto_adjust=True)`; avoid `info`/`fast_info`
  (web-scraped, flaky). Rate-limit 429 → retry w/ backoff (matches `market.fetch`).
- **Ticker verification (our P0 probe, all live ✅):** SPY, QQQ, AAPL, NVDA, GC=F, GLD, BTC-USD, ETH-USD,
  ^NSEI, RELIANCE.NS, BIL, ^TNX.
- **Indian mutual fund NAVs broken** (`0P00000437.BO` → 404) → SIP backbone = **^NSEI proxy** (as designed).
- Formulas confirmed: CAGR, annualized vol (std·√252), max drawdown (cummax), SIP FV — all implemented
  and unit-tested in `engine/market.py`.

## R3 — Financial rule-engine logic

- **Loss taxonomy (8):** PEAK_BUY (entry ≥97% of 252d max) · PANIC_SELL (exit ≤90% of 30d avg,
  recovery within 60d) · CONCENTRATION (>25% one asset) · HYPE_CHASE (buy after 20d rally >30% +
  volume spike) · HOLD_THROUGH_CRASH (no exit rule, >25% adverse move) · MISMATCH_RISK (asset σ >
  profile band) · OVER_TRADING · CUT_WINNERS_TOO_EARLY. → report top causes with confidence.
- **Risk matrix:** willingness ∧ experience, **downshift Beginner+Yes → moderate** (enthusiasm ≠ capacity).
  Conservative 30/45/20/0/5 · Moderate 55/20/15/5/5 · Aggressive 75/5/10/8/2 (equity/bonds/gold/crypto/cash).
- **SIP math:** `FV = P·[((1+i)^n−1)/i]·(1+i)`. ₹10k/mo 10y ≈ ₹18.4L@8% … ₹24.7L@13%. Never "guaranteed".
- **Best-time evidence labels:** turn-of-month = Medium · buy-the-dip >5% = Medium (but lumpsum-now wins
  ~2/3) · day-of-week = Low (don't use) · claims forbidden: "markets always recover", fixed targets.
- **Optimizer signals:** dip trigger ≤−5% vs last check → top-up 10-20% in 2-3 tranches · drift >5pp →
  rebalance · vol spike >22% → pause lumpsum · YTD<0 + SIP active → step-up nudge.

## Orchestrator validations (live)
- SPY 2y: drawdown −18.76%, vol 16.54%, CAGR 17.18% ✓
- Peak detection: 2025-02-11 within 0.8% of 90d high ✓ · Panic: 2025-03-13 −8.8% pre-exit ✓
- BTC 90d momentum +32.3% (drives HYPE_CHASE evidence) ✓ · NIFTY −15% off high → dip window open ✓
