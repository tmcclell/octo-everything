**Phase 3: Logging & Monitoring**

Automated script to verify dashboard renders correctly.

**Acceptance Criteria:**
- [ ] Playwright script loads `/space_dashboard` and `/copilot_dashboard`
- [ ] Verifies charts are present (check for Plotly elements)
- [ ] Captures screenshots of each page
- [ ] Logs success/failure to `logs/events.json`
- [ ] Runs on schedule (e.g., every 6 hours)
- [ ] Exit code 0 on success, non-zero on failure

**Script Location:**
`monitoring/health_check.py`

**Playwright Actions:**
1. Launch browser
2. Navigate to dashboard pages
3. Wait for chart render (selector: `.plotly`)
4. Take screenshot → `logs/screenshots/{page}_{timestamp}.png`
5. Log result to events.json
