"""Team404 — AI-Powered Personal Investment Advisor (Matrix Hackathon 2026).
Streamlit wizard: Profile → Loss Analysis → Risk → Plan → Ongoing Optimizer.
Run: .venv/bin/streamlit run app.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from engine import market as mkt
from engine import loss_analyzer as la
from engine import recommender as rec
from engine import sip
from engine import optimizer as opt

st.set_page_config(page_title="Team404 · AI Investment Advisor", page_icon="📈", layout="wide")

DISCLAIMER = ("**Disclaimer:** Educational tool. Data-driven illustrations, not investment advice. "
              "Markets carry risk; past performance doesn't predict future returns.")
SOURCE_LINE = ("All figures from **live yfinance data** fetched at app start. "
               "If a fetch fails, the fallback is clearly labeled *simulated*.")

# ---------- session state ----------
for k, v in {"step": 1, "profile": {}, "loss": {}, "analysis": None,
             "risk": None, "plan": None, "sip": None}.items():
    st.session_state.setdefault(k, v)

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("## 🧭 Team404 Advisor")
    st.caption("Matrix Hackathon 2026 · DRKVSRIT × Data Science")
    step_names = ["1 · Profile", "2 · Loss analysis", "3 · Risk choice", "4 · Your plan", "5 · Optimizer"]
    st.markdown("**Your journey**")
    for i, n in enumerate(step_names, 1):
        done = st.session_state["step"] > i
        st.markdown(f"{'✅' if done else '🔵' if st.session_state['step'] == i else '⚪'} {n}")
    st.divider()
    try:
        p, src = mkt.last_price("SPY")
        st.caption(f"Data: {'🟢 live' if src == 'live' else '🟡 simulated'} · SPY ${p:,.2f}")
    except Exception:
        st.caption("Data: unavailable")
    st.caption(DISCLAIMER)

st.title("📈 AI-Powered Personal Investment Advisor")
st.caption(SOURCE_LINE)

# ================= STEP 1: PROFILE =================
if st.session_state["step"] == 1:
    st.header("Step 1 · Your profile")
    c1, c2 = st.columns(2)
    with c1:
        budget = st.number_input("Investment budget (₹ / total now)", min_value=1000.0,
                                 value=200000.0, step=10000.0)
        experience = st.radio("Prior investing experience",
                              ["Beginner", "Intermediate", "Experienced"], horizontal=True)
    with c2:
        st.text_input("Stocks / Gold / Crypto / Mutual funds — what you held before",
                      key="bg_assets", placeholder="e.g. stocks, gold")
        st.number_input("For how long (months)", min_value=0, value=0, key="bg_months")

    st.markdown("### Past loss (optional)")
    has_loss = st.checkbox("I have taken a loss before and want it analysed")
    loss = {}
    if has_loss:
        l1, l2 = st.columns(2)
        with l1:
            loss["asset"] = st.text_input("Asset lost in", placeholder="e.g. crypto, stocks, gold")
            loss["amount"] = st.number_input("Amount lost", min_value=0.0, value=50000.0, step=1000.0)
        with l2:
            loss["buy_date"] = st.date_input("Rough buy date", value=None)
            loss["sell_date"] = st.date_input("Rough exit date", value=None)
        loss["why"] = st.text_area("Why do you think it happened?",
                                   placeholder="e.g. bought after seeing hype, panic sold when it fell")
        st.caption("Tip: even a rough guess helps the AI match your loss to real market moves.")

    if st.button("Continue →", type="primary", use_container_width=True):
        st.session_state["profile"] = {
            "budget": budget, "experience": experience,
            "background": f"{st.session_state.get('bg_assets','') or 'no prior holdings'}"
                          f" · {st.session_state.get('bg_months',0)} months",
        }
        st.session_state["loss"] = loss if has_loss else {}
        # run Step-2 analysis immediately (may be empty)
        if has_loss and loss.get("asset"):
            buy = str(loss["buy_date"]) if loss.get("buy_date") else None
            sell = str(loss["sell_date"]) if loss.get("sell_date") else None
            # only real entries count as concentration evidence (RULES #5 — no fabricated history)
            hist = [{"asset": loss.get("asset", "")}]
            st.session_state["analysis"] = la.analyze(
                loss["asset"], loss.get("amount", 0), loss.get("why", ""),
                buy, sell, experience, hist)
        else:
            st.session_state["analysis"] = None
        st.session_state["step"] = 2 if has_loss else 3
        st.rerun()

# ================= STEP 2: LOSS ANALYSIS =================
elif st.session_state["step"] == 2:
    st.header("Step 2 · AI background & loss analysis")
    a = st.session_state.get("analysis")
    if not a:
        st.info("No loss details provided — continuing.")
        if st.button("Continue →", type="primary"):
            st.session_state["step"] = 3; st.rerun()
    else:
        st.subheader(a["summary"])
        badge = {"live": "🟢 live market data", "simulated": "🟡 simulated fallback"}[a["data_source"]]
        st.caption(f"Evidence base: {badge} · ticker {a['ticker']}")
        for f in a["findings"]:
            icon = {"high": "🔴", "medium": "🟡", "low": "⚪"}[f.confidence]
            with st.expander(f"{icon} {f.headline}  ·  confidence: {f.confidence}", expanded=True):
                st.markdown("**What the data shows**")
                for e in f.evidence:
                    st.markdown(f"- {e}")
                st.markdown(f"\n{f.explanation}")
                st.markdown(f"**💡 Lesson:** {f.lesson}")
        st.info(f"🧭 Guidance dial set to **{st.session_state['profile']['experience']}** — "
                "explanation depth adjusts to your experience.")
        if st.button("Continue → Risk choice →", type="primary", use_container_width=True):
            st.session_state["step"] = 3; st.rerun()

# ================= STEP 3: RISK =================
elif st.session_state["step"] == 3:
    st.header("Step 3 · How much risk are you willing to take?")
    exp = st.session_state["profile"]["experience"]
    st.markdown(f"**For a {exp} investor** — willing to take **high risk for higher returns**?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💥 YES — high risk, high returns", type="primary", use_container_width=True):
            st.session_state["risk"] = True; st.session_state["step"] = 4; st.rerun()
    with c2:
        if st.button("🛡️ NO — keep it safe", use_container_width=True):
            st.session_state["risk"] = False; st.session_state["step"] = 4; st.rerun()
    arch = rec.archetype(exp, True)
    st.caption(f"We'll tune the plan to a “{arch}” profile for your experience — "
               "beginners saying 'yes' still get a moderated mix (enthusiasm ≠ capacity).")

# ================= STEP 4: PLAN =================
elif st.session_state["step"] == 4:
    prof, risk = st.session_state["profile"], st.session_state["risk"]
    budget, exp = prof["budget"], prof["experience"]
    st.header("Step 4 · Your personalized plan" + (" 💥 High-risk" if risk else " 🛡️ Safe SIP"))

    if risk:
        if st.session_state.get("plan") is None:
            st.session_state["plan"] = rec.high_risk_plan(budget, exp)
        p = st.session_state["plan"]
        st.subheader(f"Aggressive growth plan · archetype: **{p['archetype']}**")
        rows = []
        for x in p["picks"]:
            rows.append({"Pick": f"{x['name']} ({x['ticker']})", "Price": round(x['price'], 2),
                         "90d momentum": f"{x['momentum_90d']:+.1%}",
                         "Volatility": f"{x['volatility']:.0%}",
                         "Max DD": f"{x['max_drawdown']:.0%}",
                         "Amount": x["amount"], "Units": x["units"], "Data": x["source"]})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        fig = px.pie(names=[x["ticker"] for x in p["picks"]],
                     values=[x["amount"] for x in p["picks"]],
                     title="Allocation of your budget")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Why each pick (reasoning)")
        for x in p["picks"]:
            st.markdown(f"- **{x['name']}** — {x['reason']}")
        st.caption(f"Cash buffer held back: {p['cash_buffer']:,.0f} · {p['style']}")

        # live price chart of top pick
        top = p["picks"][0]
        h = mkt.get(top["ticker"], "1y")
        fig2 = go.Figure(go.Scatter(x=h.index, y=h["Close"], name=top["ticker"]))
        fig2.update_layout(height=300, margin=dict(t=30, b=10),
                           title=f"{top['ticker']} — 1y price ({h.attrs.get('source','live')})")
        st.plotly_chart(fig2, use_container_width=True)
        st.warning(p["disclaimer"])
    else:
        if st.session_state.get("sip") is None:
            monthly = max(budget * 0.10, 1000)
            st.session_state["sip"] = sip.build_plan(monthly, budget * 0.2, exp)
        s = st.session_state["sip"]
        st.subheader(f"Safe SIP plan · backbone: **{s['backbone']}**")
        st.metric("Monthly SIP", f"{s['monthly']:,.0f}")
        st.metric("Instant lumpsum deployment", f"{s['lumpsum']:,.0f}")

        rows = [{"Scenario": k, "Assumed return": f"{v['rate']:.0%}",
                 "3y": f"{v['3y']:,.0f}", "5y": f"{v['5y']:,.0f}",
                 "10y": f"{v['10y']:,.0f}", "Total invested (10y)": f"{v['invested']:,.0f}"}
                for k, v in s["scenarios"].items()]
        st.markdown("#### Expected value over time (illustration)")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        months = list(s["seasonality"].keys())
        vals = [round(v * 100, 2) for v in s["seasonality"].values()]
        fig = px.bar(x=months, y=vals, title=f"Average monthly return — {s['backbone']}",
                     labels={"x": "Month", "y": "Avg return %"})
        st.plotly_chart(fig, use_container_width=True)

        dip_txt = (f"🟢 **Dip window open right now:** index is {abs(s['drawdown_vs_high']):.1%} "
                   f"off its high — historically a better-than-average time for lumpsum.") if s["dip_now"] \
                  else f"Index near highs ({s['drawdown_vs_high']:+.1%} vs high) — SIP continues as normal."
        st.success(dip_txt)
        st.info(f"⏰ **{s['reminder']}**")
        st.markdown(f"**🧭 Hand-holding:** {s['hand_holding']}")
        st.caption(f"Data: {'🟢 ' + s['data_source']}")
        st.warning(s["disclaimer"])

    if st.button("Continue → Ongoing optimizer →", type="primary", use_container_width=True):
        st.session_state["step"] = 5; st.rerun()

# ================= STEP 5: OPTIMIZER =================
else:
    st.header("Step 5 · Ongoing optimizer")
    prof, risk = st.session_state["profile"], st.session_state["risk"]
    r = opt.monthly_check(prof["experience"], risk, prof["budget"])
    st.caption(f"Checked against market data as of **{r['checked_at']}** · "
               f"{'🟢 live' if r['market_source']=='live' else '🟡 simulated'}")

    for s in r["signals"]:
        if s["level"] == "act":
            st.success(f"**▶ {s['title']}**\n\n{s['evidence']}\n\n→ {s['action']}\n\n_{s['why']}_")
        elif s["level"] == "warn":
            st.warning(f"**⚠ {s['title']}**\n\n{s['evidence']}\n\n→ {s['action']}")
        else:
            st.info(f"**ℹ {s['title']}**\n\n{s['evidence']}\n\n→ {s['action']}")

    st.markdown("### Your monthly cadence")
    st.markdown(f"- {r['nudge']}")
    st.markdown(f"- Next check-up: first week of next month (auto via this app).")
    st.caption(r["disclaimer"])

    st.divider()
    st.markdown("### 📋 Plan summary")
    summary = pd.DataFrame([
        {"Field": "Budget", "Value": f"{prof['budget']:,.0f}"},
        {"Field": "Experience", "Value": prof["experience"]},
        {"Field": "Background", "Value": prof["background"]},
        {"Field": "Risk choice", "Value": "High risk 💥" if risk else "Safe 🛡️"},
        {"Field": "Plan type", "Value": "Aggressive picks" if risk else "SIP + projections"},
        {"Field": "Loss analysed", "Value": "Yes ✅" if st.session_state.get("analysis") else "None"},
    ])
    st.dataframe(summary, use_container_width=True, hide_index=True)

    if st.button("🔄 Start over", use_container_width=True):
        for k in ["step", "profile", "loss", "analysis", "risk", "plan", "sip"]:
            st.session_state.pop(k, None)
        st.rerun()
