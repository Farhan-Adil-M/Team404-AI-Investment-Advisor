"""engine/loss_analyzer.py — Problem Step 2: AI background & loss analysis.
Turns user loss history + real market data into a proven cause + beginner explanation.
Experience dial: how much hand-holding we give (Beginner=gentle, Experienced=numbers-first)."""
from __future__ import annotations

from dataclasses import dataclass, field
from engine import market as mkt

# asset keywords → yfinance ticker for loss-history analysis
ASSET_MAP = {
    "stock": "SPY", "stocks": "SPY", "equity": "SPY", "share": "SPY",
    "gold": "GC=F", "silver": "SI=F",
    "crypto": "BTC-USD", "bitcoin": "BTC-USD", "btc": "BTC-USD",
    "ethereum": "ETH-USD", "eth": "ETH-USD", "coin": "BTC-USD",
    "mutual fund": "^NSEI", "mutual funds": "^NSEI", "sip": "^NSEI", "nifty": "^NSEI",
    "index": "SPY", "etf": "SPY", "nifty50": "^NSEI",
}
EXPERIENCE_LEVELS = ("Beginner", "Intermediate", "Experienced")


@dataclass
class LossFinding:
    code: str            # PEAK_BUY | PANIC_SELL | CONCENTRATION | HYPE_CHASE | HOLD_THROUGH_CRASH | MISMATCH_RISK
    confidence: str      # high | medium | low
    headline: str        # one-line cause
    evidence: list[str] = field(default_factory=list)     # hard numbers from live data
    explanation: str = ""      # beginner-friendly paragraph
    lesson: str = ""           # what to do differently


def _tone(text: str, experience: str) -> str:
    """Experience dial (Step 2): Beginners get a gentler wrap-up, experts get the bottom line."""
    if experience == "Beginner":
        return text + "\n\n_Plain-English takeaway:_ the market, not you, caused most of this — "
    if experience == "Intermediate":
        return text
    return text  # Experienced: evidence already numbers-first below


