# DEMO_SCRIPT.md — 3-minute live demo (Team404)

**Before judges arrive:** app running (`streamlit run app.py`), browser open on Step 1, hard-refresh
(Ctrl+Shift+R). Test URL health first: `curl localhost:8501/_stcore/health` → `ok`.

**0:00–0:20 — Hook (Problem)**
> "A beginner and an experienced investor get the same generic advice today. And if you've taken a
> loss, nobody tells you *why*. Our tool asks what real advisors ask — age, income, goals — and
> proves every word with live market data."

**0:20–1:20 — Live flow (Execution, 30 pts)**
1. **Step 1 (rich intake):** Age 28 · Salaried · 0 dependents · goal = long-term wealth ·
   horizon 12y · income ₹80,000 · expenses ₹45,000 · emergency ₹15,000 · budget ₹1L ·
   experience Beginner · willingness 4/5 · add loss: *"crypto, bought 2025-02-11, exit 2025-03-13,
   bought after hype, panic-sold"* → **Continue**
   - Point out the **"Why we ask"** microcopy under each card.
2. **Step 2 (wow moment):** "Entry near the 90-day high… exited **-8.8%** below the 30-day high"
   — 🟢 live badge, confidence levels, beginner-friendly lesson, experience dial.
3. **Step 3:** two big choice cards + **capacity vs willingness meters** (min rule) → click **Yes**.

**1:20–2:00 — The dual plan (Innovation, 25 pts)**
4. **Step 4 ⭐ Recommended:** reasoning steps (110−age glide, emergency-gate flag for the ₹1.2L
   shortfall!), allocation donut, contributed-vs-growth area chart, instrument cards.
   **🎛️ Build your own:** drag sliders → live expected return vs worst-case −dd + guard warnings
   ("money needed in 2 years shouldn't sit in 30%+ equity").
   **🚀 High-risk picks:** live QQQ/NVDA/SPY/NIFTY stats table + per-pick reasoning.
5. *If they'd said No:* **🛡️ Safe SIP** tab — 3/5/10y scenarios, seasonality bars, dip window.

**2:00–2:30 — Ongoing optimizer (Innovation)**
6. **Step 5:** live signal cards ("Crypto +32% → rebalance"), cadence, plan summary.
> "It keeps working after the plan is made — that's the part nobody does."

**2:30–3:00 — Trust + close (Impact 15 / Fit 10)**
- Every number traceable to a live yfinance fetch (badges); fallback labeled 🟡 simulated
- No API key → deterministic engine → **cannot crash mid-demo**
- Free, works on any laptop · README maps features → the 5 problem steps
> "Free, honest, and it turns your worst loss into your best lesson. Team404 — thank you."

**Likely judge questions**
- *Where's the AI?* → Deterministic rule-engine over real market data: it diagnoses losses with
  proven evidence and adapts depth to experience — deliberately offline-safe (a demo that can't
  crash beats one that calls an API).
- *Real data?* 🟢 badge = live; fallback explicitly labeled 🟡 simulated (honesty rule).
- *Why these rules?* → 110−age glide (target-date default), capacity-vs-willingness binding,
  emergency-fund gating — standard advisory practice, cited in `RESEARCH.md`.
- *Not advice?* → Disclaimers on every projection screen; trade-offs always shown.
- *Team?* → **Team404:** A.kruthika, Shaik Zeeshan, M. Farhan Adil, M. Noel.
