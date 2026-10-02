"""Portfolios page — 5 preset portfolios backtested against REAL yfinance history.
Isolated from the wizard: app.py renders nothing but shared CSS on this route.
Accuracy = how close our assumed long-run rate was to the 3y realized weighted CAGR."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine import market as mkt
from engine import planner as P

# ---------------- self-contained dark theme ----------------
# Streamlit does not render the main script's <style> output on pages/ sub-routes,
# so this page carries its own compact dark styling (same tokens as the wizard).
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stTopbar"] {
  background: #0B1D32 !important; color: #F4F6F8;
}
body, .stApp, [data-testid="stAppViewContainer"] * { font-family: 'Inter', ui-sans-serif, system-ui, sans-serif; }
[data-testid="stSidebar"] { background: #0E2138 !important; border-right: 1px solid rgba(255,255,255,.07); }
[data-testid="stSidebar"] * { color: #F4F6F8; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stMainBlockContainer"] { max-width: 1180px; padding-top: 1.6rem; }
h1, h2, h3, h4 { color: #F4F6F8 !important; }
p, li, label, caption, [data-testid="stCaptionContainer"] { color: #A0AEC0 !important; }
.t4-kicker { color: #00C853; font-size: .72rem; letter-spacing: .18em; font-weight: 700; }
.t4-card { background: rgba(22,45,74,.62); border: 1px solid rgba(255,255,255,.08);
           border-radius: 16px; padding: 16px 18px; backdrop-filter: blur(10px); }
[data-testid="stExpander"] { background: #162D4A; border: 1px solid rgba(255,255,255,.08);
                             border-radius: 12px; }
[data-testid="stExpander"] summary { color: #F4F6F8 !important; }
[data-testid="stDataFrame"], [data-testid="stDataFrame"] * { color: #F4F6F8 !important; }
[data-testid="stDataFrame"] { border: 1px solid rgba(255,255,255,.08); border-radius: 14px; overflow: hidden; }
thead tr th { background: #162D4A !important; }
[data-testid="stMetricValue"] { color: #F4F6F8 !important; }
div[data-testid="stSlider"] [role="slider"] { background: #00C853; }
a, [data-testid="stMarkdownContainer"] a { color: #00E676 !important; }
[data-testid="stPlotlyChart"] { background: transparent; }
footer { visibility: hidden; }
</style>""", unsafe_allow_html=True)

# ---------------- portfolio presets (weights %) ----------------
PORTFOLIOS = [
    {"icon": "🐢", "name": "Conservative Guard", "alloc": {"equity": 30, "debt": 45, "gold": 20, "crypto": 0, "cash": 5},
     "desc": "Capital preservation first — for near-term goals and nervous investors."},
    {"icon": "⚖️", "name": "Balanced Core", "alloc": {"equity": 55, "debt": 20, "gold": 15, "crypto": 0, "cash": 5},
     "desc": "The middle path — growth with a shock absorber in every direction."},
    {"icon": "🚀", "name": "Aggressive Growth", "alloc": {"equity": 75, "debt": 5, "gold": 10, "crypto": 8, "cash": 2},
     "desc": "Long horizon, strong stomach — ride out big dips for bigger compounding."},
    {"icon": "🥇", "name": "Gold Shield", "alloc": {"equity": 20, "debt": 30, "gold": 40, "crypto": 0, "cash": 10},
     "desc": "Inflation-hedged defensively — gold-heavy with a small equity engine."},
    {"icon": "🌐", "name": "Index SIP Core", "alloc": {"equity": 70, "debt": 20, "gold": 10, "crypto": 0, "cash": 0},
     "desc": "Simple, cheap, broad — the classic 3-fund style core for monthly investing."},
]
TICKER = {"equity": "SPY", "debt": "BIL", "gold": "GC=F", "crypto": "BTC-USD", "cash": "BIL"}
SLICE_COLORS = {"equity": "#00C853", "debt": "#3E5C8A", "gold": "#E8B84B", "crypto": "#E85D4A", "cash": "#A0AEC0"}
TEXT, MUTED, ACCENT, GOLD, DANGER = "#F4F6F8", "#A0AEC0", "#00C853", "#E8B84B", "#D13438"
SRC_STATE = {"live": False}


