"""generate_ppt_themed.py — 6-slide deck styled with the *website* design system.

Mirrors app/app.py CSS tokens:
  bg #0B1D32 · surface #162D4A · text #F4F6F8 · muted #A0AEC0
  accent #00C853 · gold #E8B84B · danger #D13438 · blue #4E8FCB · steel #3E5C8A
  headings 'Sora' · body 'Inter' · kickers = uppercase + wide letter-spacing

Run:  python generate_ppt_themed.py   →  Team404_Deck_Themed.pptx
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml

from pptx.dml.color import RGBColor as C

# ---------------------------------------------------------------- design tokens
BG       = C(0x0B, 0x1D, 0x32)
SURFACE  = C(0x16, 0x2D, 0x4A)
SURF_HI  = C(0x12, 0x30, 0x52)   # slightly lifted card
BAR_BG   = C(0x0E, 0x24, 0x40)   # sidebar / window chrome
TEXT     = C(0xF4, 0xF6, 0xF8)
BODY     = C(0xC7, 0xD2, 0xDF)
MUTED    = C(0xA0, 0xAE, 0xC0)
ACCENT   = C(0x00, 0xC8, 0x53)
GOOD     = C(0x00, 0xE6, 0x76)
DANGER   = C(0xD1, 0x34, 0x38)
GOLD     = C(0xE8, 0xB8, 0x4B)
CORAL    = C(0xE8, 0x5D, 0x4A)
BLUE     = C(0x4E, 0x8F, 0xCB)
STEEL    = C(0x3E, 0x5C, 0x8A)
BORDER   = C(0x24, 0x48, 0x6F)

H_FONT, B_FONT = "Sora", "Inter"
W, H = 13.333, 7.5

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]

# ------------------------------------------------------------------- primitives
def _noline(sh):
    sh.line.fill.background()
    sh.shadow.inherit = False


def _alpha(shape, pct):
    """Apply transparency (0-100) to a solid fill."""
    sp = shape.fill._xPr.find(qn("a:solidFill"))
    clr = sp.find(qn("a:srgbClr"))
    clr.append(parse_xml('<a:alpha xmlns:a="http://schemas.openxmlformats.org/'
                         'drawingml/2006/main" val="%d"/>' % int(pct * 1000)))


def shape(slide, kind, x, y, w, h, fill=None, line=None, lw=1.0, radius=None,
          alpha=None):
    sh = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    _noline(sh)
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
        if alpha is not None:
            _alpha(sh, alpha)
    if line is not None:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sh.adjustments[0] = radius
        except Exception:
            pass
    sh.text_frame.word_wrap = True
    return sh


def card(slide, x, y, w, h, fill=SURFACE, line=BORDER, radius=0.055, lw=0.9,
         alpha=None):
    return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, lw,
                 radius, alpha)


def bar(slide, x, y, w, h, fill, alpha=None):
    return shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, fill, None,
                 alpha=alpha)


def paras(box, items, anchor="t", margins=0.0):
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE,
                          "b": MSO_ANCHOR.BOTTOM}[anchor]
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = \
        Inches(margins)
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER,
                       "r": PP_ALIGN.RIGHT}[it.get("align", "l")]
        if it.get("space_before"):
            p.space_before = Pt(it["space_before"])
        p.space_after = Pt(it.get("space_after", 0))
        if it.get("line_spacing"):
            p.line_spacing = it["line_spacing"]
        r = p.add_run()
        r.text = it["text"]
        f = r.font
        f.size = Pt(it.get("size", 12))
        f.bold = it.get("bold", False)
        f.name = it.get("font", B_FONT)
        f.color.rgb = it.get("color", TEXT)
        if it.get("spc"):
            f._rPr.set("spc", str(int(it["spc"] * 100)))
    return box


def text(slide, x, y, w, h, s, size=12, color=TEXT, bold=False, font=B_FONT,
         align="l", anchor="t", spc=None, line_spacing=None, space_after=0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    return paras(box, [dict(text=s, size=size, color=color, bold=bold, font=font,
                            align=align, spc=spc, line_spacing=line_spacing,
                            space_after=space_after)], anchor)


def pill_w(s, size=8.5, bold=True, spc=0.4, pad=0.34):
    """Rough width of a pill: uppercase/bold in Inter runs ~0.66em per char."""
    per = 0.66 if bold else 0.58
    return (len(s) * (per * size + spc) / 72.0) + pad


def pill(slide, x, y, s, fg=ACCENT, fill=ACCENT, alpha=14, size=8.5, h=0.30,
         border=True, spc=0.4, bold=True):
    w = pill_w(s, size, bold, spc)
    sh = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h,
               fill, fill if border else None, 0.75, 0.5, alpha)
    paras(sh, [dict(text=s, size=size, color=fg, bold=bold, font=B_FONT,
                    align="c", spc=spc)], "m")
    return w


def new_slide():
    s = prs.slides.add_slide(BLANK)
    f = s.background.fill
    f.solid()
    f.fore_color.rgb = BG
    # soft radial glow (top-left) — same trick the site hero uses
    g = shape(s, MSO_SHAPE.OVAL, -3.4, -3.0, 8.6, 6.2, STEEL, alpha=26)
    g2 = shape(s, MSO_SHAPE.OVAL, 9.4, 4.9, 6.8, 5.0, STEEL, alpha=18)
    return s


def header(s, kicker, title, size=27, tw=12.2):
    text(s, 0.6, 0.40, 8.0, 0.26, kicker, 10.5, ACCENT, True, B_FONT, spc=1.8)
    text(s, 0.58, 0.72, tw, 0.95, title, size, TEXT, True, H_FONT,
         line_spacing=1.06)
    bar(s, 0.6, 1.55, 1.35, 0.045, ACCENT)


def footer(s, n, label="Team404 · Matrix Hackathon 2026"):
    bar(s, 0.6, 6.92, 12.13, 0.012, BORDER, alpha=70)
    text(s, 0.6, 7.00, 7.0, 0.26, label, 8, MUTED, False, B_FONT, spc=0.6)
    text(s, 11.4, 7.00, 1.33, 0.26, "0%d" % n, 8, ACCENT, True, B_FONT,
         align="r", spc=0.6)


def note(s, x, y, w, h, color, head, sub=None, tint=10):
    """Website .t4-note: colour-coded left rule + tinted body."""
    card(s, x, y, w, h, SURFACE, BORDER, 0.07, 0.8, alpha=55)
    bar(s, x + 0.02, y + 0.06, 0.055, h - 0.12, color)
    items = [dict(text=head, size=11.5, color=TEXT, bold=True, font=B_FONT,
                  space_after=3 if sub else 0)]
    if sub:
        items.append(dict(text=sub, size=9.5, color=MUTED, font=B_FONT))
    paras(s.shapes.add_textbox(Inches(x + 0.22), Inches(y),
                               Inches(w - 0.4), Inches(h)), items, "m")


# =============================================================== SLIDE 1 · HERO
s = new_slide()

text(s, 0.85, 1.42, 7.2, 0.28,
     "MATRIX HACKATHON 2026  ·  DRKVSRIT × DATA SCIENCE", 11, ACCENT, True,
     B_FONT, spc=1.9)
text(s, 0.83, 1.86, 7.1, 2.35, "AI-Powered Personal\nInvestment Advisor",
     43, TEXT, True, H_FONT, line_spacing=1.05)
bar(s, 0.86, 4.22, 1.5, 0.055, ACCENT)
text(s, 0.85, 4.46, 6.9, 0.9,
     "Advice that doesn’t just tell you what to do — it proves why, "
     "against real market data.", 14.5, BODY, False, B_FONT, line_spacing=1.5)

cx = 0.85
for lab, col in [("5-step wizard", ACCENT), ("Real market data", BLUE),
                 ("Offline-safe AI", GOLD), ("100% free", GOOD)]:
    cx += pill(s, cx, 5.42, lab, col, col, 14, 9.5, 0.34) + 0.14

text(s, 0.85, 6.10, 7.2, 0.3,
     "Team404 — A.kruthika · Shaik Zeeshan · M. Farhan Adil · M. Noel",
     13, TEXT, True, B_FONT)
text(s, 0.85, 6.44, 7.2, 0.28, "DRKVSRIT × Data Science · 1 Oct 2026",
     10, MUTED, False, B_FONT, spc=0.5)

# --- product mock (right) -----------------------------------------------------
mx, my, mw, mh = 8.35, 1.35, 4.3, 5.05
card(s, mx, my, mw, mh, SURFACE, BORDER, 0.045, 1.0)
bar(s, mx + 0.01, my + 0.01, mw - 0.02, 0.42, BAR_BG)
for i, col in enumerate([CORAL, GOLD, ACCENT]):
    shape(s, MSO_SHAPE.OVAL, mx + 0.22 + i * 0.24, my + 0.155, 0.12, 0.12, col)
text(s, mx + 1.05, my + 0.10, 2.6, 0.26, "advisor · step 4 of 5", 8.5, MUTED,
     False, B_FONT, spc=0.5)

# mini rail
rail = ["1", "2", "3", "4", "5"]
step_x = [mx + 0.62 + i * 0.78 for i in range(5)]
bar(s, step_x[0], my + 0.86, step_x[-1] - step_x[0], 0.03, BORDER)
for i, x0 in enumerate(step_x):
    active = i == 3
    if active:
        shape(s, MSO_SHAPE.OVAL, x0 - 0.19, my + 0.68, 0.4, 0.4, ACCENT,
              alpha=22)
    shape(s, MSO_SHAPE.OVAL, x0 - 0.09, my + 0.78, 0.2, 0.2,
          ACCENT if active else BAR_BG, ACCENT if active else BORDER, 0.9)
    text(s, x0 - 0.2, my + 0.80, 0.4, 0.2, rail[i], 7,
         BG if active else MUTED, True, B_FONT, align="c")

text(s, mx + 0.3, my + 1.28, 3.8, 0.24, "STEP 4 · RECOMMENDATION", 8, ACCENT,
     True, B_FONT, spc=1.4)
text(s, mx + 0.3, my + 1.54, 3.8, 0.3, "Recommended for you", 14, TEXT, True,
     H_FONT)

# allocation bar
alloc = [(0.76, ACCENT, "76%"), (0.15, BLUE, "15%"), (0.09, GOLD, "9%")]
bx, bw = mx + 0.3, 3.7
for frac, col, lab in alloc:
    w = bw * frac - 0.03
    bar(s, bx, my + 2.0, w, 0.3, col, alpha=88)
    bx += bw * frac
text(s, mx + 0.3, my + 2.38, 3.8, 0.24, "EQUITY 76%  ·  DEBT 15%  ·  GOLD 9%",
     7.5, MUTED, True, B_FONT, spc=0.7)

for i, (lab, val, col) in enumerate([("EXPECTED RETURN", "11.2%", GOOD),
                                     ("WORST-CASE", "−18%", GOLD)]):
    ox = mx + 0.3 + i * 1.9
    text(s, ox, my + 2.78, 1.8, 0.22, lab, 7, MUTED, True, B_FONT, spc=0.8)
    text(s, ox, my + 3.00, 1.8, 0.34, val, 17, col, True, H_FONT)

note(s, mx + 0.3, my + 3.52, 3.7, 0.7, ACCENT,
     "Emergency fund covered → equity unlocked",
     "rule: 6 months expenses before any equity")

# ============================================================= SLIDE 2 · PROBLEM
s = new_slide()
header(s, "THE PROBLEM", "One decision, four hidden inputs — nothing connects them")

text(s, 0.6, 1.86, 5.4, 0.26, "WHAT ACTUALLY DECIDES THE ANSWER", 9.5, ACCENT,
     True, B_FONT, spc=1.4)
inputs = [("₹", "Budget", "income − expenses − dependents", ACCENT),
          ("↑", "Experience", "beginner or seasoned investor", BLUE),
          ("⌂", "Background", "prior assets, past losses", GOLD),
          ("◎", "Risk comfort", "willingness vs. real capacity", CORAL)]
for i, (gl, name, sub, col) in enumerate(inputs):
    x = 0.6 + (i % 2) * 2.78
    y = 2.24 + (i // 2) * 1.5
    card(s, x, y, 2.6, 1.3, SURFACE, BORDER, 0.08, 0.9)
    ic = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.2, y + 0.2, 0.42, 0.42,
               col, radius=0.28, alpha=22)
    paras(ic, [dict(text=gl, size=14, color=col, bold=True, font=B_FONT,
                    align="c")], "m")
    text(s, x + 0.74, y + 0.24, 1.7, 0.28, name, 12.5, TEXT, True, H_FONT)
    text(s, x + 0.2, y + 0.74, 2.25, 0.5, sub, 9, MUTED, False, B_FONT,
         line_spacing=1.3)

note(s, 0.6, 5.34, 5.38, 0.86, DANGER, "Result: everyone gets the same "
     "generic tip.", "No tool reads all four together.")

arw = shape(s, MSO_SHAPE.RIGHT_ARROW, 6.18, 3.30, 0.78, 0.62, STEEL)
_alpha(arw, 100)

card(s, 7.18, 2.24, 5.55, 3.0, SURFACE, DANGER, 0.05, 1.0, alpha=70)
bar(s, 7.20, 2.30, 0.06, 2.88, DANGER)
xb = shape(s, MSO_SHAPE.OVAL, 7.46, 2.46, 0.34, 0.34, DANGER, alpha=22)
paras(xb, [dict(text="✕", size=12, color=DANGER, bold=True, align="c")], "m")
text(s, 7.92, 2.46, 4.5, 0.34, "What people get today", 15, TEXT, True, H_FONT)
for i, t in enumerate(["Same portfolio advice, regardless of context",
                       "Past losses never explained — only regret",
                       "Decisions run on hype, panic and FOMO"]):
    text(s, 7.52, 3.05 + i * 0.62, 0.3, 0.3, "✕", 11, DANGER, True, B_FONT)
    text(s, 7.86, 3.05 + i * 0.62, 4.6, 0.55, t, 11.5, BODY, False, B_FONT,
         line_spacing=1.3)

note(s, 7.18, 5.44, 5.55, 0.76, GOLD,
     "The gap: emotion fills in where data is missing.",
     "A beginner cannot tell signal from noise.")

footer(s, 2)

# ============================================================= SLIDE 3 · APPROACH
s = new_slide()
header(s, "OUR APPROACH", "A 5-step wizard that asks what real advice needs")

cw, gap = 2.3, 0.18
x0 = (W - (5 * cw + 4 * gap)) / 2
centers = [x0 + i * (cw + gap) + cw / 2 for i in range(5)]

rail_card = card(s, x0 - 0.16, 1.82, 5 * cw + 4 * gap + 0.32, 1.02, BAR_BG,
                 BORDER, 0.06, 0.9)
bar(s, centers[0], 2.22, centers[-1] - centers[0], 0.03, BORDER)
bar(s, centers[0], 2.22, centers[-1] - centers[0], 0.03, ACCENT, alpha=45)
labels = ["PROFILE", "LOSS ANALYSIS", "RISK CHECK", "DUAL PLAN", "OPTIMIZER"]
for i, c in enumerate(centers):
    active = i < 4
    shape(s, MSO_SHAPE.OVAL, c - 0.17, 2.06, 0.34, 0.34,
          ACCENT if active else BAR_BG, ACCENT if active else BORDER, 1.0)
    text(s, c - 0.2, 2.13, 0.4, 0.22, str(i + 1), 9,
         BG if active else MUTED, True, B_FONT, align="c")
    text(s, c - 1.15, 2.50, 2.3, 0.24, labels[i], 8,
         ACCENT if active else MUTED, True, B_FONT, align="c", spc=1.0)

steps = [
    ("Profile", "Age, income, expenses, dependents, goals, emergency fund, risk 1–5", "RULE"),
    ("Loss analysis", "Your dates matched to real price history — cause, not guesswork", "LIVE"),
    ("Risk check", "Capacity × willingness: the lower of the two binds", "RULE"),
    ("Dual plan", "Recommended-for-you and build-your-own, with reasoning shown", "RULE"),
    ("Optimizer", "Dip → top-up · drift → rebalance · volatility spike → hold", "LIVE"),
]
for i, (name, body, tag) in enumerate(steps):
    x = x0 + i * (cw + gap)
    card(s, x, 3.10, cw, 2.62, SURFACE, BORDER, 0.07, 0.9)
    badge = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.2, 3.3, 0.38, 0.38,
                  ACCENT, radius=0.3, alpha=22)
    paras(badge, [dict(text=str(i + 1), size=13, color=ACCENT, bold=True,
                       font=H_FONT, align="c")], "m")
    text(s, x + 0.68, 3.34, 1.5, 0.3, name, 12.5, TEXT, True, H_FONT)
    text(s, x + 0.2, 3.86, cw - 0.4, 1.3, body, 9.5, BODY, False, B_FONT,
         line_spacing=1.35)
    if tag == "LIVE":
        pill(s, x + 0.2, 5.22, "● LIVE DATA", GOOD, ACCENT, 14, 7.5, 0.26)
    else:
        pill(s, x + 0.2, 5.22, "RULE ENGINE", BLUE, BLUE, 14, 7.5, 0.26)

note(s, x0 - 0.16, 5.94, 5 * cw + 4 * gap + 0.32, 0.76, ACCENT,
     "Deterministic AI — runs offline, no API key, cannot crash on an outage.",
     "Every number is computed in-app from yfinance data (12 live tickers).")
footer(s, 3)

# ============================================================== SLIDE 4 · ENGINE
s = new_slide()
header(s, "INSIDE THE ENGINE", "Every claim is proven against real market data")

# --- left: loss taxonomy -----------------------------------------------------
card(s, 0.6, 1.82, 6.1, 2.86, SURFACE, BORDER, 0.05, 0.9)
text(s, 0.85, 2.02, 5.6, 0.3, "1  ·  Why you lost — named & evidenced", 14,
     TEXT, True, H_FONT)
tags = [("PEAK_BUY", DANGER), ("PANIC_SELL", CORAL), ("HYPE_CHASE", GOLD),
        ("CONCENTRATION", BLUE), ("HOLD_THROUGH_CRASH", STEEL),
        ("MISMATCH_RISK", ACCENT)]
tx, ty = 0.85, 2.48
for lab, col in tags:
    w = pill_w(lab, 8, True, 0.4)
    if tx + w > 6.45:
        tx, ty = 0.85, ty + 0.44
    tx += pill(s, tx, ty, lab, col, col, 15, 8, 0.30) + 0.14

card(s, 0.85, 3.44, 5.6, 1.0, BAR_BG, BORDER, 0.07, 0.8, alpha=70)
bar(s, 0.87, 3.50, 0.055, 0.88, GOLD)
paras(s.shapes.add_textbox(Inches(1.05), Inches(3.44), Inches(5.25),
                           Inches(1.0)), [
    dict(text="“You bought 11 Feb, within 0.8% of the 90-day high — "
              "and exited 8.8% below the 30-day high.”", size=10.5,
         color=BODY, font=B_FONT, line_spacing=1.3, space_after=4),
    dict(text="evidence from real price history · explained in beginner language",
         size=8.5, color=MUTED, font=B_FONT)], "m")

# --- right: dual plan --------------------------------------------------------
card(s, 6.95, 1.82, 5.78, 2.86, SURFACE, BORDER, 0.05, 0.9)
text(s, 7.2, 2.02, 5.3, 0.3, "2  ·  Dual plan — ours and yours", 14, TEXT,
     True, H_FONT)

card(s, 7.2, 2.46, 2.72, 1.42, BAR_BG, BORDER, 0.07, 0.8, alpha=75)
text(s, 7.38, 2.58, 2.4, 0.26, "Recommended for you", 10.5, TEXT, True, H_FONT)
bx, bw = 7.38, 2.34
for frac, col in [(0.76, ACCENT), (0.15, BLUE), (0.09, GOLD)]:
    bar(s, bx, 2.94, bw * frac - 0.03, 0.2, col, alpha=88)
    bx += bw * frac
text(s, 7.38, 3.24, 2.4, 0.5, "110 − age glide path\n+ emergency-fund gate",
     8.5, MUTED, False, B_FONT, line_spacing=1.3)

card(s, 10.1, 2.46, 2.4, 1.42, BAR_BG, BORDER, 0.07, 0.8, alpha=75)
text(s, 10.28, 2.58, 2.1, 0.26, "Build your own", 10.5, TEXT, True, H_FONT)
for i, frac in enumerate([0.7, 0.42, 0.55]):
    y = 2.96 + i * 0.24
    bar(s, 10.28, y, 1.7, 0.055, BORDER, alpha=80)
    shape(s, MSO_SHAPE.OVAL, 10.28 + 1.7 * frac - 0.07, y - 0.05, 0.15, 0.15,
          [ACCENT, BLUE, GOLD][i])
text(s, 10.28, 3.66, 2.1, 0.2, "live sliders · trade-off curve", 7.5, MUTED,
     False, B_FONT)

text(s, 7.2, 3.98, 5.3, 0.56,
     "High-risk path: live momentum, volatility & drawdown per pick   ·   "
     "Low-risk path: SIP 3 / 5 / 10-year scenarios", 9.5, BODY, False, B_FONT,
     line_spacing=1.35)

# --- rule strip --------------------------------------------------------------
rules = [("110 − age", "equity glide path — the older you get, the safer",
          ACCENT),
         ("min(capacity, willingness)", "enthusiasm ≠ capacity — the lower binds",
          BLUE),
         ("6-month fund gate", "no equity until the emergency fund is full",
          GOLD)]
rw, rgap = 3.95, 0.2
for i, (val, sub, col) in enumerate(rules):
    x = 0.6 + i * (rw + rgap)
    card(s, x, 4.94, rw, 1.34, SURFACE, BORDER, 0.07, 0.9, alpha=80)
    bar(s, x + 0.02, 5.0, 0.055, 1.22, col)
    text(s, x + 0.28, 5.14, rw - 0.5, 0.4, val, 15, col, True, H_FONT)
    text(s, x + 0.28, 5.6, rw - 0.5, 0.5, sub, 9.5, MUTED, False, B_FONT,
         line_spacing=1.3)

text(s, 0.6, 6.42, 12.1, 0.3,
     "Advisory logic is transparent: every flag, badge and number traces back "
     "to a rule or a real price.", 10, MUTED, False, B_FONT, align="c")
footer(s, 4)

# ================================================================ SLIDE 5 · DEMO
s = new_slide()
header(s, "LIVE DEMO", "From intake to optimizer — five steps, one sitting")

sl = ["PROFILE", "LOSS", "RISK", "PLAN", "OPTIMIZE"]
lit = [True, False, False, True, True]
sw = 2.2
sx0 = (W - (5 * sw)) / 2 + 0.15
cens = [sx0 + i * sw + sw / 2 for i in range(5)]
bar(s, cens[0], 2.02, cens[-1] - cens[0], 0.022, BORDER)
for i, c in enumerate(cens):
    col = ACCENT if lit[i] else BORDER
    shape(s, MSO_SHAPE.OVAL, c - 0.075, 1.945, 0.15, 0.15, col)
    text(s, c - 1.0, 2.16, 2.0, 0.22, "%d · %s" % (i + 1, sl[i]), 7.5,
         ACCENT if lit[i] else MUTED, lit[i], B_FONT, align="c", spc=0.9)

shots = [("step1_profile.png", "1", "Rich intake",
          "Age 28 · ₹80k income · goal in 12y · risk 4/5"),
         ("step4_recommended.png", "4", "Dual plan",
          "76% equity, guard-rail flags, step-by-step why"),
         ("step5_optimizer.png", "5", "Optimizer",
          "Live signals: dip → top-up · drift → rebalance")]
fw, fgap = 3.95, 0.18
fx0 = 0.6
img_h = (fw - 0.16) / (1440 / 950)
for i, (fn, num, name, sub) in enumerate(shots):
    x = fx0 + i * (fw + fgap)
    y = 2.52
    card(s, x, y, fw, 0.34 + img_h + 0.08, BAR_BG, BORDER, 0.03, 1.0)
    for k, col in enumerate([CORAL, GOLD, ACCENT]):
        shape(s, MSO_SHAPE.OVAL, x + 0.14 + k * 0.18, y + 0.12, 0.10, 0.10, col)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.75, y + 0.075, fw - 0.9, 0.20,
          BG, radius=0.5, alpha=60)
    text(s, x + 0.86, y + 0.09, fw - 1.0, 0.18, "localhost:8501", 7, MUTED,
         False, B_FONT)
    s.shapes.add_picture(os.path.join("shots", fn), Inches(x + 0.08),
                         Inches(y + 0.34), width=Inches(fw - 0.16))
    cy = y + 0.34 + img_h + 0.18
    badge = shape(s, MSO_SHAPE.OVAL, x, cy, 0.34, 0.34, ACCENT, alpha=22)
    paras(badge, [dict(text=num, size=11, color=ACCENT, bold=True, font=H_FONT,
                       align="c")], "m")
    text(s, x + 0.44, cy + 0.01, fw - 0.5, 0.3, name, 12.5, TEXT, True, H_FONT)
    text(s, x, cy + 0.42, fw - 0.1, 0.5, sub, 9.5, MUTED, False, B_FONT,
         line_spacing=1.3)

text(s, 0.6, 6.5, 12.1, 0.3,
     "Steps 2 & 3 (loss proof and risk check) run on the same rail — one flow, "
     "no dead ends.", 9.5, MUTED, False, B_FONT, align="c")
footer(s, 5)

# ============================================================== SLIDE 6 · IMPACT
s = new_slide()
header(s, "IMPACT", "From regret to discipline")

metrics = [("5", "GUIDED STEPS, ZERO JARGON", GOOD),
           ("12", "LIVE TICKERS VIA YFINANCE", BLUE),
           ("0", "API KEYS — OFFLINE-SAFE", GOLD),
           ("₹0", "COST — FREE & OPEN", CORAL)]
mw, mgap = 2.95, 0.17
for i, (val, lab, col) in enumerate(metrics):
    x = 0.6 + i * (mw + mgap)
    card(s, x, 1.84, mw, 1.2, SURFACE, BORDER, 0.08, 0.9, alpha=85)
    text(s, x + 0.24, 1.99, mw - 0.4, 0.24, lab, 7.5, MUTED, True, B_FONT,
         spc=1.1)
    text(s, x + 0.22, 2.24, mw - 0.4, 0.6, val, 27, col, True, H_FONT)

outs = [("✓", "Explained, not told", "Beginners see the why behind every "
         "number — no jargon, no guesswork.", ACCENT),
        ("↺", "Losses become lessons", "Past mistakes are proven with real "
         "price history, then turned into rules.", GOLD),
        ("↑", "Habits over hype", "SIP and rebalancing replace panic, FOMO "
         "and regret.", BLUE)]
ow, ogap = 3.95, 0.2
for i, (gl, name, sub, col) in enumerate(outs):
    x = 0.6 + i * (ow + ogap)
    card(s, x, 3.3, ow, 1.86, SURFACE, BORDER, 0.06, 0.9)
    bar(s, x + 0.02, 3.38, 0.055, 1.7, col)
    ic = shape(s, MSO_SHAPE.OVAL, x + 0.3, 3.56, 0.44, 0.44, col, alpha=22)
    paras(ic, [dict(text=gl, size=14, color=col, bold=True, align="c")], "m")
    text(s, x + 0.3, 4.14, ow - 0.6, 0.3, name, 13.5, TEXT, True, H_FONT)
    text(s, x + 0.3, 4.5, ow - 0.6, 0.6, sub, 9.5, MUTED, False, B_FONT,
         line_spacing=1.35)

close = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.6, 5.46, 12.13, 1.16,
              ACCENT, radius=0.16, alpha=16)
close.line.color.rgb = ACCENT
close.line.width = Pt(1.0)
text(s, 1.0, 5.66, 7.6, 0.4, "Thank you — Team404", 21, TEXT, True, H_FONT)
text(s, 1.02, 6.12, 7.8, 0.34,
     "AI-Powered Personal Investment Advisor · background analysis & "
     "risk-based planning", 10, BODY, False, B_FONT)
# two right-aligned pills inside the closing strip
labels = ["real market data", "offline-safe"]
widths = [pill_w(t, 8, True, 0.4) for t in labels]
px = 12.46 - sum(widths) - 0.16
for t, w in zip(labels, widths):
    pill(s, px, 5.96, t, GOOD, ACCENT, 16, 8, 0.32)
    px += w + 0.16
text(s, 9.0, 5.62, 3.46, 0.26, "DRKVSRIT × DATA SCIENCE", 8.5, ACCENT, True,
     B_FONT, align="c", spc=1.4)
footer(s, 6)

out = "Team404_Deck_Themed.pptx"
prs.save(out)
print("saved", out, "·", len(prs.slides._sldIdLst), "slides")
