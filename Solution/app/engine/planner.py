"""engine/planner.py — R5-researched advisory rules: profile → recommended plan + custom plan.
Rules: 110-age equity glide · 50/30/20 SIP capacity · emergency-fund gating (3-6 mo) ·
goal buckets · risk capacity vs willingness (binding = min). Illustrative rates, not advice."""
from __future__ import annotations

# illustrative long-run rates & worst-case drawdowns per sleeve (labeled as assumptions in UI)
RATES = {"equity": 0.12, "debt": 0.08, "gold": 0.09, "crypto": 0.15, "cash": 0.06}
MAXDD = {"equity": -0.35, "debt": -0.05, "gold": -0.15, "crypto": -0.60, "cash": 0.0}
INSTRUMENTS = {
    "equity": ["Nifty 50 index fund", "ELSS (tax-saving, 80C)", "US: total-market index ETF"],
    "debt": ["PPF", "Short-duration debt fund", "FD / Treasuries"],
    "gold": ["Gold ETF / SGB"],
    "cash": ["Liquid fund / High-yield savings (emergency)"],
    "crypto": ["BTC/ETH (speculative, ≤5%)"],
}
GOAL_BUCKETS = [  # (min_years, max_years, equity, debt, gold, cash)
    (0, 3, 0.10, 0.70, 0.05, 0.15),
    (3, 7, 0.40, 0.45, 0.10, 0.05),
    (7, 15, 0.70, 0.20, 0.07, 0.03),
    (15, 120, 0.85, 0.08, 0.05, 0.02),
]


def _clamp(x, lo, hi): return max(lo, min(hi, x))


def risk_profile(willingness: int, experience: str, dependents: int,
                 stable: bool, horizon_years: float) -> dict:
    """Capacity (financial) vs willingness (emotional) → binding = min, per R5."""
    capacity = 5
    if not stable: capacity -= 1            # freelance/business volatility
    if dependents >= 2: capacity -= 1
    if horizon_years < 3: capacity -= 2
    elif horizon_years < 7: capacity -= 1
    capacity = _clamp(capacity, 1, 5)
    if experience == "Beginner":
        willingness = min(willingness, 3)   # enthusiasm ≠ capacity (R3 rule)
    binding = min(capacity, willingness)
    level = {1: "Conservative", 2: "Moderately Conservative", 3: "Balanced",
             4: "Growth", 5: "Aggressive"}[binding]
    return {"capacity": capacity, "willingness": willingness, "binding": binding,
            "level": level, "governed_by": "capacity" if capacity < willingness else "willingness",
            "capacity_notes": (["unstable income"] if not stable else []) +
                              ([f"{dependents} dependents"] if dependents >= 2 else []) +
                              (["short goal horizon"] if horizon_years < 7 else [])}


def emergency_status(monthly_expenses: int, dependents: int, current: int) -> dict:
    months_needed = 6 if dependents >= 1 else 3
    target = monthly_expenses * months_needed
    shortfall = max(0, target - current)
    return {"target": target, "current": current, "shortfall": shortfall,
            "months": months_needed, "funded": shortfall == 0,
            "gate_active": shortfall > 0}


def sip_capacity(monthly_income: int, monthly_expenses: int, emg: dict) -> dict:
    """20%-of-income rule, or income−expenses if larger; emergency gate applies first (R5)."""
    base = max(int(0.20 * monthly_income), monthly_income - monthly_expenses)
    capacity = int(_clamp(base, 0, 0.40 * monthly_income))
    if emg["gate_active"]:
        # phase 1: all spare cash to emergency fund until funded
        return {"phase1_months": max(1, round(emg["shortfall"] / max(capacity, 1))),
                "phase1_amount": capacity, "phase2_amount": capacity,
                "gate_active": True, "investable_now": 0,
                "note": f"Emergency fund short by ₹{emg['shortfall']:,} — fund it first "
                        f"(~{max(1, round(emg['shortfall'] / max(capacity,1)))} months), then start the SIP."}
    return {"phase1_months": 0, "phase1_amount": 0, "phase2_amount": capacity,
            "gate_active": False, "investable_now": capacity,
            "note": f"₹{capacity:,}/mo available to invest (20-30% of income rule)."}


def glide_path(age: int, stable: bool, dependents: int) -> dict:
    """110 − age equity anchor (modern target-date default), adjusted & clamped 30–90%."""
    eq = 110 - age
    if not stable: eq -= 5
    if dependents >= 2: eq -= 3
    eq = int(_clamp(eq, 30, 90))
    return {"age": age, "rule": "110 − age", "equity_pct": eq}


def _weighted(sleeves: dict[str, float]) -> tuple[float, float]:
    r = sum(p * RATES[k] for k, p in sleeves.items())
    dd = sum(p * MAXDD[k] for k, p in sleeves.items())
    return r, dd


def _normalize(raw: dict[str, float]) -> dict[str, float]:
    tot = sum(raw.values()) or 1.0
    return {k: round(v / tot, 3) for k, v in raw.items()}


