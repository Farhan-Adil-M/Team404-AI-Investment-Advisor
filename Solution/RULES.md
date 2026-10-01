# RULES.md — Team404 Agent Workflow (Matrix Hackathon, DATA NEXUS)

**Event:** Matrix Hackathon 2026 · DRKVSRIT × Data Science · **OCT 01, 2026**
**Submission closes: 4:30 PM IST** · Evaluation/demo opens: 3:00 PM · Results: 4:45 PM
**Problem:** AI-Powered Personal Investment Advisor (see `../Problem` + `Smart AI advisor(Finance).pdf`)
**Team:** Team404 — A.kruthika, Shaik Zeeshan, M. Farhan Adil, M. Noel

These rules are derived 1:1 from the official hackathon site
(https://matrix-hackathon-seven.vercel.app/ — verified from live `/api/data`).
**Every agent in this workflow must follow them. Violations = rejected deliverable.**

---

## A. ZERO-TOLERANCE RULES (anti-disqualification, 10 DQ conditions)

| # | Rule | Anti-DQ |
|---|------|---------|
| 1 | **RUN-OR-BAN** — No agent may declare a module "done" without *executing* it. App must launch via `streamlit run` + smoke test before any handoff. The phrase "should work" is banned. | DQ#2 (code crashes live) |
| 2 | **CHECKLIST-BUILD** — `SUBMISSION_CHECKLIST.md` maintained from day one; ZIP with all 8 mandatory items is a required final phase. | DQ#1 (missing ZIP file) |
| 3 | **COMPLETE-FEATURES-FIRST** — Problem Steps 1–5 all function end-to-end before any cosmetic polish. No stubs/TODOs shipped. | DQ#3 (incomplete/non-functional) |
| 4 | **ORIGINAL-CODE-ONLY** — No cloned repos, no copied tutorials/templates. yfinance/Streamlit docs = API reference only. Every file traceable to a spawn we ran. | DQ#4 (plagiarism) |
| 5 | **REAL-DATA-OR-LABELLED** — Every chart/number comes from actual yfinance fetches. Any fallback/cached value is visibly labeled "simulated" in the UI. Faking results = reject. | DQ#5 (fake/misleading demo) |
| 6 | **PROBLEM-FIT-TRACE** — Every module tags which of Steps 1–5 it serves; orchestrator audits traceability at each phase gate. | DQ#6 (off-problem) |
| 7 | **TEAM-INFO** — README carries: Team404 + A.kruthika, Shaik Zeeshan, M. Farhan Adil, M. Noel. | DQ#7 (team info missing) |
| 8 | **DEADLINE-WORKBACK** — Working demo by 3:00 PM · ZIP done by 4:20 PM · hard stop 4:30 PM · **submit exactly once, after local ZIP verification** (multiple submissions = DQ). | DQ#8, DQ#9 |
| 9 | **CLEAN-RUN-VERIFIED** — Run instructions tested as if from a clean checkout (`requirements.txt`, exact commands, no machine-specific paths) so judges can verify unaided. | DQ#10 (judges can't verify) |

## B. JUDGING-MAXIMIZATION RULES (priority = points)

| # | Rule | Weight |
|---|------|--------|
| 10 | **LIVE-FIRST** — The demo path (profile → loss analysis → risk choice → plan → optimizer) is re-tested live repeatedly. Outranks everything. | 30 pts + **tiebreaker** |
| 11 | **INNOVATION-SPOTLIGHT** — Loss-reason narrative + ongoing optimizer are the named differentiators; extra build/review attention. | 25 pts |
| 12 | **UI-POLISH** — Charts, step flow, beginner-readable explanations. | 20 pts (+15 Impact) |
| 13 | **FIT-MAP** — README explicitly maps features → the 5 problem steps. | 10 pts |
| 14 | **PRESENT-READY** — Deck (Problem → Approach → Solution → Demo → Impact), screenshots, rehearsed 3-min demo script are deliverables, not afterthoughts. | Site rule #4 |

## C. AGENT-CONDUCT RULES

| # | Rule |
|---|------|
| 15 | **EFFICIENCY-ONLY MODELS** — Research/docs on FREE tier first (`opencode/ling-3.0-flash-fin-free`, `opencode/nemotron-3.5-lightning-free`, `opencode/mimo-v2.6-flash-free`, `opencode-go/longcat-2.5-preview-free`, `opencode-go/space-bunny-free`). Code: `opencode-go/mimo-v2.6-flash` ($0.14) → `deepseek-v4.1-flash` / `qwen3.8-flash` ($0.15). **BANNED:** `glm-5.3`, `glm-5.2`, `kimi-k2.7-code`, `kimi-k3`, `grok-4.x`, `qwen3.8-max`, `claude-*`, `gpt-6.1-sol*`, `deepseek-v4-pro`, `hy4-preview` — any model > $0.40/M input. No "strong" delegation: design/review stays with the orchestrator. |
| 16 | **ANNOUNCE-BEFORE-SPAWN** — Every spawn: tier + model + reason announced before launch. |
| 17 | **GATE-PER-PHASE** — No phase advances until its artifact exists and its checks pass (RUN-OR-BAN applies). |
| 18 | **DEMO-SAFETY** — Runtime never depends on an external LLM API (no key available). Deterministic data-driven engine is the primary "AI"; optional enrichment only if it degrades gracefully offline. |

## D. WORKFLOW (phase gates)

```
W0  RULES.md + SUBMISSION_CHECKLIST.md           ← this file (done at start)
P0  venv + pip install + live yfinance probe      gate: 1 real price fetched
P1  Researcher spawns (free tier, parallel):      gate: Solution/RESEARCH.md
      R1 model-comparison (longcat vs space-bunny vs mimo-free vs nemotron vs ling-fin)
      R2 yfinance patterns + tickers (stocks/gold/crypto/SIP proxies)
      R3 financial logic (loss taxonomy, SIP math, best-time-to-invest, risk rules)
      R4 free-LLM runtime options (keyless)       → likely: skip if <30 min ROI
P2  Design (orchestrator only)                    gate: Solution/DESIGN.md
P3  Build (code tier, module-by-module, RUN-OR-BAN):
      data layer → loss-analysis engine → risk/recommend engine
      → SIP projection + optimizer → Streamlit UI
P4  Verify: live yfinance + 3 personas end-to-end gate: full demo path green @3:00 PM
P5  Package: screenshots → README → PPT/PDF → clean-run test → 8-item ZIP
```

**Escalation:** if a spawn stalls or its output fails review → orchestrator re-spawns on the
next efficient model, never a banned one, and logs it here.

**Master priority order (invariants):** run-live > feature-complete > real-data honesty >
UI polish > deck/docs. When time runs out, cut from the bottom.
