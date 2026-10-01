"""Team404 — AI-Powered Personal Investment Advisor (Matrix Hackathon 2026) — v2 UI.
Deep-Navy × Emerald fintech design. 5-step journey:
Profile (rich intake) → AI loss analysis → Risk choice → The Plan (dual-plan) → Ongoing optimizer.
Run: .venv/bin/streamlit run app.py
Engine modules (market, loss_analyzer, recommender, sip, optimizer, planner) are the ONLY
source of numbers — every chart/data point comes from them (honest-data rule)."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine import market as mkt
from engine import loss_analyzer as la
from engine import recommender as rec
from engine import sip as sipmod
from engine import optimizer as opt
from engine import planner as P

st.set_page_config(page_title="Team404 · AI Investment Advisor", page_icon="📈", layout="wide")

# ============================== design tokens ==============================
BG, SURFACE, TEXT, MUTED = "#0B1D32", "#162D4A", "#F4F6F8", "#A0AEC0"
ACCENT, DANGER, GOLD, STEEL, CORAL = "#00C853", "#D13438", "#E8B84B", "#3E5C8A", "#E85D4A"
SLICE_COLORS = {"equity": ACCENT, "debt": STEEL, "gold": GOLD, "crypto": CORAL, "cash": MUTED}
PICK_COLORS = [ACCENT, STEEL, GOLD, CORAL, "#4E8FCB", MUTED]
SCENARIO_COLORS = [STEEL, ACCENT, GOLD]

DISCLAIMER = ("Educational tool — data-driven illustrations, not investment advice. "
              "Markets carry risk; past performance doesn't predict future returns.")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@600;700&display=swap');

html, body, .stApp { font-family: 'Inter', system-ui, sans-serif; background: #0B1D32; color: #F4F6F8; }
h1, h2, h3, h4, .t4-sora { font-family: 'Sora', 'Inter', sans-serif; letter-spacing: -0.01em; }
.stApp, [data-testid="stAppViewContainer"] { background:
  radial-gradient(1200px 500px at 85% -10%, rgba(0,200,83,0.10), transparent 60%),
  radial-gradient(900px 420px at -10% 20%, rgba(62,92,138,0.22), transparent 55%), #0B1D32; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }

/* sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0E2440 0%, #0B1D32 100%); border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebar"] * { color: #F4F6F8; }

/* headings inside the app */
[data-testid="stHeading"] { color: #F4F6F8; }
h1, h2, h3 { color: #F4F6F8 !important; }
p, label, span { color: inherit; }
[data-testid="stCaptionContainer"], .t4-muted { color: #A0AEC0; }

/* entrance animation */
@keyframes t4fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.main .block-container { animation: t4fadeUp .55s ease both; padding-top: 1.6rem; }
.t4-fade { animation: t4fadeUp .6s ease both; }

/* hero */
.t4-hero { position: relative; overflow: hidden; border-radius: 22px; padding: 40px 40px 34px 40px; margin: 4px 0 20px 0;
  border: 1px solid rgba(255,255,255,0.08);
  background: linear-gradient(120deg, #0B1D32 0%, #162D4A 35%, #123A5E 65%, #0B1D32 100%);
  background-size: 300% 300%; animation: t4heroShift 14s ease infinite;
  box-shadow: 0 22px 60px rgba(4,12,24,0.55); }
@keyframes t4heroShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
.t4-hero::after { content: ""; position: absolute; right: -120px; top: -120px; width: 380px; height: 380px; border-radius: 50%;
  background: radial-gradient(circle, rgba(0,200,83,0.22), transparent 70%); }
.t4-kicker { color: #00C853; font-size: .74rem; font-weight: 700; letter-spacing: .18em; margin-bottom: 12px; }
.t4-hero h1 { font-size: 2.75rem; line-height: 1.08; margin: 0 0 12px 0; }
.t4-hero .t4-sub { color: #C7D2DF; font-size: 1.06rem; max-width: 720px; line-height: 1.65; margin: 0 0 18px 0; }
.t4-chips { display: flex; flex-wrap: wrap; gap: 10px; }
.t4-chip { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.10); color: #E7EDF4;
  border-radius: 999px; padding: 7px 15px; font-size: .82rem; font-weight: 500; }

/* progress rail */
.t4-rail { display: flex; align-items: center; gap: 6px; margin: 6px 0 26px 0; padding: 16px 20px; border-radius: 18px;
  background: rgba(22,45,74,0.55); border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(10px); overflow-x: auto; }
.t4-rail-step { display: flex; flex-direction: column; align-items: center; gap: 7px; min-width: 92px; }
.t4-rail-dot { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: .82rem; font-weight: 700; border: 1.5px solid rgba(255,255,255,0.16); color: #A0AEC0; background: rgba(255,255,255,0.04); }
.t4-rail-step.active .t4-rail-dot { background: #00C853; color: #04220F; border-color: #00C853; box-shadow: 0 0 0 5px rgba(0,200,83,0.18); }
.t4-rail-step.done .t4-rail-dot { background: rgba(0,200,83,0.16); color: #00C853; border-color: rgba(0,200,83,0.5); }
.t4-rail-label { font-size: .74rem; color: #A0AEC0; white-space: nowrap; font-weight: 500; }
.t4-rail-step.active .t4-rail-label { color: #F4F6F8; font-weight: 700; }
.t4-rail-step.done .t4-rail-label { color: #7FDCA6; }
.t4-rail-line { flex: 1; height: 2px; min-width: 18px; background: rgba(255,255,255,0.12); border-radius: 2px; margin-bottom: 22px; }
.t4-rail-line.filled { background: linear-gradient(90deg, rgba(0,200,83,0.7), rgba(0,200,83,0.35)); }

/* section headers */
.t4-section { display: flex; align-items: baseline; gap: 12px; margin: 26px 0 6px 0; }
.t4-section .t4-eyebrow { color: #00C853; font-size: .72rem; font-weight: 700; letter-spacing: .16em; }
.t4-section h2 { margin: 2px 0 0 0; font-size: 1.55rem; }
.t4-lead { color: #A0AEC0; font-size: .98rem; line-height: 1.7; max-width: 860px; margin: 4px 0 10px 0; }

/* glass cards (markdown-drawn) */
.t4-card { background: rgba(22,45,74,0.55); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px;
  padding: 20px 22px; margin: 12px 0; backdrop-filter: blur(10px);
  transition: transform .25s ease, box-shadow .25s ease; }
.t4-card:hover { transform: translateY(-4px); box-shadow: 0 16px 40px rgba(4,12,24,0.45); }
.t4-card h3, .t4-card h4 { margin: 0 0 8px 0; }
.t4-card .t4-small { color: #A0AEC0; font-size: .85rem; line-height: 1.6; }

/* container cards (widgets live here) */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(22,45,74,0.55) !important; backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 18px !important;
  transition: transform .25s ease, box-shadow .25s ease; }
[data-testid="stVerticalBlockBorderWrapper"]:hover { transform: translateY(-3px); box-shadow: 0 16px 40px rgba(4,12,24,0.42); }

/* metric strip */
.t4-metrics { display: flex; flex-wrap: wrap; gap: 14px; margin: 14px 0; }
.t4-metric { flex: 1 1 190px; background: linear-gradient(160deg, rgba(22,45,74,0.85), rgba(18,38,64,0.65));
  border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 18px 20px;
  animation: t4fadeUp .6s ease both; transition: transform .25s ease, box-shadow .25s ease; }
.t4-metric:hover { transform: translateY(-4px); box-shadow: 0 16px 38px rgba(4,12,24,0.5); }
.t4-metric .t4-m-label { color: #A0AEC0; font-size: .76rem; font-weight: 600; letter-spacing: .07em; text-transform: uppercase; }
.t4-metric .t4-m-value { font-family: 'Sora', sans-serif; font-size: 1.85rem; font-weight: 700; color: #F4F6F8; margin: 6px 0 2px 0; }
.t4-metric .t4-m-value.t4-good { color: #00E676; }
.t4-metric .t4-m-value.t4-bad { color: #FF6B6B; }
.t4-metric .t4-m-sub { color: #A0AEC0; font-size: .8rem; line-height: 1.5; }

/* notes / insights */
.t4-note { border-radius: 14px; padding: 15px 18px; margin: 12px 0; font-size: .92rem; line-height: 1.65;
  border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.05); }
.t4-note.t4-ok { border-left: 4px solid #00C853; background: rgba(0,200,83,0.09); }
.t4-note.t4-warn { border-left: 4px solid #E8B84B; background: rgba(232,184,75,0.09); }
.t4-note.t4-bad { border-left: 4px solid #D13438; background: rgba(209,52,56,0.10); }
.t4-note.t4-info { border-left: 4px solid #4E8FCB; background: rgba(78,143,203,0.10); }
.t4-note.t4-why { border-left: 4px solid rgba(255,255,255,0.25); background: rgba(255,255,255,0.045); color: #C7D2DF; font-size: .88rem; }

/* choice cards (risk step) */
.t4-choice { border-radius: 20px; padding: 26px 26px 22px 26px; border: 1.5px solid rgba(255,255,255,0.10);
  background: rgba(22,45,74,0.55); min-height: 240px;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease; }
.t4-choice:hover { transform: translateY(-5px); box-shadow: 0 20px 48px rgba(4,12,24,0.5); }
.t4-choice.t4-yes:hover { border-color: rgba(0,200,83,0.55); }
.t4-choice.t4-no:hover { border-color: rgba(78,143,203,0.6); }
.t4-choice .t4-icon { font-size: 2.1rem; }
.t4-choice h3 { margin: 10px 0 8px 0; font-size: 1.28rem; }
.t4-choice p { color: #C7D2DF; line-height: 1.7; font-size: .93rem; margin: 0 0 10px 0; }
.t4-tag { display: inline-block; border-radius: 999px; padding: 5px 12px; font-size: .74rem; font-weight: 600;
  background: rgba(0,200,83,0.12); color: #7FDCA6; border: 1px solid rgba(0,200,83,0.28); margin: 3px 6px 0 0; }
.t4-tag.t4-tag-blue { background: rgba(78,143,203,0.12); color: #9CC4EE; border-color: rgba(78,143,203,0.3); }
.t4-tag.t4-tag-gold { background: rgba(232,184,75,0.12); color: #F2D48B; border-color: rgba(232,184,75,0.3); }

/* meters (capacity vs willingness) */
.t4-meter { margin: 12px 0; }
.t4-meter-top { display: flex; justify-content: space-between; font-size: .85rem; color: #C7D2DF; margin-bottom: 6px; }
.t4-meter-val { font-weight: 700; color: #F4F6F8; }
.t4-meter-track { height: 10px; border-radius: 6px; background: rgba(255,255,255,0.08); overflow: hidden; }
.t4-meter-fill { height: 100%; border-radius: 6px; animation: t4grow 1s ease both; }
@keyframes t4grow { from { width: 0 !important; } }
.t4-meter-note { color: #A0AEC0; font-size: .78rem; margin-top: 5px; }

/* numbered reasoning steps */
.t4-step { display: flex; gap: 14px; align-items: flex-start; margin: 10px 0; }
.t4-step-num { flex: 0 0 30px; height: 30px; border-radius: 9px; background: rgba(0,200,83,0.14); color: #7FDCA6;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .85rem;
  border: 1px solid rgba(0,200,83,0.3); }
.t4-step-body { color: #DCE5EE; font-size: .93rem; line-height: 1.65; padding-top: 3px; }

/* list rows */
.t4-row { display: flex; gap: 12px; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
.t4-row:last-child { border-bottom: none; }
.t4-row-icon { font-size: 1.05rem; line-height: 1.5; }

/* badges */
.t4-badge { display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 4px 12px;
  font-size: .74rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.06); color: #DCE5EE; }
.t4-badge.t4-live { background: rgba(0,200,83,0.12); color: #7FDCA6; border-color: rgba(0,200,83,0.3); }
.t4-badge.t4-sim { background: rgba(232,184,75,0.12); color: #F2D48B; border-color: rgba(232,184,75,0.3); }

/* table */
.t4-table { width: 100%; border-collapse: collapse; font-size: .88rem; }
.t4-table th { text-align: left; color: #A0AEC0; font-weight: 600; padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.10);
  font-size: .76rem; letter-spacing: .06em; text-transform: uppercase; }
.t4-table td { padding: 11px 12px; border-bottom: 1px solid rgba(255,255,255,0.06); color: #E7EDF4; }
.t4-table tr:hover td { background: rgba(255,255,255,0.03); }

/* streamlit widget polish */
div.stButton > button { border-radius: 12px; font-weight: 600; letter-spacing: .01em; transition: all .22s ease; }
div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 26px rgba(4,12,24,0.45); }
button[data-testid="stBaseButton-primary"] { background: linear-gradient(135deg, #00C853, #00A844) !important; color: #04220F !important; border: none !important; }
button[data-testid="stBaseButton-secondary"] { background: rgba(255,255,255,0.06) !important; color: #F4F6F8 !important; border: 1px solid rgba(255,255,255,0.14) !important; }
div.stButton > button[kind="secondary"] { background: rgba(255,255,255,0.06); color: #F4F6F8; border: 1px solid rgba(255,255,255,0.14); }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px; padding: 10px 18px; color: #C7D2DF; font-weight: 600; }
.stTabs [aria-selected="true"] { background: rgba(0,200,83,0.16) !important; color: #F4F6F8 !important; border-color: rgba(0,200,83,0.45) !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none; }
div[data-testid="stExpander"] { background: rgba(22,45,74,0.45); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; }
[data-testid="stExpander"] summary:hover { color: #00E676; }
div[data-testid="stSlider"] [role="slider"] { background: #00C853; }
div[data-testid="stSlider"] div[data-testid="stThumbValue"] { color: #F4F6F8; }
section[data-testid="stSidebar"] div.stButton > button { width: 100%; }
[data-testid="stMetricValue"] { color: #F4F6F8; }
footer { visibility: hidden; }

/* dataframes blend into the theme */
[data-testid="stDataFrame"] { border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; overflow: hidden; }
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ============================== helpers ==============================


def inr(x, decimals: int = 1) -> str:
    """₹ in Indian lakhs/crores notation: ₹12.5L, ₹1.2Cr, ₹45,000."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return "—"
    sign = "−" if v < 0 else ""
    v = abs(v)
    if v >= 1e7:
        return f"{sign}₹{v / 1e7:.{decimals}f}Cr"
    if v >= 1e5:
        return f"{sign}₹{v / 1e5:.{decimals}f}L"
    return f"{sign}₹{v:,.0f}"


