"""capture.py — walks the live app UI and screenshots all 5 steps (both plan paths).
Run: python capture.py  (app must be running on :8501)  → shots/stepN_*.png"""
import asyncio, os, sys
from playwright.async_api import async_playwright

BASE = "http://localhost:8501"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(OUT, exist_ok=True)


async def wait_header(page, text, timeout=45000):
    await page.get_by_role("heading", name=lambda n: text in n).first.wait_for(timeout=timeout)


async def shot(page, name):
    await page.wait_for_timeout(1200)  # let charts settle
    await page.screenshot(path=os.path.join(OUT, name), full_page=False)
    print("shot:", name)


async def run_streamlit_text(page, selector, value):
    loc = page.locator(selector)
    await loc.fill("")
    await loc.fill(value)


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

        # ---------- PATH A: with loss → high risk ----------
        await page.goto(BASE, wait_until="networkidle")
        await wait_header(page, "Step 1")
        # budget default is fine; enable loss section
        await page.get_by_text("I have taken a loss before").click()
        await page.wait_for_timeout(800)
        await page.get_by_label("Asset lost in").fill("crypto")
        # dates: streamlit date inputs are text fields
        dts = page.locator('input[type="date"]')
        if await dts.count() >= 2:
            await dts.nth(0).fill("2025-02-11")
            await dts.nth(1).fill("2025-03-13")
        else:
            ti = page.get_by_label("Rough buy date")
            if await ti.count():
                await ti.first.fill("2025/02/11")
        await page.get_by_label("Why do you think it happened?").fill(
            "bought after hype, panicked and sold during the crash")
        await shot(page, "step1_profile.png")
        await page.get_by_role("button", name="Continue →").click()
        await wait_header(page, "Step 2")
        await shot(page, "step2_loss_analysis.png")
        await page.get_by_role("button", name="Continue → Risk choice →").click()
        await wait_header(page, "Step 3")
        await shot(page, "step3_risk.png")
        await page.get_by_role("button", name="YES").click()
        await wait_header(page, "Step 4")
        await page.wait_for_timeout(2500)  # charts
        await shot(page, "step4_high_risk.png")
        await page.get_by_role("button", name="Continue → Ongoing optimizer →").click()
        await wait_header(page, "Step 5")
        await shot(page, "step5_optimizer.png")

        # ---------- PATH B: no loss → safe SIP ----------
        await page.get_by_role("button", name="Start over").click()
        await wait_header(page, "Step 1")
        await page.get_by_role("button", name="Continue →").click()
        await wait_header(page, "Step 3")
        await page.get_by_role("button", name="keep it safe").click()
        await wait_header(page, "Step 4")
        await page.wait_for_timeout(2500)
        await shot(page, "step4_safe_sip.png")

        await browser.close()
        real_errors = [e for e in errors if "favicon" not in e and "404" not in e]
        if real_errors:
            print("PAGE ERRORS:"); [print(" -", e[:200]) for e in real_errors[:5]]
            sys.exit(1)
        print("ALL SHOTS OK ✅")


asyncio.run(main())