@st.cache_data(ttl=900, show_spinner=False)
def sleeve_stats(sym: str):
    """3y CAGR + max drawdown + source for one sleeve ticker (live yfinance)."""
    h = mkt.get(sym, "3y")
    return mkt.cagr(h), mkt.drawdown_pct(h), h.attrs.get("source", "live")


def inr(v: float) -> str:
    a = abs(v)
    if a >= 1e7: return f"₹{v/1e7:,.2f}Cr"
    if a >= 1e5: return f"₹{v/1e5:,.2f}L"
    return f"₹{v:,.0f}"


def backtest(alloc_pct: dict) -> dict:
    """Weighted sleeve backtest on live 3y history. Assumptions from planner.RATES."""
    assumed, realized, worst, realized_dd = 0.0, 0.0, 0.0, 0.0
    sleeves = {}
    for sleeve, w in alloc_pct.items():
        if w <= 0:
            continue
        wt = w / 100
        assumed += wt * P.RATES[sleeve]
        worst += wt * P.MAXDD[sleeve]
        if sleeve == "cash":          # cash sleeve shares BIL with debt but keeps its own rate
            c, dd, src = sleeve_stats("BIL")
        else:
            c, dd, src = sleeve_stats(TICKER[sleeve])
        SRC_STATE["live"] = SRC_STATE["live"] or src == "live"
        realized += wt * c
        realized_dd += wt * dd
        sleeves[sleeve] = {"ticker": TICKER[sleeve], "w": w, "cagr": c, "dd": dd, "src": src}
    denom = max(abs(assumed), abs(realized), 0.01)
    accuracy = max(0.0, min(100.0, 100 * (1 - abs(assumed - realized) / denom)))
    return {"assumed": assumed, "realized": realized, "worst": worst,
            "realized_dd": realized_dd, "accuracy": accuracy, "sleeves": sleeves}


# ---------------- page ----------------
st.markdown('<div class="t4-kicker">REFERENCE · PORTFOLIO LAB</div>', unsafe_allow_html=True)
st.markdown("<h1 style='margin:4px 0 6px'>5 portfolios, scored against real history</h1>", unsafe_allow_html=True)
st.markdown(
    f'<p style="color:{MUTED};max-width:820px;line-height:1.6;margin-bottom:14px">'
    f'Every portfolio below is backtested on <b>3 years of live yfinance data</b> — we compare the '
    f'long-run rate each mix <i>assumes</i> (12% equity / 8% debt / 9% gold / 15% crypto / 6% cash) '
    f'against what its sleeves <i>actually returned</i>. <b>Accuracy</b> = 100 × (1 − |assumed − realized| ÷ '
    f'the larger of the two) — a honesty score for our own assumptions, not a prediction.</p>',
    unsafe_allow_html=True)

with st.spinner("Backtesting sleeves against live history (3y)…"):
    results = [(p, backtest(p["alloc"])) for p in PORTFOLIOS]

badge = '🟢 live market data' if SRC_STATE["live"] else '🟡 simulated fallback'
st.markdown(f'<span style="color:{ACCENT};font-size:.78rem;letter-spacing:.08em">● {badge}</span>',
            unsafe_allow_html=True)

