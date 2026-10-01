"""engine/market.py — data layer (Problem Step 2/4/5 backing).
Rule #5: REAL-DATA-OR-LABELLED — every frame carries .attrs["source"] = live|simulated."""
from __future__ import annotations

import time
import numpy as np
import pandas as pd
import yfinance as yf

RETRY = 3
TICKERS = {
    "us_etf": ["SPY", "QQQ"], "us_stock": ["AAPL", "NVDA"],
    "gold": ["GC=F", "GLD"], "crypto": ["BTC-USD", "ETH-USD"],
    "india": ["^NSEI", "RELIANCE.NS"], "safe": ["BIL"], "bond_yield": ["^TNX"],
}
PREFERRED = {"stocks": "SPY", "gold": "GC=F", "crypto": "BTC-USD", "india": "^NSEI", "safe": "BIL"}


def fetch(sym: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame | None:
    """Fetch history with retry/backoff. Returns None on failure (caller labels fallback)."""
    for attempt in range(RETRY):
        try:
            h = yf.Ticker(sym).history(period=period, interval=interval, auto_adjust=True)
            if h is not None and not h.empty:
                h.attrs["source"] = "live"
                return h
        except Exception:
            pass
        time.sleep(1.5 * (attempt + 1))
    return None


def simulated(sym: str, period: str = "2y") -> pd.DataFrame:
    """Deterministic fallback clearly labeled 'simulated' (RULES #5). Seeded by symbol."""
    n = {"1y": 252, "2y": 504, "5y": 1260}.get(period, 504)
    rng = np.random.default_rng(abs(hash(sym)) % (2**32))
    rets = rng.normal(0.0004, 0.011, n)
    close = 100 * np.cumprod(1 + rets)
    idx = pd.bdate_range(end=pd.Timestamp.today(), periods=n)
    h = pd.DataFrame({"Open": close, "High": close * 1.005, "Low": close * 0.995,
                      "Close": close, "Volume": (rng.integers(1e6, 5e6, n))}, index=idx)
    h.attrs["source"] = "simulated"
    return h


def get(sym: str, period: str = "2y") -> pd.DataFrame:
    h = fetch(sym, period)
    return h if h is not None else simulated(sym, period)


def last_price(sym: str) -> tuple[float, str]:
    h = get(sym, "3mo")
    return float(h["Close"].iloc[-1]), h.attrs.get("source", "live")


# ---------- signals used by loss analysis & recommender ----------
def drawdown_pct(h: pd.DataFrame) -> float:
    c = h["Close"]
    return float((c / c.cummax() - 1).min())


def annualized_vol(h: pd.DataFrame) -> float:
    return float(h["Close"].pct_change().std() * np.sqrt(252))


def cagr(h: pd.DataFrame) -> float:
    c = h["Close"]
    years = max((c.index[-1] - c.index[0]).days / 365.25, 1e-6)
    return float((c.iloc[-1] / c.iloc[0]) ** (1 / years) - 1)


def momentum(h: pd.DataFrame, days: int = 90) -> float:
    c = h["Close"]
    if len(c) <= days:
        return float(c.iloc[-1] / c.iloc[0] - 1)
    return float(c.iloc[-1] / c.iloc[-days] - 1)


def _match_tz(index: pd.DatetimeIndex, t) -> pd.Timestamp:
    """Align a user date with the index tz (yfinance indexes are tz-aware)."""
    ts = pd.Timestamp(t)
    if index.tz is not None:
        ts = ts.tz_localize(index.tz) if ts.tzinfo is None else ts.tz_convert(index.tz)
    elif ts.tzinfo is not None:
        ts = ts.tz_localize(None)
    return ts


def was_at_peak(h: pd.DataFrame, buy_ts, win: int = 90) -> tuple[bool, float]:
    """True if buy happened within 5% of the local max (bought-at-peak detection)."""
    c = h["Close"]
    pos = c.index.searchsorted(_match_tz(c.index, buy_ts))
    if pos <= 0:
        return False, 0.0
    window = c.iloc[max(0, pos - win):pos + 1]
    if window.empty:
        return False, 0.0
    buy_p, peak = float(c.iloc[pos - 1]), float(window.max())
    gap = (peak - buy_p) / peak if peak else 0.0
    return gap <= 0.05, gap


def panic_window(h: pd.DataFrame, sell_ts, win: int = 30) -> tuple[bool, float]:
    """True if sell followed a sharp drawdown within win days (panic-sell detection)."""
    c = h["Close"]
    pos = c.index.searchsorted(_match_tz(c.index, sell_ts))
    window = c.iloc[max(0, pos - win):max(pos, 1)]
    if window.empty or len(window) < 2:
        return False, 0.0
    dd = float(window.iloc[-1] / window.max() - 1)
    return dd <= -0.08, dd


def month_seasonality(h: pd.DataFrame) -> dict[str, float]:
    """Average return by calendar month → 'best time to invest' evidence."""
    r = h["Close"].pct_change().dropna()
    avg = r.groupby(r.index.month).mean()
    return {pd.Timestamp(2000, m, 1).strftime("%b"): float(v) for m, v in avg.items()}


def sip_projection(monthly: float, annual_rate: float, years: int) -> float:
    """FV of monthly SIP at end of each month, monthly compounding."""
    r = annual_rate / 12
    n = years * 12
    return float(monthly * (((1 + r) ** n - 1) / r) * (1 + r)) if r else monthly * n
