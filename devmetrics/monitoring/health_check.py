"""Playwright-based dashboard health checks.

Loads each dashboard page, verifies charts render, captures screenshots
on failure, and logs results via the event logger.
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path(__file__).parent.parent / "logs"
SCREENSHOTS_DIR = LOGS_DIR / "screenshots"


async def check_page(
    page,
    url: str,
    page_name: str,
    logger,
    timeout_ms: int = 30000,
) -> bool:
    """Navigate to a page and verify it renders.

    Returns True if the page loaded and contains expected content.
    """
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    try:
        response = await page.goto(url, wait_until="networkidle", timeout=timeout_ms)

        if response is None or response.status >= 400:
            status = response.status if response else "no response"
            screenshot_path = str(SCREENSHOTS_DIR / f"failure_{page_name}_{timestamp}.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            logger.health_check(page_name, success=False, screenshot_path=screenshot_path)
            return False

        # Wait for Streamlit to finish loading
        await page.wait_for_selector("[data-testid='stAppViewContainer']", timeout=timeout_ms)

        # Check for Plotly charts (main indicator of rendered dashboard)
        charts = await page.query_selector_all(".js-plotly-plot")
        if not charts:
            # Fallback: check for any Streamlit metric widgets
            metrics = await page.query_selector_all("[data-testid='stMetricValue']")
            if not metrics:
                screenshot_path = str(SCREENSHOTS_DIR / f"failure_{page_name}_{timestamp}.png")
                await page.screenshot(path=screenshot_path, full_page=True)
                logger.health_check(page_name, success=False, screenshot_path=screenshot_path)
                return False

        # Success — take a reference screenshot
        screenshot_path = str(SCREENSHOTS_DIR / f"success_{page_name}_{timestamp}.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        logger.health_check(page_name, success=True, screenshot_path=screenshot_path)
        return True

    except Exception as e:
        screenshot_path = str(SCREENSHOTS_DIR / f"failure_{page_name}_{timestamp}.png")
        try:
            await page.screenshot(path=screenshot_path, full_page=True)
        except Exception:
            pass
        logger.health_check(page_name, success=False, screenshot_path=screenshot_path)
        logger.error(f"Health check exception for {page_name}: {e}", page=page_name)
        return False


async def run_health_checks(base_url: str = "http://localhost:8501") -> bool:
    """Run health checks on all dashboard pages.

    Returns True if all checks pass.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
        return False

    # Import logger here to avoid circular imports at module level
    from monitoring.event_logger import EventLogger
    logger = EventLogger("health_check")

    pages_to_check = [
        ("home", f"{base_url}/"),
        ("space_dashboard", f"{base_url}/1_space_dashboard"),
        ("copilot_dashboard", f"{base_url}/2_copilot_dashboard"),
    ]

    all_passed = True

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        for page_name, url in pages_to_check:
            passed = await check_page(page, url, page_name, logger)
            if not passed:
                all_passed = False
                print(f"  ✗ {page_name} — FAILED")
            else:
                print(f"  ✓ {page_name} — OK")

        await browser.close()

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Run dashboard health checks")
    parser.add_argument(
        "--url",
        default="http://localhost:8501",
        help="Base URL of the Streamlit dashboard",
    )
    args = parser.parse_args()

    print(f"Running health checks against {args.url}...")
    passed = asyncio.run(run_health_checks(args.url))

    if passed:
        print("\n✅ All health checks passed.")
        sys.exit(0)
    else:
        print("\n❌ Some health checks failed. See logs/events.json for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
