**Phase 3: Logging & Monitoring**

Structured event logging for API errors, rate limits, data anomalies.

**Acceptance Criteria:**
- [ ] All collectors log key events to `logs/events.json`
- [ ] Events include: timestamp, level, source, message, context
- [ ] API errors logged with status code and endpoint
- [ ] Rate limit hits logged with retry-after time
- [ ] Data anomalies logged (e.g., zero PRs returned, missing dates)
- [ ] Python `logging` module configured for structured output

**Event Schema:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "ERROR",
  "source": "space_collector",
  "message": "API rate limit exceeded",
  "context": {
    "endpoint": "/repos/owner/repo/pulls",
    "status_code": 429,
    "retry_after": 3600
  }
}
```

**Logger Location:**
`monitoring/event_logger.py`