def pct(x, decimals: int = 1) -> str:
    return f"{float(x) * 100:.{decimals}f}%"


def src_badge(src: str) -> str:
    cls, txt = ("t4-live", "● live market data") if src == "live" else ("t4-sim", "● simulated fallback")
    return f'<span class="t4-badge {cls}">{txt}</span>'


def why(text: str):
    st.markdown(f'<div class="t4-note t4-why">💡 <b>Why we ask:</b> {text}</div>', unsafe_allow_html=True)


def note(kind: str, html: str):
    icons = {"t4-ok": "✅", "t4-warn": "⚠️", "t4-bad": "🛑", "t4-info": "ℹ️"}
    st.markdown(f'<div class="t4-note {kind}">{icons.get(kind, "•")} {html}</div>', unsafe_allow_html=True)


def section(eyebrow: str, title: str, lead: str = ""):
    st.markdown(f'<div class="t4-section"><div><div class="t4-eyebrow">{eyebrow}</div>'
                f'<h2>{title}</h2></div></div>', unsafe_allow_html=True)
    if lead:
        st.markdown(f'<div class="t4-lead">{lead}</div>', unsafe_allow_html=True)


def metrics(cards):
    """cards: list of (label, value_html, sub_html, tone) — tone in {'', 't4-good', 't4-bad'}."""
    parts = []
    for label, value, sub, tone in cards:
        parts.append(f'<div class="t4-metric"><div class="t4-m-label">{label}</div>'
                     f'<div class="t4-m-value {tone}">{value}</div>'
                     f'<div class="t4-m-sub">{sub}</div></div>')
    st.markdown('<div class="t4-metrics">' + "".join(parts) + "</div>", unsafe_allow_html=True)


