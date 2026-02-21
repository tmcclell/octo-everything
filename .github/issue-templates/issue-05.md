**Phase 1: SPACE Metrics**

Track count of open PRs per repo over time.

**Acceptance Criteria:**
- [ ] Collector counts open PRs per configured repo
- [ ] Runs on schedule (daily snapshot)
- [ ] Stores time-series data in `data/space/wip_counts.json`
- [ ] Charts WIP trends over time

**API Endpoint:**
`GET /repos/{owner}/{repo}/pulls?state=open`

**Data Schema:**
```json
{
  "date": "2024-01-15",
  "repo": "owner/repo",
  "open_pr_count": 12
}
```
