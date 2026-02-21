**Phase 3: Logging & Monitoring**

Capture screenshots when Playwright health checks fail.

**Acceptance Criteria:**
- [ ] On health check failure, Playwright captures full-page screenshot
- [ ] Screenshot saved to `logs/screenshots/failure_{page}_{timestamp}.png`
- [ ] Failure event logged to `logs/events.json` with screenshot path
- [ ] Screenshots retained for 30 days (cleanup script optional)

**Dependencies:**
Requires Playwright Health Checks implementation (issue #12).

**Tech:**
- Playwright `page.screenshot()` API
- Error handling in `monitoring/health_check.py`