def meter_bar(label: str, value, color: str, note_text: str = "") -> str:
    v = max(0, min(5, float(value)))
    return (f'<div class="t4-meter"><div class="t4-meter-top"><span>{label}</span>'
            f'<span class="t4-meter-val">{v:.0f}/5</span></div>'
            f'<div class="t4-meter-track"><div class="t4-meter-fill" style="width:{v / 5 * 100:.0f}%;background:{color}"></div></div>'
            + (f'<div class="t4-meter-note">{note_text}</div>' if note_text else "") + "</div>")


def risk_meters_html(rp: dict) -> str:
    gov = ("your <b>financial capacity</b> is the limiter — enthusiasm is capped by real-world constraints"
           if rp["governed_by"] == "capacity" else
           "your <b>stated willingness</b> is the limiter — your finances could handle more risk, but you don't want it")
    notes = " · ".join(rp["capacity_notes"]) if rp["capacity_notes"] else "stable income, no major constraints"
    return (meter_bar("Risk capacity (financial reality)", rp["capacity"], STEEL, notes)
            + meter_bar("Risk willingness (comfort with swings)", rp["willingness"], GOLD, "your 1–5 answer from Step 1")
            + meter_bar(f"Binding risk level = min(capacity, willingness) → <b>{rp['level']}</b>",
                        rp["binding"], ACCENT, f"Governed by {gov}."))


def rail(step: int):
    names = ["Profile", "Loss analysis", "Risk choice", "Your plan", "Optimizer"]
    parts = []
    for i, n in enumerate(names, 1):
        cls = "done" if step > i else ("active" if step == i else "todo")
        icon = "✓" if step > i else str(i)
        parts.append(f'<div class="t4-rail-step {cls}"><div class="t4-rail-dot">{icon}</div>'
                     f'<div class="t4-rail-label">{i} · {n}</div></div>')
        if i < 5:
            parts.append(f'<div class="t4-rail-line {"filled" if step > i else ""}"></div>')
    st.markdown('<div class="t4-rail">' + "".join(parts) + "</div>", unsafe_allow_html=True)


def hero():
    st.markdown(
        '<div class="t4-hero">'
        '<div class="t4-kicker">TEAM404 · AI INVESTMENT ADVISOR · MATRIX HACKATHON 2026</div>'
        '<h1>Your money,<br>with a plan.</h1>'
        '<p class="t4-sub">Five friendly steps — tell us about you, learn from past losses, choose your risk, '
        'get a <b>personalized dual plan</b>, and keep it healthy with monthly optimizer nudges. '
        'Every number is computed from real market data (clearly labelled when simulated).</p>'
        '<div class="t4-chips">'
        '<span class="t4-chip">📊 Live market data (yfinance)</span>'
        '<span class="t4-chip">🧠 Loss-pattern analysis</span>'
        '<span class="t4-chip">🎯 Recommended + Build-your-own plans</span>'
        '<span class="t4-chip">🛡️ Emergency-fund safety gate</span>'
        '</div></div>', unsafe_allow_html=True)


# ---------- plotly styling ----------
def style_fig(fig, height: int = 330):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=height,
        font=dict(family="Inter, sans-serif", color=TEXT, size=12),
        margin=dict(t=34, b=14, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11)),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor="rgba(255,255,255,0.15)", font=dict(color=TEXT)),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color=MUTED)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.07)", zeroline=False, color=MUTED)
    return fig


def donut(labels, values, colors, title: str, hole: float = 0.62, height: int = 330):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=hole, sort=False,
        marker=dict(colors=colors, line=dict(color=BG, width=2)),
        textinfo="label+percent", textfont=dict(size=11.5, color=TEXT),
        hovertemplate="%{label}<br><b>%{percent}</b><extra></extra>"))
    fig.update_layout(title=dict(text=title, font=dict(size=14, color=TEXT), x=0.02),
                      annotations=[dict(text="allocation", x=0.5, y=0.5, font=dict(size=12, color=MUTED), showarrow=False)])
    return style_fig(fig, height)


def chart(fig, key: str):
    st.plotly_chart(fig, width="stretch", key=key, config={"displayModeBar": False})


# ---------- cached engine wrappers (market fetches are slow ~10-20s) ----------
@st.cache_data(ttl=900, show_spinner=False)
def _mkt_hist(sym: str, period: str):
    return mkt.get(sym, period)


