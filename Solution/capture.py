"""capture.py — screenshots the rebuilt UI (all 5 steps + both plan paths).
Run: python capture.py  (app must be running on :8501)  → shots/stepN_*.png"""
import asyncio, os, re, sys
from playwright.async_api import async_playwright

BASE = "http://localhost:8501"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(OUT, exist_ok=True)


async def wait_h(page, text, timeout=60000):
    await page.get_by_role("heading", name=re.compile(re.escape(text))).first.wait_for(timeout=timeout)


async def shot(page, name, settle=1500):
    await page.wait_for_timeout(settle)
    await page.screenshot(path=os.path.join(OUT, name), full_page=False)
    print("shot:", name)


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 950})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

        # ---------- PATH A: rich profile + loss + YES ----------
        await page.goto(BASE, wait_until="networkidle")
        await wait_h(page, "Tell us about you")
        # rich intake
        await page.get_by_label("Age", exact=True).fill("28")
        await page.get_by_label("Monthly income (₹)").fill("80000")
        await page.get_by_label("Monthly expenses (₹)").fill("45000")
        await page.get_by_label("Emergency fund saved (₹)").fill("15000")
        await page.get_by_label("Existing investments (₹)").fill("50000")
        await page.get_by_label("Investment budget — lumpsum (₹)").fill("100000")
        await page.get_by_label("What have you held before? (stocks / gold / crypto / mutual funds…)").fill("stocks, gold")
        # loss section
        await page.get_by_text("I've taken a loss before").click()
        await page.wait_for_timeout(700)
        await page.get_by_label("Asset you lost money on").fill("crypto")
        await page.get_by_label("Amount lost (₹)").fill("80000")
        await page.get_by_label("Rough buy date").fill("2025-02-11")
        await page.get_by_label("Rough exit date").fill("2025-03-13")
        await page.get_by_label("Why do you think it happened?").fill(
            "bought after hype on twitter, panic-sold during the crash")
        await shot(page, "step1_profile.png", 1000)
        await page.get_by_role("button", name="Continue →").click()
        await wait_h(page, "Let's learn what happened")
        await shot(page, "step2_loss_analysis.png", 2500)
        await page.get_by_role("button", name="Continue to risk choice →").click()
        await wait_h(page, "One question that steers")
        await shot(page, "step3_risk.png")
        await page.get_by_role("button", name="Yes — go aggressive").click()
        await wait_h(page, "Here it is — your personalized")
        await page.wait_for_timeout(4000)  # charts + balloons settle
        await shot(page, "step4_recommended.png", 2000)
        # custom tab
        await page.get_by_role("tab", name=re.compile("Build your own")).click()
        await page.wait_for_timeout(1500)
        await shot(page, "step4_custom.png")
        # high-risk picks tab
        await page.get_by_role("tab", name=re.compile("High-risk picks")).click()
        await page.wait_for_timeout(3500)
        await shot(page, "step4_high_risk.png")
        # optimizer
        await page.get_by_role("button", name="Continue to ongoing optimizer").click()
        await wait_h(page, "Your plan, kept healthy")
        await page.wait_for_timeout(3000)
        await shot(page, "step5_optimizer.png")

        # ---------- PATH B: no loss → safe SIP ----------
        await page.get_by_role("button", name="Start over").click()
        await wait_h(page, "Tell us about you")
        await page.get_by_label("Age", exact=True).fill("35")
        await page.get_by_label("Monthly income (₹)").fill("120000")
        await page.get_by_label("Monthly expenses (₹)").fill("70000")
        await page.get_by_label("Emergency fund saved (₹)").fill("300000")
        await page.get_by_role("button", name="Continue →").click()
        await wait_h(page, "One question that steers")   # no loss → skips step 2
        await page.get_by_role("button", name="No — keep it safe").click()
        await wait_h(page, "Here it is — your personalized")
        await page.wait_for_timeout(4000)
        await page.get_by_role("tab", name=re.compile("Safe SIP")).click()
        await page.wait_for_timeout(3000)
        await shot(page, "step4_safe_sip.png")

        await browser.close()
        real = [e for e in errors if not any(x in e for x in ("favicon", "404", "net::"))]
        if real:
            print("PAGE ERRORS:")
            for e in real[:6]: print(" -", e[:220])
            sys.exit(1)
        print("ALL SHOTS OK ✅")


asyncio.run(main())