# ---- score cards ----
cols = st.columns(len(results))
for col, (p, r) in zip(cols, results):
    acc = r["accuracy"]
    acc_color = ACCENT if acc >= 70 else GOLD if acc >= 45 else DANGER
    with col:
        bars = "".join(
            f'<div style="display:flex;align-items:center;gap:6px;margin:3px 0">'
            f'<span style="width:56px;color:{MUTED};font-size:.68rem">{s.capitalize()}</span>'
            f'<div style="flex:1;background:rgba(255,255,255,.07);border-radius:4px;height:7px">'
            f'<div style="width:{w}%;background:{SLICE_COLORS[s]};height:100%;border-radius:4px"></div></div>'
            f'<span style="font-size:.68rem;color:{TEXT}">{w}%</span></div>'
            for s, w in p["alloc"].items() if w > 0)
        st.markdown(
            f'<div class="t4-card" style="height:100%">'
            f'<div style="font-size:1.4rem">{p["icon"]}</div>'
            f'<div style="font-weight:700;color:{TEXT};margin:2px 0 8px">{p["name"]}</div>'
            f'{bars}'
            f'<div style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08)">'
            f'<div style="color:{MUTED};font-size:.68rem;letter-spacing:.1em">ASSUMPTION ACCURACY</div>'
            f'<div style="font-size:1.9rem;font-weight:800;color:{acc_color}">{acc:.0f}%</div>'
            f'<div style="color:{MUTED};font-size:.7rem;margin-top:6px">'
            f'assumed <b style="color:{TEXT}">{r["assumed"]:.1%}</b> · realized 3y '
            f'<b style="color:{TEXT}">{r["realized"]:.1%}</b></div>'
            f'<div style="color:{MUTED};font-size:.7rem">'
            f'worst-case {r["worst"]:.0%} vs realized {r["realized_dd"]:.0%}</div>'
            f'</div></div>', unsafe_allow_html=True)

# ---- assumed vs realized chart ----
fig = go.Figure()
names = [f'{p["icon"]} {p["name"]}' for p, _ in results]
fig.add_trace(go.Bar(name="Assumed (our long-run rate)", x=names,
                     y=[r["assumed"] * 100 for _, r in results],
                     marker_color="#3E5C8A", hovertemplate="%{x}: %{y:.1f}%<extra>assumed</extra>"))
fig.add_trace(go.Bar(name="Realized (3y live data)", x=names,
                     y=[r["realized"] * 100 for _, r in results],
                     marker_color="#00C853", hovertemplate="%{x}: %{y:.1f}%<extra>realized</extra>"))
fig.update_layout(barmode="group", height=360,
                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                  font=dict(family="Inter, sans-serif", color=TEXT, size=12),
                  margin=dict(t=44, b=64, l=10, r=10),
                  legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0),
                  title=dict(text="Assumed vs realized annual return — which of our assumptions held up?",
                             font=dict(size=13, color=TEXT), x=0.02),
                  yaxis_title="Annual return %",
                  xaxis=dict(tickfont=dict(size=11)),
                  yaxis=dict(gridcolor="rgba(255,255,255,0.07)"))
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

# ---- methodology & per-sleeve detail ----
with st.expander("📐 Methodology & per-sleeve detail"):
    st.markdown(
        f"- **Sleeve proxies:** equity→SPY · debt→BIL (1-3m T-Bill ETF) · gold→GC=F · crypto→BTC-USD · "
        f"cash→BIL. **Period:** 3 years of daily history via yfinance.\n"
        f"- **Weighted realized return** = Σ (weight × sleeve CAGR). **Weighted drawdown** = Σ "
        f"(weight × sleeve max drawdown) — a conservative approximation (real diversified drawdowns "
        f"are usually shallower).\n"
        f"- **Accuracy** scores our assumption against realized history — it does NOT forecast the future.")
    rows = []
    for p, r in results:
        for s, d in r["sleeves"].items():
            rows.append({"Portfolio": p["name"], "Sleeve": s.capitalize(), "Ticker": d["ticker"],
                         "Weight": f'{d["w"]}%', "3y CAGR": f'{d["cagr"]:.1%}',
                         "Max DD": f'{d["dd"]:.1%}', "Data": d["src"]})
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

st.markdown(
    f'<div class="t4-card" style="margin-top:8px"><span style="color:{MUTED};font-size:.8rem">'
    f'⚠ Past performance ≠ future returns. These are educational backtests on live data, not '
    f'investment advice — allocations here are presets, your personal plan lives in the '
    f'<a href="/" style="color:{ACCENT}">main advisor</a>.</span></div>', unsafe_allow_html=True)
st.markdown('[← Back to the advisor](/)', unsafe_allow_html=True)