def analyze(loss_asset: str, loss_amount: float, loss_why: str,
            buy_date: str | None, sell_date: str | None,
            experience: str, all_history: list[dict]) -> dict:
    """Return {'findings': [LossFinding], 'summary': str, 'data_source': 'live'|'mixed'|'simulated'}."""
    asset = (loss_asset or "").strip().lower()
    sym = next((v for k, v in ASSET_MAP.items() if k in asset), "SPY")
    h = mkt.get(sym, "2y")
    src = h.attrs.get("source", "live")
    findings: list[LossFinding] = []

    # 1) Bought at market peak?
    if buy_date:
        at_peak, gap = mkt.was_at_peak(h, buy_date)
        if at_peak and gap is not None:
            findings.append(LossFinding(
                code="PEAK_BUY", confidence="high",
                headline=f"You likely bought near the top of {sym}",
                evidence=[f"Your entry was within {gap:.1%} of the 90-day high (data: {sym})."],
                explanation=(f"You bought {loss_asset} very close to its recent peak price. "
                             "Buying after a big run-up means you paid 'peak enthusiasm' prices — "
                             "when the price later cooled off, that showed up as a loss on paper."),
                lesson="Split purchases over time (SIP/staggered entries) instead of one lump at once."))

    # 2) Panic-sold during a dip?
    if sell_date:
        panic, dd = mkt.panic_window(h, sell_date)
        if panic:
            findings.append(LossFinding(
                code="PANIC_SELL", confidence="high",
                headline="The exit looks like a dip-driven (panic) sell",
                evidence=[f"{sym} was {dd:.1%} below its 30-day high right before your exit."],
                explanation=("You sold while the price was in a sharp dip. Selling into a fall locks in "
                             "the loss — and historically most of the recovery happens right after "
                             "those scary drops."),
                lesson="Set rules before you buy (stop-loss / hold horizon) so fear doesn't decide the exit."))

    # 3) Concentration: many separate losses in one asset / one theme?
    if len(all_history) >= 3:
        same = sum(1 for x in all_history if (x.get("asset", "").lower() in asset)) or \
               sum(1 for x in all_history if asset and asset in x.get("asset", "").lower())
        if same >= 3:
            findings.append(LossFinding(
                code="CONCENTRATION", confidence="medium",
                headline="Repeated losses in the same asset = concentration risk",
                evidence=[f"{same} of your loss entries involve {loss_asset or 'the same asset'}."],
                explanation=("Putting too much money into one asset multiplies both ways: when that one "
                             "thing falls, your whole portfolio falls with it."),
                lesson="Cap any single asset at ~10-25% of the portfolio; diversify across classes."))

    # 4) Hype-chase: user said so, or loss occurred right after a >20% pump
    why = (loss_why or "").lower()
    hype_words = ("hype", "fomo", "tip", "twitter", "reels", "friend", "pump", "news", "popular", "大家都")
    if any(w in why for w in hype_words):
        r90 = mkt.momentum(h, 90)
        ev = f"{sym} had moved {r90:+.1%} over the prior 90 days." if r90 > 0.15 else \
             "You noted the buy was driven by hype/tips rather than research."
        findings.append(LossFinding(
            code="HYPE_CHASE", confidence="medium",
            headline="Looks like a hype/FOMO entry",
            evidence=[ev],
            explanation=("Buying what everyone is talking about usually means buying after the price "
                         "has already jumped — late buyers often absorb the dip that follows."),
            lesson="Ignore tip chains; require one line of your own research before buying."))

    # 5) Held through a crash (no stop-loss): big market drawdown during holding window
    dd = mkt.drawdown_pct(h)
    if buy_date and not findings and dd <= -0.15:
        findings.append(LossFinding(
            code="HOLD_THROUGH_CRASH", confidence="medium",
            headline=f"You held through a {abs(dd):.0%} market drawdown",
            evidence=[f"{sym} max drawdown over the window: {dd:.1%} (live data)."],
            explanation=("There was a broad market fall while you held. With no exit rule, the "
                         "drawdown kept growing until you sold."),
            lesson="Use a stop-loss or hedging (gold/bonds) to cap how far a position can fall."))

    # 6) Risk-profile mismatch: losing instrument doesn't match stated experience
    if not findings:
        risky = any(k in asset for k in ("crypto", "coin", "stock", "equity", "btc", "eth"))
        if risky and experience == "Beginner":
            findings.append(LossFinding(
                code="MISMATCH_RISK", confidence="low",
                headline="Instrument riskier than your experience level",
                evidence=[f"{loss_asset or 'This asset'} is high-volatility; experience: {experience}."],
                explanation=("The asset you picked swings much more than is typical for someone at "
                             "your experience level — bigger swings make it easy to exit at the worst moment."),
                lesson="Start with index/SIP exposure, add riskier assets only with rules and small sizes."))

    if not findings:
        findings.append(LossFinding(
            code="NO_CLEAR_CAUSE", confidence="low",
            headline="No single cause found in the market data",
            evidence=[f"Reviewed {sym} price history; no matching crash/pattern for your dates."],
            explanation=("Your dates don't line up with a clear market event, so the loss may have come "
                         "from position sizing or an individual asset's news rather than the broad market."),
            lesson="Record entry/exit reasons next time — that log is what makes losses teachable."))

    data_source = "simulated" if src == "simulated" else "live"
    summary = _summarize(findings, experience, loss_amount, loss_asset, sym, data_source)
    return {"findings": findings, "summary": summary, "data_source": data_source, "ticker": sym}


def _summarize(findings: list[LossFinding], experience: str, amount: float,
               asset: str, sym: str, src: str) -> str:
    top = findings[0]
    lead = {"high": "The data strongly suggests", "medium": "The data suggests",
            "low": "There's a possibility"}[top.confidence]
    base = (f"{lead} your loss came from: {top.headline}. "
            f"Key evidence: {top.evidence[0]}")
    if experience == "Beginner":
        base += " Don't worry — this is one of the most common beginner patterns, and it's fixable."
    elif experience == "Experienced":
        base += f" (Sym={sym}, source={src}.)"
    if amount and amount > 0:
        base += f" Estimated loss reviewed: {amount:,.0f}."
    return base