def recommend(profile: dict) -> dict:
    """Full recommended plan from the rich intake profile (R5 dual-plan pattern)."""
    age = profile.get("age", 30)
    income = profile.get("monthly_income", 50000)
    expenses = profile.get("monthly_expenses", int(0.6 * income))
    dependents = profile.get("dependents", 0)
    stable = profile.get("employment", "Salaried") == "Salaried"
    horizon = profile.get("horizon_years", 10)
    experience = profile.get("experience", "Beginner")
    willingness = int(profile.get("risk_willingness", 3))

    emg = emergency_status(expenses, dependents, profile.get("emergency_fund", 0))
    sip = sip_capacity(income, expenses, emg)
    glide = glide_path(age, stable, dependents)
    risk = risk_profile(willingness, experience, dependents, stable, horizon)

    # goal-bucket base by horizon, blended with glide-path equity anchor
    lo = next((b for b in GOAL_BUCKETS if b[0] <= horizon <= b[1]), GOAL_BUCKETS[-1])
    eq_target = _clamp(int(0.5 * glide["equity_pct"] + 0.5 * 100 * lo[2]), 5, 90) / 100
    # risk level scales equity: binding 1→−15pp … 5→+10pp
    scale = {1: -0.15, 2: -0.08, 3: 0.0, 4: 0.05, 5: 0.10}[risk["binding"]]
    eq = _clamp(eq_target + scale, 0.0, 0.90)
    rest = 1.0 - eq
    gold = 0.10 if risk["binding"] <= 3 else 0.07
    crypto = {1: 0.0, 2: 0.0, 3: 0.02, 4: 0.05, 5: 0.08}[risk["binding"]]
    cash = 0.05 if emg["funded"] else 0.10
    debt = max(0.0, rest - gold - crypto - cash)
    sleeves = _normalize({"equity": eq, "debt": debt, "gold": gold,
                          "crypto": crypto, "cash": cash})

    rate, dd = _weighted(sleeves)
    monthly = sip["investable_now"]
    lumpsum = profile.get("budget", 0)

    flags = []
    if emg["gate_active"]:
        flags.append(f"⚠ Build your emergency fund first (₹{emg['shortfall']:,} short of "
                     f"{emg['months']} months' expenses) — we've modeled a 2-phase start.")
    if dependents > 0:
        flags.append(f"🧑‍👧 Term cover recommended: 10-15× annual income "
                     f"(≈₹{income*12*12:,}–₹{income*12*15:,}).")
    if profile.get("existing_investments", 0) > 0:
        flags.append("Review existing holdings for concentration before adding more.")
    if age < 30:
        flags.append("Long horizon = time is your biggest asset — stay invested through dips.")

    return {
        "archetype": risk["level"], "risk": risk, "glide": glide,
        "allocation": {k: round(v * 100) for k, v in sleeves.items()},
        "sleeves_raw": sleeves, "expected_rate": rate, "worst_case_dd": dd,
        "sip": sip, "emergency": emg,
        "instruments": {k: INSTRUMENTS[k] for k, v in sleeves.items() if v > 0.01},
        "monthly_invest": monthly, "lumpsum": lumpsum,
        "flags": flags,
        "reasoning": [
            f"Age {age}: equity anchor = 110 − {age} = {glide['equity_pct']}% (target-date default).",
            f"Risk capacity {risk['capacity']}/5 vs willingness {risk['willingness']}/5 → "
            f"binding = {risk['binding']} ({risk['governed_by']}) — {risk['level']}.",
            f"Horizon {horizon:g}y → bucket mix from {'<3y' if horizon<3 else '3-7y' if horizon<7 else '7-15y' if horizon<15 else '15y+'} rule.",
            f"SIP capacity: {sip['note']}",
        ] + (["Emergency gate active: safety margin overrides aggression."] if emg["gate_active"] else []),
    }


def custom_plan(equity: float, debt: float, gold: float, crypto: float,
                cash: float, monthly: float, lumpsum: float, horizon_years: float) -> dict:
    """User-built plan: normalize sliders, project, and warn on profile conflicts."""
    sleeves = _normalize({"equity": equity / 100, "debt": debt / 100, "gold": gold / 100,
                          "crypto": crypto / 100, "cash": cash / 100})
    rate, dd = _weighted(sleeves)
    warnings = []
    if sleeves["crypto"] > 0.10:
        warnings.append("Crypto above 10% is speculative — consider capping at 5%.")
    if horizon_years < 3 and sleeves["equity"] > 0.30:
        warnings.append(f"Money needed within 3 years shouldn't sit in >30% equity "
                        f"(a {MAXDD['equity']:.0%} fall could arrive right when you need it).")
    if sleeves["equity"] > 0.85:
        warnings.append("Equity >85%: expect swings of a third of your money without flinching.")
    if sleeves["cash"] > 0.40:
        warnings.append("Heavy cash: inflation will quietly erode long-term value.")
    return {
        "allocation": {k: round(v * 100) for k, v in sleeves.items()},
        "expected_rate": rate, "worst_case_dd": dd,
        "monthly_invest": monthly, "lumpsum": lumpsum,
        "instruments": {k: INSTRUMENTS[k] for k, v in sleeves.items() if v > 0.01},
        "warnings": warnings or ["Allocation is within sane guard-rails. ✅"],
        "tradeoff": f"+{rate:.1%} expected vs {dd:.0%} worst-case — higher equity buys "
                    f"return with bigger scary drops.",
    }


def project_total(monthly: float, lumpsum: float, rate: float, years: int) -> list[dict]:
    """Year-by-year FV for the contribution-vs-growth area chart."""
    i, rows, fv = rate / 12, [], lumpsum
    for y in range(1, years + 1):
        for _ in range(12):
            fv = fv * (1 + i) + monthly
        invested = lumpsum + monthly * 12 * y
        rows.append({"year": y, "invested": invested, "growth": max(0.0, fv - invested),
                     "value": fv})
    return rows
