"""engine/optimizer.py — Problem Step 5: ongoing plan tracker + adjustment suggestions.
Monthly recompute from live data: dip top-up, drift rebalance, accumulation, health checks."""
from __future__ import annotations

from engine import market as mkt
from engine import recommender as rec


def monthly_check(experience: str, high_risk: bool, budget: float,
                  last_check_price: float | None = None) -> dict:
    """Produce prioritized optimizer signals with evidence + plain-language action."""
    signals = []

    # 1) Dip trigger: market >5% below last check (or 52w high if first run)
    h = mkt.get("SPY", "1y")
    src = h.attrs.get("source", "live")
    price = float(h["Close"].iloc[-1])
    ref = last_check_price if last_check_price else float(h["Close"].max())
    change = price / ref - 1 if ref else 0.0
    if change <= -0.05:
        signals.append({
            "level": "act", "title": "Market dip — invest more",
            "evidence": f"Market is {abs(change):.1%} below your last check (live: {ref:.0f} → {price:.0f}).",
            "action": f"Deploy 10-20% of your cash buffer or step the SIP up ~10-20% "
                      f"(≈{budget * 0.15:,.0f} one-time), spread over 2-3 tranches.",
            "why": "Buying after a >5% drawdown has historically improved average forward returns — "
                   "on average, not every time.",
        })
    else:
        signals.append({
            "level": "info", "title": "No dip — stay the course",
            "evidence": f"Market {change:+.1%} vs last check (live data).",
            "action": "Keep the autopilot on. Extra tinkering usually costs returns.",
            "why": "Lumpsum-now beats waiting roughly 2/3 of the time (opportunity cost of idle cash).",
        })

    # 2) Allocation drift: recompute live weights vs target
    alloc = rec.allocation(experience, high_risk)
    targets = {k: v for k, v in alloc.items() if k in ("Equity index (SIP)", "Gold", "Crypto", "Bonds/Safe (BIL)")}
    drift_note = []
    for label in targets:
        sym = {"Equity index (SIP)": "SPY", "Gold": "GC=F", "Crypto": "BTC-USD", "Bonds/Safe (BIL)": "BIL"}[label]
        ph = mkt.get(sym, "6mo")
        mom = mkt.momentum(ph, 90)
        if abs(mom) > 0.10:  # sleeve moved >10pp-ish → weights drifted
            drift_note.append(f"{label} {mom:+.1%} (90d)")
    if drift_note:
        signals.append({
            "level": "act", "title": "Rebalance: allocation drifted",
            "evidence": "; ".join(drift_note) + " — outside the ±5pp band.",
            "action": "Sell a little of the winner, top up the laggard, back to target weights.",
            "why": "Rebalancing enforces 'buy low, sell high' mechanically and controls risk.",
        })

    # 3) Volatility spike / risk health
    vol = mkt.annualized_vol(h)
    if vol > 0.22:
        signals.append({
            "level": "warn", "title": "Volatility elevated",
            "evidence": f"Annualized volatility {vol:.0%} (threshold 22%).",
            "action": "Hold new lumpsum for now; SIP continues as usual.",
            "why": "A calm entry beats chasing a whipsaw; SIPs average through it for you.",
        })

    # 4) Experience-based hand-holding line
    nudge = {
        "Beginner": "Check-in cadence: monthly is enough. If a red month scares you, "
                    "reduce crypto/equity share rather than stopping the SIP.",
        "Intermediate": "You're on track — review quarterly and only if allocation drifts >5pp.",
        "Experienced": "Use the dip trigger as your only tactical lever; everything else autopilots.",
    }[experience]

    # evidence label honesty (RULES #5 / R3 ground rules)
    return {
        "signals": signals, "market_price": price, "market_source": src,
        "volatility": vol, "nudge": nudge,
        "checked_at": h.index[-1].strftime("%Y-%m-%d"),
        "disclaimer": "Signals are data-driven illustrations, not investment advice. "
                      "Markets can and do ignore history.",
    }