@st.cache_data(ttl=900, show_spinner=False)
def _last_price(sym: str):
    return mkt.last_price(sym)


@st.cache_data(ttl=900, show_spinner=False)
def _analyze(asset, amount, why_txt, buy, sell, experience, hist_json):
    return la.analyze(asset, amount, why_txt, buy, sell, experience, json.loads(hist_json))


@st.cache_data(ttl=900, show_spinner=False)
def _high_risk_plan(budget, experience):
    return rec.high_risk_plan(budget, experience)


@st.cache_data(ttl=900, show_spinner=False)
def _sip_plan(monthly, lumpsum, experience):
    return sipmod.build_plan(monthly, lumpsum, experience)


@st.cache_data(ttl=900, show_spinner=False)
def _monthly_check(experience, high_risk, budget):
    return opt.monthly_check(experience, high_risk, budget)


# ============================== session state ==============================
DEFAULTS = {
    "in_age": 28, "in_income": 60000, "in_expenses": 32000, "in_dependents": "0",
    "in_emergency": 100000, "in_employment": "Salaried", "in_goal": "Long-term wealth building",
    "in_horizon": 12, "in_existing": 50000, "in_willingness": 3,
    "in_budget": 200000.0, "in_experience": "Beginner",
    "in_bg_assets": "", "in_bg_months": 0,
    "in_has_loss": False, "in_loss_asset": "", "in_loss_amount": 50000.0,
    "in_buy": "", "in_sell": "", "in_why": "",
    "c_eq": 60, "c_debt": 15, "c_gold": 10, "c_crypto": 5, "c_cash": 10,
    "c_monthly": 10000.0, "c_lumpsum": 200000.0,
}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)
st.session_state.setdefault("step", 1)
st.session_state.setdefault("profile", {})
st.session_state.setdefault("loss", {})
st.session_state.setdefault("analysis", None)
st.session_state.setdefault("risk", None)
st.session_state.setdefault("celebrated", False)

STEP = st.session_state["step"]

# ============================== sidebar ==============================
with st.sidebar:
    st.markdown('<div class="t4-kicker">TEAM404 · MATRIX HACKATHON 2026</div>', unsafe_allow_html=True)
    st.markdown("## 🧭 DataNexus Advisor")
    st.caption("DRKVSRIT × Data Science · an honest, data-driven investment companion.")
    st.markdown(f'<div class="t4-card"><div class="t4-small">Built on live market data via yfinance. '
                f'If a fetch fails, the fallback is <b>clearly labelled “simulated”</b> — we never '
                f'pass invented numbers off as real.</div></div>', unsafe_allow_html=True)
    try:
        _p, _src = _last_price("SPY")
        st.markdown(f'<div style="margin:10px 0">{src_badge(_src)} &nbsp; <b>SPY</b> ${_p:,.2f}</div>',
                    unsafe_allow_html=True)
    except Exception:
        st.caption("Market data: temporarily unavailable")
    st.divider()
    st.caption(DISCLAIMER)

# ============================== hero + rail ==============================
hero()
rail(STEP)

# ============================== STEP 1 · PROFILE ==============================
if STEP == 1:
    section("STEP 1 · YOUR PROFILE", "Tell us about you — this shapes everything.",
            "One decision per card, no jargon. Everything here feeds the recommendation engine — "
            "the more honest your answers, the more useful your plan.")

    with st.container(border=True):
        st.markdown("#### 🧍 About you")
        st.caption("The human context behind the numbers.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Age", min_value=18, max_value=99, step=1, key="in_age",
                            help="Age sets how much of your money can ride out market swings.")
        with c2:
            st.selectbox("Employment", ["Salaried", "Freelance", "Business"], key="in_employment",
                         help="Stable salary = higher risk capacity. Freelance/business income is lumpier.")
        with c3:
            st.selectbox("Dependents", ["0", "1", "2", "3+"], key="in_dependents",
                         help="People financially relying on you — affects your safety net size.")
        c4, c5 = st.columns(2)
        with c4:
            st.selectbox("Primary goal", [
                "Long-term wealth building", "Retirement", "Home purchase",
                "Child's education", "Financial independence", "Short-term safety"], key="in_goal")
        with c5:
            st.slider("Time horizon (years)", min_value=1, max_value=30, step=1, key="in_horizon",
                      format="%d yrs", help="How long until you need this money. Long horizon = more room for swings.")
    why("Age sets how much of your money can ride out swings (the classic <b>110 − age</b> equity anchor), "
        "and your horizon decides whether dips are a threat or a sale.")

    with st.container(border=True):
        st.markdown("#### 💰 Money in, money out")
        st.caption("Your financial engine — surplus and safety net.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Monthly income (₹)", min_value=0, step=5000, key="in_income")
        with c2:
            st.number_input("Monthly expenses (₹)", min_value=0, step=5000, key="in_expenses")
        with c3:
            st.number_input("Emergency fund saved (₹)", min_value=0, step=10000, key="in_emergency",
                            help="Cash you can access in a crisis — 3–6 months of expenses is the target.")
        st.number_input("Existing investments (₹)", min_value=0, step=10000, key="in_existing",
                        help="Stocks, mutual funds, gold, crypto… anything you already hold.")
    why("Income − expenses decides how much you can invest monthly, and your emergency fund decides "
        "<b>whether it's safe to invest at all yet</b> — we gate the plan on it.")

    with st.container(border=True):
        st.markdown("#### 🎯 Experience, budget & risk appetite")
        st.caption("This changes everything about your plan — take a breath and answer honestly.")
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Investment budget — lumpsum (₹)", min_value=1000.0, step=10000.0, key="in_budget",
                            help="The total amount you're ready to deploy now.")
        with c2:
            st.radio("Prior investing experience", ["Beginner", "Intermediate", "Experienced"],
                     horizontal=True, key="in_experience")
        st.text_input("What have you held before? (stocks / gold / crypto / mutual funds…)",
                      key="in_bg_assets", placeholder="e.g. stocks, gold, an SIP or two")
        st.number_input("For how long? (months)", min_value=0, max_value=600, step=1, key="in_bg_months")
        st.slider("Risk willingness — how do swings feel to you?", min_value=1, max_value=5, step=1,
                  key="in_willingness",
                  help="1 = Conservative (keep me calm) … 5 = Aggressive (I can stomach big drops for growth)")
        st.caption('<span class="t4-muted">1 · Conservative &nbsp;·&nbsp; 2 · Cautious &nbsp;·&nbsp; 3 · Balanced '
                   '&nbsp;·&nbsp; 4 · Growth &nbsp;·&nbsp; 5 · Aggressive</span>', unsafe_allow_html=True)
    why("Beginners get simpler, moderated plans (enthusiasm ≠ experience), and your 1–5 willingness "
        "combines with your <b>risk capacity</b> later — the lower one wins.")

    with st.container(border=True):
        st.markdown("#### 🔍 Past loss (optional)")
        st.caption("Losses are tuition — let's make yours teach you something.")
        st.checkbox("I've taken a loss before and want it analysed", key="in_has_loss")
        if st.session_state["in_has_loss"]:
            l1, l2 = st.columns(2)
            with l1:
                st.text_input("Asset you lost money on", key="in_loss_asset",
                              placeholder="e.g. crypto, stocks, gold, mutual funds")
                st.number_input("Amount lost (₹)", min_value=0.0, step=5000.0, key="in_loss_amount")
            with l2:
                st.text_input("Rough buy date", key="in_buy", placeholder="YYYY-MM-DD  (e.g. 2024-11-15)")
                st.text_input("Rough exit date", key="in_sell", placeholder="YYYY-MM-DD  (e.g. 2025-02-11)")
            st.text_area("Why do you think it happened?", key="in_why",
                         placeholder="e.g. bought after seeing hype on social media, then panic-sold when it fell")
            st.caption("🕰️ Even a rough date helps — we match your story against real market moves. "
                       "Leave dates blank if you don't remember.")
        else:
            st.caption("No loss to analyse? Great — you'll sail straight past Step 2.")

    # --- validation & navigation ---
    date_ok = True
    dpat = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for dk in ("in_buy", "in_sell"):
        val = st.session_state[dk].strip()
        if st.session_state["in_has_loss"] and val and not dpat.match(val):
            date_ok = False
    if st.session_state["in_has_loss"] and not date_ok:
        note("t4-warn", "Dates should look like <b>YYYY-MM-DD</b> (e.g. 2025-02-11). Fix them to continue.")

    nb1, nb2 = st.columns([4, 1])
    with nb2:
        go_profile = st.button("Continue →", type="primary", width="stretch", key="go_profile")
    if go_profile:
        if not date_ok:
            st.stop()
        dependents = {"0": 0, "1": 1, "2": 2, "3+": 3}[st.session_state["in_dependents"]]
        income, expenses = int(st.session_state["in_income"]), int(st.session_state["in_expenses"])
        if expenses > income:
            note("t4-warn", "Expenses exceed income — your plan will focus on building a surplus first.")
        st.session_state["profile"] = {
            "age": int(st.session_state["in_age"]),
            "monthly_income": income, "monthly_expenses": expenses,
            "dependents": dependents, "employment": st.session_state["in_employment"],
            "goal": st.session_state["in_goal"], "horizon_years": float(st.session_state["in_horizon"]),
            "existing_investments": float(st.session_state["in_existing"]),
            "emergency_fund": float(st.session_state["in_emergency"]),
            "risk_willingness": int(st.session_state["in_willingness"]),
            "budget": float(st.session_state["in_budget"]),
            "experience": st.session_state["in_experience"],
            "background": f"{st.session_state['in_bg_assets'] or 'no prior holdings'} · "
                          f"{int(st.session_state['in_bg_months'])} months",
        }
        has_loss = st.session_state["in_has_loss"] and st.session_state["in_loss_asset"].strip()
        st.session_state["loss"] = {
            "asset": st.session_state["in_loss_asset"], "amount": float(st.session_state["in_loss_amount"]),
            "buy": st.session_state["in_buy"].strip() or None, "sell": st.session_state["in_sell"].strip() or None,
            "why": st.session_state["in_why"],
        } if has_loss else {}
        if has_loss:
            with st.spinner("Reading market history around your dates…"):
                hist = [{"asset": st.session_state["in_loss_asset"]}]  # only real entries (no invented history)
                st.session_state["analysis"] = _analyze(
                    st.session_state["in_loss_asset"], float(st.session_state["in_loss_amount"]),
                    st.session_state["in_why"], st.session_state["loss"]["buy"], st.session_state["loss"]["sell"],
                    st.session_state["in_experience"], json.dumps(hist, sort_keys=True))
        else:
            st.session_state["analysis"] = None
        st.session_state["step"] = 2
        st.rerun()

