"""GitHub API client wrapper with authentication and rate limit handling.

Wraps PyGithub for REST API v3 (repos, orgs, PRs, issues).

For GitHub Projects V2 operations (views, fields, item updates), use the
REST API directly via `gh api` or `requests`:
  - View CRUD:  POST/DELETE /users/{owner}/projectsV2/{project}/views
  - Field list: GET /users/{owner}/projectsV2/{project}/fields
  - Item updates: GraphQL updateProjectV2ItemFieldValue mutation
See .github/project-config.json for field IDs, view numbers, and CLI examples.
Docs: https://docs.github.com/en/rest/projects/views
"""

import logging
import time
from typing import Optional
from github import Github, Auth, GithubException, RateLimitExceededException
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class GitHubClient:
    """Wrapper for PyGithub with authentication and error handling."""

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client.
        
        Args:
            token: GitHub personal access token. If None, reads from GITHUB_TOKEN env var.
        """
        load_dotenv()
        self.token = token or os.getenv("GITHUB_TOKEN")
        
        if not self.token:
            raise ValueError(
                "GitHub token required. Set GITHUB_TOKEN environment variable or pass token parameter."
            )
        
        auth = Auth.Token(self.token)
        self.client = Github(auth=auth)
        self._validate_connection()
        logger.info("GitHub client initialized successfully")

    def _validate_connection(self):
        """Validate GitHub connection and log rate limit status."""
        try:
            user = self.client.get_user()
            rate_limit = self.client.get_rate_limit()
            logger.info(
                f"Authenticated as: {user.login} | "
                f"Rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit} | "
                f"Resets at: {rate_limit.core.reset}"
            )
        except GithubException as e:
            logger.error(f"GitHub authentication failed: {e}")
            raise

    def get_rate_limit(self):
        """Get current rate limit status.
        
        Returns:
            dict: Rate limit info with remaining, limit, and reset time.
        """
        rate_limit = self.client.get_rate_limit()
        return {
            "remaining": rate_limit.core.remaining,
            "limit": rate_limit.core.limit,
            "reset": rate_limit.core.reset,
            "reset_timestamp": int(rate_limit.core.reset.timestamp())
        }

    def handle_rate_limit(self):
        """Check rate limit and sleep if needed."""
        rate_limit = self.get_rate_limit()
        
        if rate_limit["remaining"] < 100:
            reset_time = rate_limit["reset_timestamp"]
            current_time = int(time.time())
            sleep_duration = max(0, reset_time - current_time + 10)
            
            logger.warning(
                f"Rate limit low ({rate_limit['remaining']} remaining). "
                f"Sleeping for {sleep_duration} seconds until reset."
            )
            time.sleep(sleep_duration)

    def get_repository(self, repo_name: str):
        """Get a repository object with rate limit handling.
        
        Args:
            repo_name: Full repository name (e.g., "owner/repo")
            
        Returns:
            Repository object
        """
        try:
            self.handle_rate_limit()
            return self.client.get_repo(repo_name)
        except RateLimitExceededException:
            logger.error("Rate limit exceeded")
            self.handle_rate_limit()
            return self.client.get_repo(repo_name)
        except GithubException as e:
            logger.error(f"Error fetching repository {repo_name}: {e}")
            raise

    def get_organization(self, org_name: str):
        """Get an organization object with rate limit handling.
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization object
        """
        try:
            self.handle_rate_limit()
            return self.client.get_organization(org_name)
        except RateLimitExceededException:
            logger.error("Rate limit exceeded")
            self.handle_rate_limit()
            return self.client.get_organization(org_name)
        except GithubException as e:
            logger.error(f"Error fetching organization {org_name}: {e}")
            raise

    def close(self):
        """Close the GitHub client connection."""
        if self.client:
            self.client.close()
            logger.info("GitHub client connection closed")
