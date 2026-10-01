"""engine/sip.py — Problem Step 4 (low-risk path): SIP plan, projections, best-time-to-invest.
Honest math per R3 research: illustrations, never promises (no 'guaranteed' language)."""
from __future__ import annotations

from engine import market as mkt

SCENARIOS = {"Conservative": 0.09, "Moderate": 12 * 0.01, "Optimistic": 0.13}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def build_plan(monthly: float, lumpsum: float, experience: str) -> dict:
    """Low-risk SIP plan: projections at 3/5/10y across three honest scenarios."""
    projections = {}
    for label, rate in SCENARIOS.items():
        projections[label] = {
            "rate": rate,
            "3y": round(mkt.sip_projection(monthly, rate, 3) + lumpsum * (1 + rate) ** 3, 0),
            "5y": round(mkt.sip_projection(monthly, rate, 5) + lumpsum * (1 + rate) ** 5, 0),
            "10y": round(mkt.sip_projection(monthly, rate, 10) + lumpsum * (1 + rate) ** 10, 0),
            "invested": round(monthly * 12 * 10 + lumpsum, 0),
        }

    # best time to invest: month-seasonality from the SIP backbone (^NSEI, real data)
    h = mkt.get("^NSEI", "5y")
    season = mkt.month_seasonality(h)
    best_month = max(season, key=season.get)
    worst_month = min(season, key=season.get)
    source = h.attrs.get("source", "live")

    # dip signal: is the index in a dip right now? (>5% off 52w high → good lumpsum window)
    c = h["Close"]
    dd_now = float(c.iloc[-1] / c.max() - 1)
    dip = dd_now <= -0.05

    hand_hold = {
        "Beginner": "Set an auto-debit on payday so investing happens without willpower. "
                    "Start with the Conservative scenario — treat the others as what-ifs.",
        "Intermediate": "Review quarterly, not monthly — extra tinkering usually costs returns. "
                        "Step up the SIP by ~10% with every raise.",
        "Experienced": "Consider a 10-20% step-up when the dip trigger fires; keep the "
                       "core autopilot and only tactically overlay.",
    }[experience]

    return {
        "monthly": monthly, "lumpsum": lumpsum,
        "scenarios": projections,
        "backbone": "^NSEI (NIFTY 50 index — SIP stand-in; yfinance has no MF NAV feed)",
        "seasonality": season, "best_month": best_month, "worst_month": worst_month,
        "dip_now": dip, "drawdown_vs_high": dd_now, "data_source": source,
        "reminder": f"Monthly reminder: invest at the start of the month "
                    f"(historically strongest window in this dataset: {best_month}); "
                    f"avoid {worst_month} if you have a choice.",
        "hand_holding": hand_hold,
        "disclaimer": "Projections are illustrations at assumed constant rates — markets don't "
                      "grow smoothly and some years will be negative. Not investment advice.",
    }