# ============================== STEP 2 · LOSS ANALYSIS ==============================
elif STEP == 2:
    section("STEP 2 · AI LOSS ANALYSIS", "Let's learn what happened — without the blame.",
            "We match your story to real market data and surface the pattern behind the loss. "
            "This is the step that turns regret into a rule.")
    a = st.session_state.get("analysis")
    prof = st.session_state["profile"]

    if not a:
        note("t4-ok", "<b>Nothing to analyse — that's a good thing.</b> 🎉 No past loss on record means we skip "
                      "straight to building your plan. If you ever do take a loss, come back and let us look at it "
                      "honestly — it's the fastest free education there is.")
    else:
        st.markdown(f'<div class="t4-card t4-fade"><h3>{a["summary"]}</h3>'
                    f'<div class="t4-small">Evidence base: {src_badge(a["data_source"])} &nbsp; '
                    f'matched ticker <b>{a["ticker"]}</b> · analysis depth tuned for '
                    f'<b>{prof.get("experience", "Beginner")}</b>s</div></div>', unsafe_allow_html=True)

        conf_icon = {"high": "🔴", "medium": "🟡", "low": "⚪"}
        for f in a["findings"]:
            with st.expander(f"{conf_icon.get(f.confidence, '⚪')} {f.headline}   ·   confidence: {f.confidence}",
                             expanded=True):
                st.markdown("**What the data shows**")
                for e in f.evidence:
                    st.markdown(f"- 📌 {e}")
                st.markdown(f"\n{f.explanation}")
                note("t4-info", f"<b>Lesson for next time:</b> {f.lesson}")

        exp = prof.get("experience", "Beginner")
        gentle = {
            "Beginner": "Hey — this pattern trips up almost every beginner. You're already ahead by seeing it clearly. "
                        "We'll keep your plan simple and calm.",
            "Intermediate": "Good context to have. We'll fold these lessons into your allocation rules.",
            "Experienced": "Findings above are numbers-first. Use them as checklist items in your entry/exit rules.",
        }[exp]
        note("t4-ok", f"🧭 Guidance dial set to <b>{exp}</b> — {gentle}")

    b1, b2 = st.columns([1, 4])
    with b1:
        if st.button("← Back", width="stretch", key="back_2"):
            st.session_state["step"] = 1
            st.rerun()
    with b2:
        if st.button("Continue to risk choice →", type="primary", width="stretch", key="go_risk"):
            st.session_state["step"] = 3
            st.rerun()

