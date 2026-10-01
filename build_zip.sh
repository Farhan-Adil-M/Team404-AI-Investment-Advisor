#!/usr/bin/env bash
# build_zip.sh — assemble + verify the 8-item submission ZIP (RULES #2, #8)
set -e
cd "$(dirname "$0")"
STAGE="Team404_Submission"
rm -rf "$STAGE" Team404_Submission.zip

mkdir -p "$STAGE"
cp -r Solution/app "$STAGE/app"
cp Solution/README.md Solution/Team404_Deck.pptx Solution/DEMO_SCRIPT.md \
   Solution/RULES.md Solution/DESIGN.md Solution/RESEARCH.md "$STAGE/"
cp -r Solution/shots "$STAGE/screenshots"
[ -f "Problem Statement.pdf" ] && cp "Problem Statement.pdf" "$STAGE/" || true

# clean junk (DQ guard)
find "$STAGE" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" -name "*.pyc" -delete 2>/dev/null || true

# --- verify 8 mandatory items ---
fail=0
check() { if [ -e "$1" ]; then echo "  ✅ $1"; else echo "  ❌ MISSING: $1"; fail=1; fi; }
echo "Verifying ZIP contents:"
check "$STAGE/README.md"
check "$STAGE/app/app.py"
check "$STAGE/Team404_Deck.pptx"
ls "$STAGE/screenshots"/*.png >/dev/null 2>&1 && echo "  ✅ screenshots/*.png" || { echo "  ❌ MISSING: screenshots"; fail=1; }
check "$STAGE/app/requirements.txt"
grep -q "streamlit run" "$STAGE/README.md" && echo "  ✅ run instructions in README" || { echo "  ❌ no run instructions"; fail=1; }
check "$STAGE/DEMO_SCRIPT.md"
grep -q "Team404" "$STAGE/README.md" && grep -q "Kruthika\|kruthika" "$STAGE/README.md" && echo "  ✅ team details" || { echo "  ❌ team details"; fail=1; }

[ "$fail" -eq 0 ] || { echo "ZIP NOT BUILT — fix missing items"; exit 1; }
python3 - <<'PY'
import shutil, os
shutil.make_archive("Team404_Submission", "zip", ".", "Team404_Submission")
print("zipped:", os.path.getsize("Team404_Submission.zip"), "bytes")
PY
echo "✅ Team404_Submission.zip built ($(du -h Team404_Submission.zip | cut -f1))"
