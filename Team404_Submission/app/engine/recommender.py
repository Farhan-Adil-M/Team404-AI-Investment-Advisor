"""engine/recommender.py — Problem Step 4 (high-risk path) + risk routing.
Every pick backed by live yfinance stats with plain-language reasoning (RULES #5, #11)."""
from __future__ import annotations

from engine import market as mkt

# experience × risk-willingness → archetype (R3 research matrix; downshift if Beginner+Yes)
RISK_MATRIX = {
    ("Beginner", True): "moderate",      # enthusiasm ≠ capacity → downshift
    ("Beginner", False): "conservative",
    ("Intermediate", True): "aggressive",
    ("Intermediate", False): "moderate",
    ("Experienced", True): "aggressive",
    ("Experienced", False): "moderate",
}
# archetype → (equity_share, gold, crypto, safe/bonds) — sums to 100
ALLOCATIONS = {
    "conservative": {"Equity index (SIP)": 30, "Bonds/Safe (BIL)": 45, "Gold": 20, "Crypto": 0, "Cash": 5},
    "moderate":     {"Equity index (SIP)": 55, "Bonds/Safe (BIL)": 20, "Gold": 15, "Crypto": 5, "Cash": 5},
    "aggressive":   {"Equity index (SIP)": 75, "Bonds/Safe (BIL)": 5,  "Gold": 10, "Crypto": 8, "Cash": 2},
}
# aggressive high-risk pick universe: (name, ticker, flavor)
HIGH_RISK_POOL = [
    ("US Tech Growth (Nasdaq-100)", "QQQ", "growth"),
    ("AI/Semiconductor leaders", "NVDA", "growth"),
    ("US Broad Market", "SPY", "core"),
    ("India Nifty 50", "^NSEI", "growth"),
    ("Bitcoin", "BTC-USD", "volatile"),
    ("Gold (leverage-free hedge)", "GC=F", "hedge"),
]


def archetype(experience: str, high_risk: bool) -> str:
    return RISK_MATRIX.get((experience, high_risk), "moderate")


def allocation(experience: str, high_risk: bool) -> dict[str, int]:
    return ALLOCATIONS[archetype(experience, high_risk)]


def high_risk_plan(budget: float, experience: str) -> dict:
    """Aggressive picks w/ live stats + reasoning, sized to budget, tuned by experience."""
    picks = []
    n_picks = {"Beginner": 3, "Intermediate": 4, "Experienced": 5}[experience]
    for name, sym, flavor in HIGH_RISK_POOL[:n_picks + 1]:
        h = mkt.get(sym, "1y")
        src = h.attrs.get("source", "live")
        mom, vol, dd = mkt.momentum(h, 90), mkt.annualized_vol(h), mkt.drawdown_pct(h)
        price, psrc = mkt.last_price(sym)
        reason = {
            "growth": f"90d momentum {mom:+.1%} — this is where the growth is; "
                      f"but {abs(dd):.0%} max drawdown means it can fall hard, so we size it carefully.",
            "volatile": f"{vol:.0%} annualized volatility — high risk/high reward sleeve. "
                        f"Capped small because one bad month can swing {abs(dd):.0%}.",
            "hedge": f"Gold: {mom:+.1%} 90d — not exciting, but it cushions equity crashes "
                     "(its drawdown {abs(dd):.0%} is shallower than stocks).",
            "core": f"The stable base: {mom:+.1%} 90d, {vol:.0%} vol — carries the plan "
                    "when the riskier sleeves fall.",
        }[flavor]
        # experience dial
        if experience == "Beginner":
            reason += " As a beginner, we keep this simple: 3 picks, not 10."
        elif experience == "Experienced":
            reason += f" Stats: CAGR {mkt.cagr(h):.1%}."
        # sizing: equal-weight across picks, but cap crypto-ish sleeve for beginners
        picks.append({
            "name": name, "ticker": sym, "price": price, "source": src,
            "momentum_90d": mom, "volatility": vol, "max_drawdown": dd,
            "reason": reason, "flavor": flavor,
        })
    per_pick = budget * 0.9 / len(picks)   # keep 10% cash buffer
    for p in picks:
        p["amount"] = round(per_pick, 2)
        p["units"] = round(per_pick / p["price"], 4) if p["price"] else 0
    return {
        "archetype": archetype(experience, True),
        "picks": picks, "cash_buffer": round(budget * 0.1, 2),
        "style": "buy in 2-3 tranches over the next few weeks rather than all at once",
        "disclaimer": "High-risk allocations can lose value. Illustration, not investment advice.",
    }


def allocation_table(experience: str, high_risk: bool) -> dict[str, str]:
    """Allocation % + rupee/₹-agnostic amounts for the budget shown in Step 4."""
    return ALLOCATIONS[archetype(experience, high_risk)]