# ============================== STEP 3 · RISK CHOICE ==============================
elif STEP == 3:
    prof = st.session_state["profile"]
    exp = prof.get("experience", "Beginner")
    stable = prof.get("employment", "Salaried") == "Salaried"
    rp = P.risk_profile(int(prof.get("risk_willingness", 3)), exp, int(prof.get("dependents", 0)),
                        stable, float(prof.get("horizon_years", 10)))

    section("STEP 3 · YOUR RISK CHOICE", "One question that steers the whole plan.",
            f"For a <b>{exp}</b> investor like you — are you willing to take <b>high risk for higher returns</b>? "
            "There's no wrong answer. This decides whether we show you the aggressive growth playbook or the calm SIP playbook.")

    y_arch = rec.archetype(exp, True)
    n_arch = rec.archetype(exp, False)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(
            f'<div class="t4-choice t4-yes t4-fade"><div class="t4-icon">💥</div>'
            f'<h3>YES — high risk, high returns</h3>'
            f'<p>I can watch my portfolio fall hard and not abandon the plan. I want growth engines — '
            f'tech, momentum, even a small crypto sleeve — sized carefully.</p>'
            f'<span class="t4-tag">→ “{y_arch}” playbook</span>'
            f'<span class="t4-tag t4-tag-gold">live-momentum picks</span>'
            f'<span class="t4-tag t4-tag-gold">bigger swings</span></div>', unsafe_allow_html=True)
        if st.button("💥 Yes — go aggressive", type="primary", width="stretch", key="risk_yes"):
            st.session_state["risk"] = True
            st.session_state["step"] = 4
            st.rerun()
    with c2:
        st.markdown(
            f'<div class="t4-choice t4-no t4-fade"><div class="t4-icon">🛡️</div>'
            f'<h3>NO — keep it safe</h3>'
            f"<p>I'd rather grow steadily than lose sleep. Show me the SIP playbook: diversified, "
            f"rules-based, and honest about what the market can and can't promise.</p>"
            f'<span class="t4-tag t4-tag-blue">→ “{n_arch}” playbook</span>'
            f'<span class="t4-tag t4-tag-blue">SIP + projections</span>'
            f'<span class="t4-tag t4-tag-blue">smoother ride</span></div>', unsafe_allow_html=True)
        if st.button("🛡️ No — keep it safe", width="stretch", key="risk_no"):
            st.session_state["risk"] = False
            st.session_state["step"] = 4
            st.rerun()

    with st.container(border=True):
        st.markdown("#### ⚖️ How this combines with your Step-1 answer")
        st.caption("You rated your risk willingness 1–5 earlier. We combine it with your financial "
                   "<b>risk capacity</b> (income stability, dependents, horizon) — and the <b>lower one binds</b>. "
                   "This protects you from your own optimism on a good day.")
        st.markdown(f'<div class="t4-card">{risk_meters_html(rp)}</div>', unsafe_allow_html=True)
        note("t4-info", f"Whatever you pick above, your recommended mix stays <b>{rp['level']}</b> — "
                        f"the choice shapes the <i>playbook</i> (aggressive picks vs SIP), while the binding rule "
                        f"keeps the <i>allocation</i> grounded in reality. Beginners saying “yes” still get moderated "
                        f"(enthusiasm ≠ capacity).")

    b1, _ = st.columns([1, 4])
    with b1:
        if st.button("← Back", width="stretch", key="back_3"):
            st.session_state["step"] = 2 if st.session_state.get("analysis") else 1
            st.rerun()

