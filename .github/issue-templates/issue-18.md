**Cross-Cutting**

Provide environment variable template for configuration.

**Acceptance Criteria:**
- [ ] `.env.example` file created with all required variables
- [ ] Comments explain each variable
- [ ] Example values provided (placeholders, not real tokens)
- [ ] Linked from README setup instructions
- [ ] Never commit actual `.env` file (gitignored)

**Variables:**
```bash
# GitHub Personal Access Token (classic or fine-grained)
# Scopes: repo, read:org, manage_billing:copilot (or read:enterprise)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Organization/Enterprise for Copilot metrics
GITHUB_ORG=your-org-name
GITHUB_ENTERPRISE=your-enterprise-name

# Repositories to track for SPACE metrics (comma-separated)
GITHUB_REPOS=owner/repo1,owner/repo2,owner/repo3

# ROI Calculator defaults
COPILOT_SECONDS_PER_ACCEPTANCE=55
DEVELOPER_HOURLY_RATE=75
```

**File Location:**
`.env.example` at project root.
