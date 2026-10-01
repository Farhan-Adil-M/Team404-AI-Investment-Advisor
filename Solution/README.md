# Team404 — AI-Powered Personal Investment Advisor

**Matrix Hackathon 2026 · DRKVSRIT × Data Science · Team404**
Members: **A.kruthika · Shaik Zeeshan · M. Farhan Adil · M. Noel**

## Problem statement
Most people want to invest but don't know where to start — the right decision depends on their
financial background, prior experience, and risk comfort, but no single tool considers all of it
together. Beginners get generic advice, and people who've faced past losses don't understand *why*
it happened or how to move forward.

## Solution overview
A single integrated, web-based AI advisor that walks a user through **five steps**, using **real
market data (yfinance)** at every stage:

1. **Profile input (rich intake)** — age, monthly income & expenses, dependents, emergency fund,
   employment stability, goal + time horizon, existing investments, risk willingness (1–5), plus
   the core fields: investment budget, experience (Beginner/Intermediate/Experienced),
   prior-asset background, and optional past-loss details. *(We ask what proper advice needs —
   age and income included — not just what the brief listed.)*
2. **AI background & loss analysis** — if a past loss is described, the engine matches the user's
   dates/asset against real price history and explains the *proven* reason ("you bought within
   0.8% of the 90-day high", "you exited 8.8% below the 30-day high") in beginner language,
   dialled to their experience level
3. **Risk assessment** — "Willing to take high risk for higher returns? Yes/No", combined with the
   1–5 willingness score using the **risk capacity vs willingness** rule (binding = min of the two;
   a Beginner saying Yes is moderated — *enthusiasm ≠ capacity*)
4. **Personalized recommendation — dual plan**
   - **Recommended for you:** profile-driven allocation (110−age equity glide path, goal buckets,
     emergency-fund gating, SIP capacity) with step-by-step reasoning, flags (insurance, emergency
     shortfall) and instrument suggestions
   - **Build your own:** custom sliders (equity/debt/gold/crypto/cash) with live expected-return,
     worst-case drawdown, trade-off line and guard-rail warnings
   - **High risk:** aggressive picks (real tickers, live momentum/volatility/drawdown) with
     per-pick reasoning · **Low risk:** SIP with 3/5/10-year scenarios, best-time-to-invest
     reminder and experience-matched hand-holding
5. **Ongoing optimizer** — monthly signals from live data: dip → top-up suggestion with amounts,
   allocation drift >5pp → rebalance, volatility spike → pause lumpsum

### Feature → problem-step fit map
| Problem step | Where it lives |
|---|---|
| Step 1 Profile | `app.py` wizard step 1 (rich intake → `engine/planner.py` rules) |
| Step 2 Loss analysis | `engine/loss_analyzer.py` (taxonomy: PEAK_BUY, PANIC_SELL, HYPE_CHASE, CONCENTRATION, HOLD_THROUGH_CRASH, MISMATCH_RISK) |
| Step 3 Risk question | `app.py` wizard step 3 + risk matrix in `engine/recommender.py` + capacity/willingness binding in `engine/planner.py` |
| Step 4 Recommendation | `engine/planner.py` (recommended + custom dual plan) · `engine/recommender.py` (high-risk) · `engine/sip.py` (low-risk SIP) |
| Step 5 Optimizer | `engine/optimizer.py` |
| Real market data | `engine/market.py` (yfinance with retry + clearly-labeled simulated fallback) |

## Tech stack
- **Python 3.14** · **Streamlit 1.64** (UI wizard) · **yfinance 1.7** (live + historical market data)
- **pandas / numpy** (signals: drawdown, volatility, CAGR, seasonality) · **Plotly 7** (charts)
- **python-pptx** (presentation deck generation)
- Runtime "AI" = deterministic rule engine over real market data (offline-safe; no API key required,
  so the demo **cannot** crash on a network/LLM outage)

## Setup & run instructions
```bash
# 1. clone / unzip, then:
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. run the app
streamlit run app.py               # opens http://localhost:8501
```
Python ≥ 3.10 required. Internet needed for live yfinance data; if a fetch fails the UI shows a
clearly labeled *simulated* fallback instead of crashing.

## Verify it works (smoke test)
```bash
python -c "import yfinance as yf; print(yf.Ticker('SPY').history(period='5d').tail(1))"
```
You should see a live SPY closing price row.

## Honest-data policy
Every number shown comes from live yfinance fetches (labeled 🟢). Fallback data, if ever used, is
labeled 🟡 *simulated* in the UI. Projections are illustrations at assumed constant rates —
not promises, not investment advice.

## Docs
- `RULES.md` — hackathon rules → agent-workflow rules
- `DESIGN.md` — architecture & problem-fit traceability
- `RESEARCH.md` — researcher-agent findings (yfinance, finance logic, model selection)
- `SUBMISSION_CHECKLIST.md` — ZIP completeness tracker