# ============================== STEP 4 · THE PLAN ==============================
elif STEP == 4:
    prof, risk = st.session_state["profile"], st.session_state["risk"]
    exp = prof.get("experience", "Beginner")

    if not st.session_state["celebrated"]:
        st.balloons()
        st.session_state["celebrated"] = True

    plan = P.recommend(prof)  # pure math — instant & live

    section("STEP 4 · YOUR PLAN", "Here it is — your personalized investment plan 🎉",
            f"Built from your answers using researched rules (110−age glide, 50/30/20 capacity, emergency-fund gate). "
            f"Switch tabs to explore the recommendation, build your own, or see the "
            f"{'high-risk playbook' if risk else 'calm SIP playbook'} you asked for.")

    metrics([
        ("Your archetype", plan["archetype"], f"binding risk {plan['risk']['binding']}/5 · governed by {plan['risk']['governed_by']}", ""),
        ("Expected long-run rate", pct(plan["expected_rate"]), "weighted assumption across sleeves — not a promise", "t4-good"),
        ("Worst-case drawdown", pct(plan["worst_case_dd"]), "a bad-but-plausible year, so nothing surprises you", "t4-bad"),
        ("Monthly investing", inr(plan["monthly_invest"]) + "/mo", plan["sip"]["note"][:60] + ("…" if len(plan["sip"]["note"]) > 60 else ""), ""),
    ])

    tab_rec, tab_custom, tab_variant = st.tabs(
        ["⭐ Recommended for you", "🎛️ Build your own", "🚀 High-risk picks" if risk else "🛡️ Safe SIP plan"])

    # ---------- tab 1: recommended ----------
    with tab_rec:
        left, right = st.columns([1.1, 1])
        with left:
            st.markdown("#### 🧠 How we got here")
            for i, step_txt in enumerate(plan["reasoning"], 1):
                st.markdown(f'<div class="t4-step"><div class="t4-step-num">{i}</div>'
                            f'<div class="t4-step-body">{step_txt}</div></div>', unsafe_allow_html=True)
            if plan["flags"]:
                st.markdown("#### 🚩 Things we're watching for you")
                for fl in plan["flags"]:
                    kind = "t4-warn" if fl.startswith("⚠") else "t4-info"
                    note(kind, fl)
        with right:
            st.markdown("#### ⚖️ Capacity vs willingness")
            st.markdown(f'<div class="t4-card">{risk_meters_html(plan["risk"])}</div>', unsafe_allow_html=True)

        don = donut(
            [k.capitalize() for k, v in plan["allocation"].items() if v > 0],
            [v for v in plan["allocation"].values() if v > 0],
            [SLICE_COLORS[k] for k, v in plan["allocation"].items() if v > 0],
            f"Recommended allocation — {plan['archetype']}")
        chart(don, "rec_donut")

        years = max(3, int(prof.get("horizon_years", 10)))
        rows = P.project_total(plan["monthly_invest"], prof.get("budget", 0.0), plan["expected_rate"], years)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[r["year"] for r in rows], y=[r["invested"] for r in rows], name="You invest",
            stackgroup="one", line=dict(width=0.6, color=STEEL), fillcolor="rgba(62,92,138,0.55)",
            hovertemplate="Year %{x}: %{y:,.0f}<extra>You invest</extra>"))
        fig.add_trace(go.Scatter(
            x=[r["year"] for r in rows], y=[r["growth"] for r in rows], name="Growth (assumed)",
            stackgroup="one", line=dict(width=0.6, color=ACCENT), fillcolor="rgba(0,200,83,0.40)",
            hovertemplate="Year %{x}: %{y:,.0f}<extra>Growth</extra>"))
        fig.update_layout(title=dict(text=f"Your money over {years} years — contributions vs assumed growth "
                                          f"({pct(plan['expected_rate'])}/yr, illustration)",
                                     font=dict(size=13, color=TEXT), x=0.02),
                          xaxis_title="Years", yaxis_title="₹")
        chart(style_fig(fig, 330), "rec_projection")

        emg, sipd = plan["emergency"], plan["sip"]
        if sipd.get("gate_active"):
            note("t4-warn",
                 f"<b>🛡️ Safety gate is active:</b> your emergency fund is {inr(emg['shortfall'])} short of "
                 f"{emg['months']} months of expenses. Plan phase 1 — park {inr(sipd['phase2_amount'])}/mo into the "
                 f"emergency fund for ~{sipd['phase1_months']} months, then phase 2 starts investing automatically. "
                 f"<br><br>→ {sipd['note']}")
        else:
            note("t4-ok", f"<b>Emergency fund funded ✅</b> — {emg['months']} months of expenses covered "
                          f"({inr(emg['target'])} target). Your full {inr(plan['monthly_invest'])}/mo can go to work.")

        st.markdown("#### 🧰 What to actually buy")
        instr_cols = st.columns(min(3, max(1, len(plan["instruments"]))))
        for idx, (sleeve, items) in enumerate(plan["instruments"].items()):
            with instr_cols[idx % len(instr_cols)]:
                color = SLICE_COLORS.get(sleeve, MUTED)
                items_html = "".join(f'<div class="t4-row"><div class="t4-row-icon">›</div><div>{it}</div></div>' for it in items)
                st.markdown(f'<div class="t4-card"><h4 style="color:{color}">{sleeve.capitalize()} · '
                            f'{plan["allocation"].get(sleeve, 0)}%</h4>{items_html}</div>', unsafe_allow_html=True)
        note("t4-info", f"<b>Assumptions:</b> long-run rates equity 12% · debt 8% · gold 9% · crypto 15% · cash 6% "
                        f"(illustrative). Worst-case drawdowns per sleeve are blended into your figure above. "
                        f"{DISCLAIMER}")

    # ---------- tab 2: build your own ----------
    with tab_custom:
        st.markdown("#### 🎛️ Design your own mix — the numbers update live")
        st.caption("Sliders are relative weights (they don't need to add to 100 — we normalize). "
                   "Compare your design against the recommendation and pick what you can stick with.")
        s1, s2, s3, s4, s5 = st.columns(5)
        with s1:
            st.slider("Equity %", 0, 100, key="c_eq")
        with s2:
            st.slider("Debt %", 0, 100, key="c_debt")
        with s3:
            st.slider("Gold %", 0, 100, key="c_gold")
        with s4:
            st.slider("Crypto %", 0, 100, key="c_crypto")
        with s5:
            st.slider("Cash %", 0, 100, key="c_cash")
        m1, m2 = st.columns(2)
        with m1:
            st.number_input("Monthly investment (₹)", min_value=0.0, step=2500.0, key="c_monthly")
        with m2:
            st.number_input("Lumpsum (₹)", min_value=0.0, step=10000.0, key="c_lumpsum")

        custom = P.custom_plan(st.session_state["c_eq"], st.session_state["c_debt"], st.session_state["c_gold"],
                               st.session_state["c_crypto"], st.session_state["c_cash"],
                               st.session_state["c_monthly"], st.session_state["c_lumpsum"],
                               float(prof.get("horizon_years", 10)))
        metrics([
            ("Expected long-run rate", pct(custom["expected_rate"]), "your mix, weighted by sleeve assumptions", "t4-good"),
            ("Worst-case drawdown", pct(custom["worst_case_dd"]), "how deep a bad stretch could go", "t4-bad"),
            ("Monthly / lumpsum", f"{inr(st.session_state['c_monthly'])} + {inr(st.session_state['c_lumpsum'])}",
             "your deployment", ""),
        ])
        note("t4-info", f"⚖️ <b>Trade-off:</b> {custom['tradeoff']}")
        for w in custom["warnings"]:
            kind = "t4-ok" if w.endswith("✅") else "t4-warn"
            note(kind, w)

        cdon = donut([k.capitalize() for k, v in custom["allocation"].items() if v > 0],
                     [v for v in custom["allocation"].values() if v > 0],
                     [SLICE_COLORS[k] for k, v in custom["allocation"].items() if v > 0],
                     "Your custom allocation")
        chart(cdon, "custom_donut")

        st.markdown("#### 🧰 Instruments for your mix")
        for sleeve, items in custom["instruments"].items():
            st.markdown(f'<div class="t4-row"><div class="t4-row-icon">🔹</div>'
                        f'<div><b>{sleeve.capitalize()}</b> — {", ".join(items)}</div></div>', unsafe_allow_html=True)

    # ---------- tab 3: problem-required variant ----------
    with tab_variant:
        if risk:
            st.markdown("#### 🚀 High-risk growth playbook")
            st.caption("Every pick is backed by live momentum / volatility / drawdown stats — sized to your budget, "
                       "tuned to your experience. Prices shown are from the data source labelled.")
            with st.spinner("Pulling live pick stats…"):
                hp = _high_risk_plan(float(prof.get("budget", 0)), exp)
            rows = [{"Pick": f"{x['name']}", "Ticker": x["ticker"],
                     "Price": f"{x['price']:,.2f}", "90d momentum": f"{x['momentum_90d']:+.1%}",
                     "Volatility": f"{x['volatility']:.0%}", "Max drawdown": f"{x['max_drawdown']:.0%}",
                     "Your amount": inr(x["amount"]), "Units": f"{x['units']:,.4f}", "Data": x["source"]}
                    for x in hp["picks"]]
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            chart(donut([x["ticker"] for x in hp["picks"]], [x["amount"] for x in hp["picks"]],
                        PICK_COLORS[:len(hp["picks"])], "Where your budget goes"),
                  "picks_donut")

            st.markdown("#### 🤔 Why each pick")
            for x in hp["picks"]:
                with st.expander(f"{x['name']} ({x['ticker']}) — {inr(x['amount'])} · {x['flavor']}"):
                    st.markdown(x["reason"])
                    st.markdown(f"- 90d momentum: **{x['momentum_90d']:+.1%}**")
                    st.markdown(f"- Annualized volatility: **{x['volatility']:.0%}**")
                    st.markdown(f"- Max drawdown in window: **{x['max_drawdown']:.0%}**")
                    st.markdown(f"- Price: **{x['price']:,.2f}** · data {src_badge(x['source'])}", unsafe_allow_html=True)

            top = hp["picks"][0]
            with st.spinner(f"Loading {top['ticker']} price history…"):
                h = _mkt_hist(top["ticker"], "1y")
            fig = go.Figure(go.Scatter(x=h.index, y=h["Close"], name=top["ticker"],
                                       line=dict(color=ACCENT, width=2), fillcolor="rgba(0,200,83,0.12)",
                                       fill="tozeroy", hovertemplate="%{x|%b %d, %Y}<br>%{y:,.2f}<extra></extra>"))
            fig.update_layout(title=dict(text=f"{top['name']} — 1y price ({h.attrs.get('source', 'live')} data)",
                                         font=dict(size=13, color=TEXT), x=0.02))
            chart(style_fig(fig, 330), "top_pick_chart")

            note("t4-warn", f"Cash buffer held back: <b>{inr(hp['cash_buffer'])}</b> — dry powder for dips. "
                            f"Style: {hp['style']}.<br><br>{hp['disclaimer']}")
        else:
            st.markdown("#### 🛡️ Safe SIP playbook")
            st.caption("Steady, rules-based investing with honest projections — three scenarios, no promises.")
            monthly = max(float(prof.get("budget", 0)) * 0.10, 1000)
            lump = float(prof.get("budget", 0)) * 0.2
            with st.spinner("Pulling seasonality from the SIP backbone…"):
                sp = _sip_plan(monthly, lump, exp)
            metrics([
                ("Monthly SIP", inr(sp["monthly"]), "auto-debit on payday — consistency beats timing", ""),
                ("Instant lumpsum", inr(sp["lumpsum"]), "deployed at once (or in 2–3 tranches)", ""),
                ("10y invested", inr(sp["scenarios"]["Moderate"]["invested"]), "your contributions alone", ""),
            ])
            srows = [{"Scenario": k, "Assumed return": f"{v['rate']:.0%}",
                      "3y": inr(v["3y"]), "5y": inr(v["5y"]), "10y": inr(v["10y"]),
                      "Invested (10y)": inr(v["invested"])} for k, v in sp["scenarios"].items()]
            st.dataframe(pd.DataFrame(srows), width="stretch", hide_index=True)

            months = list(sp["seasonality"].keys())
            vals = [v * 100 for v in sp["seasonality"].values()]
            colors = [ACCENT if v >= 0 else DANGER for v in vals]
            fig = go.Figure(go.Bar(x=months, y=vals, marker_color=colors,
                                   hovertemplate="%{x}: %{y:.2f}%<extra>avg monthly return</extra>"))
            fig.add_hline(y=0, line_width=1, line_color="rgba(255,255,255,0.25)")
            fig.update_layout(title=dict(text=f"Average monthly return by month — {sp['backbone']}",
                                         font=dict(size=13, color=TEXT), x=0.02),
                              xaxis_title="Month", yaxis_title="Avg return %")
            chart(style_fig(fig, 330), "seasonality_chart")

            dip_txt = (f"<b>🟢 Dip window open right now:</b> the index is {abs(sp['drawdown_vs_high']):.1%} off its high — "
                       f"historically a better-than-average time to deploy lumpsum (in tranches)."
                       if sp["dip_now"] else
                       f"<b>Index near highs</b> ({sp['drawdown_vs_high']:+.1%} vs high) — SIP continues as normal, "
                       f"no rush to deploy the lumpsum.")
            note("t4-ok" if sp["dip_now"] else "t4-info", dip_txt)
            note("t4-info", f"⏰ <b>{sp['reminder']}</b>")
            note("t4-ok", f"🧭 <b>Hand-holding for you:</b> {sp['hand_holding']}")
            st.caption(f"Backbone: {sp['backbone']} · data {sp['data_source']}")
            note("t4-warn", sp["disclaimer"])

    b1, b2 = st.columns([1, 4])
    with b1:
        if st.button("← Back", width="stretch", key="back_4"):
            st.session_state["step"] = 3
            st.rerun()
    with b2:
        if st.button("Continue to ongoing optimizer →", type="primary", width="stretch", key="go_step5"):
            st.session_state["step"] = 5
            st.rerun()

