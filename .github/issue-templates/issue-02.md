**Phase 1: SPACE Metrics**

Fetch closed/merged PRs and compute open→merge duration.

**Acceptance Criteria:**
- [ ] Collector fetches closed PRs from configured repos via PyGithub
- [ ] Calculates duration between `created_at` and `merged_at`
- [ ] Stores results in `data/space/pr_cycle_times.json`
- [ ] Handles pagination for large PR sets
- [ ] Filters for merged PRs only (excludes closed-without-merge)

**API Endpoint:**
`GET /repos/{owner}/{repo}/pulls?state=closed`

**Data Schema:**
```json
{
  "pr_id": 123,
  "repo": "owner/repo",
  "created_at": "2024-01-15T10:00:00Z",
  "merged_at": "2024-01-16T14:30:00Z",
  "cycle_time_hours": 28.5
}
```
