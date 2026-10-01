"""QA: flag shapes outside slide bounds and text likely to overflow its box."""
import sys
from pptx import Presentation
from PIL import ImageFont

EMU = 914400.0
SW, SH = 13.333, 7.5

# rough per-glyph advance widths as a fraction of font size (bold ≈ wider)
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_cache = {}


def font(size, bold):
    px = max(int(size * 96 / 72), 6)
    key = (px, bold)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(BOLD if bold else REG, px)
    return _cache[key]


def width_pt(s, size, bold):
    """width in points of a single-line string"""
    f = font(size, bold)
    return f.getlength(s) * 72 / 96


def wrap_lines(s, size, bold, box_w_in):
    """number of lines after wrapping into box_w_in inches"""
    limit = box_w_in * 72
    if not s.strip():
        return 1
    lines = 0
    for hard in s.split("\n"):
        words, cur = hard.split(" "), ""
        n = 1
        for w in words:
            trial = (cur + " " + w).strip()
            if width_pt(trial, size, bold) > limit and cur:
                n += 1
                cur = w
            else:
                cur = trial
        lines += n
    return lines


issues = []
prs = Presentation(sys.argv[1] if len(sys.argv) > 1 else "Team404_Deck_Themed.pptx")
for si, slide in enumerate(prs.slides, 1):
    for sh in slide.shapes:
        x, y = sh.left / EMU, sh.top / EMU
        w, h = sh.width / EMU, sh.height / EMU
        if x < -0.01 or y < -0.01 or x + w > SW + 0.01 or y + h > SH + 0.01:
            if not (w > 4 and h > 3):   # ignore intentional glow ovals
                issues.append(f"S{si} OUT-OF-BOUNDS {sh.shape_type} "
                              f"({x:.2f},{y:.2f},{w:.2f},{h:.2f}) "
                              f"{sh.has_text_frame and sh.text_frame.text[:30]!r}")
        if not sh.has_text_frame:
            continue
        tf = sh.text_frame
        ml = tf.margin_left / EMU + tf.margin_right / EMU
        inner_w = w - ml
        total = 0.0
        for p in tf.paragraphs:
            runs = [r for r in p.runs if r.text]
            if not runs:
                continue
            size = max((r.font.size.pt if r.font.size else 18) for r in runs)
            bold = any(r.font.bold for r in runs)
            txt = "".join(r.text for r in runs)
            n = wrap_lines(txt, size, bold, inner_w)
            ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.0
            total += n * size * 1.21 * ls
            total += (p.space_after.pt if p.space_after else 0)
            total += (p.space_before.pt if p.space_before else 0)
        box_h = h * 72
        if total > box_h * 1.06:
            issues.append(f"S{si} TEXT-OVERFLOW need {total:.0f}pt > box "
                          f"{box_h:.0f}pt  @({x:.2f},{y:.2f},{w:.2f},{h:.2f}) "
                          f"{tf.text[:48]!r}")

print("\n".join(issues) if issues else "clean: no bounds/overflow issues")
print(f"--- {len(issues)} issue(s)")