# ============================== STEP 5 · OPTIMIZER ==============================
else:
    prof, risk = st.session_state["profile"], st.session_state["risk"]
    section("STEP 5 · ONGOING OPTIMIZER", "Your plan, kept healthy — month after month 📡",
            "A plan without maintenance drifts. Every month we re-check the market against your plan and tell you, "
            "in plain English, if anything needs doing. Usually: nothing. Sometimes: a real opportunity.")

    with st.spinner("Running this month's market check…"):
        r = _monthly_check(prof.get("experience", "Beginner"), bool(risk), float(prof.get("budget", 0)))
    metrics([
        ("Market (SPY)", f"{r['market_price']:,.0f}", f"checked {r['checked_at']} · {r['market_source']} data", ""),
        ("Annualized volatility", pct(r["volatility"], 0), "22% is our 'elevated' threshold", ""),
        ("Signals this month", str(len(r["signals"])), "only what needs your attention", ""),
    ])

    level_style = {"act": ("t4-ok", "▶"), "warn": ("t4-warn", "⚠"), "info": ("t4-info", "ℹ")}
    for s in r["signals"]:
        kind, icon = level_style.get(s["level"], ("t4-info", "ℹ"))
        st.markdown(f'<div class="t4-card t4-fade"><h3>{icon} {s["title"]}</h3>'
                    f'<div class="t4-small" style="font-size:.92rem;color:#DCE5EE">{s["evidence"]}</div>'
                    f'<div style="margin-top:8px"><b>→ Action:</b> {s["action"]}</div>'
                    f'<div class="t4-small" style="margin-top:6px">💡 {s.get("why", "")}</div></div>',
                    unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### 📅 Your monthly cadence")
        st.markdown(f'<div class="t4-row"><div class="t4-row-icon">🔔</div><div>{r["nudge"]}</div></div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="t4-row"><div class="t4-row-icon">🗓️</div><div><b>Next check-up:</b> first week of '
                    'next month — revisit here and we\'ll re-run the signals against fresh data.</div></div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="t4-row"><div class="t4-row-icon">🧘</div><div><b>Golden rule:</b> the plan works '
                    'because it\'s boring. Automate the SIP, then mostly leave it alone.</div></div>',
                    unsafe_allow_html=True)

    st.markdown("#### 📋 Your plan at a glance")
    rows = [
        ("🎯 Goal", f"{prof.get('goal', '—')} · {prof.get('horizon_years', 0):g}-year horizon"),
        ("💼 Budget", f"{inr(prof.get('budget', 0))} lumpsum · {inr(prof.get('monthly_income', 0))}/mo income"),
        ("📚 Experience", f"{prof.get('experience', '—')} · background: {prof.get('background', '—')}"),
        ("⚖️ Risk", f"{'High risk 💥' if risk else 'Safe 🛡️'} · willingness {prof.get('risk_willingness', 0)}/5"),
        ("🧩 Plan type", "Recommended + high-risk picks" if risk else "Recommended + safe SIP"),
        ("🔍 Loss analysed", "Yes — findings in Step 2 ✅" if st.session_state.get("analysis") else "None (skipped)"),
    ]
    rows_html = "".join(f'<tr><td style="width:220px;color:#A0AEC0">{k}</td><td>{v}</td></tr>' for k, v in rows)
    st.markdown(f'<div class="t4-card"><table class="t4-table">{rows_html}</table></div>', unsafe_allow_html=True)

    note("t4-info", f"📎 {DISCLAIMER}")

    b1, b2, b3 = st.columns([1, 1, 3])
    with b1:
        if st.button("← Back to plan", width="stretch", key="back_5"):
            st.session_state["step"] = 4
            st.rerun()
    with b2:
        def _restart():
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["step"] = 1
        st.button("🔄 Start over", width="stretch", key="restart", on_click=_restart)
