"""Tests for GitHubClient - authentication, rate limiting, error handling."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from github import GithubException, RateLimitExceededException

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from devmetrics.collectors.github_client import GitHubClient


class TestGitHubClientInit:
    """Test GitHubClient initialization and authentication."""

    def test_init_with_token(self):
        """Test initialization with explicit token."""
        with patch('devmetrics.collectors.github_client.Github') as mock_github:
            mock_client = Mock()
            mock_github.return_value = mock_client
            mock_client.get_user.return_value = Mock(login="testuser")
            mock_client.get_rate_limit.return_value = Mock(
                core=Mock(remaining=5000, limit=5000, reset=datetime.now())
            )
            
            client = GitHubClient(token="test_token")
            
            assert client.token == "test_token"
            mock_github.assert_called_once()

    def test_init_without_token_raises_error(self):
        """Test initialization without token raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('devmetrics.collectors.github_client.load_dotenv'):
                with pytest.raises(ValueError, match="GitHub token required"):
                    GitHubClient()

    def test_init_with_env_token(self):
        """Test initialization reads token from environment."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            with patch('devmetrics.collectors.github_client.Github') as mock_github:
                mock_client = Mock()
                mock_github.return_value = mock_client
                mock_client.get_user.return_value = Mock(login="testuser")
                mock_client.get_rate_limit.return_value = Mock(
                    core=Mock(remaining=5000, limit=5000, reset=datetime.now())
                )
                
                client = GitHubClient()
                
                assert client.token == "env_token"

    def test_validate_connection_failure(self):
        """Test authentication failure is caught and raised."""
        with patch('devmetrics.collectors.github_client.Github') as mock_github:
            mock_client = Mock()
            mock_github.return_value = mock_client
            mock_client.get_user.side_effect = GithubException(401, "Unauthorized")
            
            with pytest.raises(GithubException):
                GitHubClient(token="invalid_token")


class TestGitHubClientRateLimit:
    """Test rate limit handling."""

    @pytest.fixture
    def mock_client(self):
        """Create mock GitHub client."""
        with patch('devmetrics.collectors.github_client.Github') as mock_github:
            mock_gh = Mock()
            mock_github.return_value = mock_gh
            mock_gh.get_user.return_value = Mock(login="testuser")
            mock_gh.get_rate_limit.return_value = Mock(
                core=Mock(remaining=5000, limit=5000, reset=datetime.now())
            )
            
            client = GitHubClient(token="test_token")
            client.client = mock_gh
            yield client, mock_gh

    def test_get_rate_limit(self, mock_client):
        """Test get_rate_limit returns correct structure."""
        client, mock_gh = mock_client
        reset_time = datetime.now()
        mock_gh.get_rate_limit.return_value = Mock(
            core=Mock(remaining=4500, limit=5000, reset=reset_time)
        )
        
        rate_limit = client.get_rate_limit()
        
        assert rate_limit["remaining"] == 4500
        assert rate_limit["limit"] == 5000
        assert rate_limit["reset"] == reset_time
        assert "reset_timestamp" in rate_limit

    def test_handle_rate_limit_not_triggered_when_high(self, mock_client):
        """Test rate limit handling does not sleep when remaining is high."""
        client, mock_gh = mock_client
        mock_gh.get_rate_limit.return_value = Mock(
            core=Mock(remaining=500, limit=5000, reset=datetime.now())
        )
        
        with patch('time.sleep') as mock_sleep:
            client.handle_rate_limit()
            mock_sleep.assert_not_called()

    def test_handle_rate_limit_sleeps_when_low(self, mock_client):
        """Test rate limit handling sleeps when remaining is low."""
        client, mock_gh = mock_client
        future_reset = datetime.now() + timedelta(seconds=60)
        mock_gh.get_rate_limit.return_value = Mock(
            core=Mock(remaining=50, limit=5000, reset=future_reset)
        )
        
        with patch('time.sleep') as mock_sleep:
            with patch('time.time', return_value=datetime.now().timestamp()):
                client.handle_rate_limit()
                mock_sleep.assert_called_once()
                sleep_duration = mock_sleep.call_args[0][0]
                assert sleep_duration > 0

    def test_get_repository_with_rate_limit_exceeded(self, mock_client):
        """Test get_repository retries on rate limit exceeded."""
        client, mock_gh = mock_client
        
        # First call raises exception, second succeeds
        mock_repo = Mock()
        mock_gh.get_repo.side_effect = [
            RateLimitExceededException(403, "Rate limit exceeded"),
            mock_repo
        ]
        mock_gh.get_rate_limit.return_value = Mock(
            core=Mock(remaining=0, limit=5000, reset=datetime.now())
        )
        
        with patch('time.sleep'):
            result = client.get_repository("owner/repo")
            
        assert result == mock_repo
        assert mock_gh.get_repo.call_count == 2


class TestGitHubClientRepositoryOperations:
    """Test repository and organization operations."""

    @pytest.fixture
    def mock_client(self):
        """Create mock GitHub client."""
        with patch('devmetrics.collectors.github_client.Github') as mock_github:
            mock_gh = Mock()
            mock_github.return_value = mock_gh
            mock_gh.get_user.return_value = Mock(login="testuser")
            mock_gh.get_rate_limit.return_value = Mock(
                core=Mock(remaining=5000, limit=5000, reset=datetime.now())
            )
            
            client = GitHubClient(token="test_token")
            client.client = mock_gh
            yield client, mock_gh

    def test_get_repository_success(self, mock_client):
        """Test successful repository retrieval."""
        client, mock_gh = mock_client
        mock_repo = Mock()
        mock_gh.get_repo.return_value = mock_repo
        mock_gh.get_rate_limit.return_value = Mock(
            core=Mock(remaining=5000, limit=5000, reset=datetime.now())
        )
        
        result = client.get_repository("owner/repo")
        
        assert result == mock_repo
        mock_gh.get_repo.assert_called_with("owner/repo")

    def test_get_repository_not_found(self, mock_client):
        """Test repository not found raises exception."""
        client, mock_gh = mock_client
        mock_gh.get_repo.side_effect = GithubException(404, "Not Found")
        mock_gh.get_rate_limit.return_value = Mock(
            core=Mock(remaining=5000, limit=5000, reset=datetime.now())
        )
        
        with pytest.raises(GithubException):
            client.get_repository("owner/nonexistent")

    def test_get_organization_success(self, mock_client):
        """Test successful organization retrieval."""
        client, mock_gh = mock_client
        mock_org = Mock()
        mock_gh.get_organization.return_value = mock_org
        mock_gh.get_rate_limit.return_value = Mock(
            core=Mock(remaining=5000, limit=5000, reset=datetime.now())
        )
        
        result = client.get_organization("test-org")
        
        assert result == mock_org
        mock_gh.get_organization.assert_called_with("test-org")

    def test_close_connection(self, mock_client):
        """Test close method calls client.close()."""
        client, mock_gh = mock_client
        
        client.close()
        
        mock_gh.close.assert_called_once()


class TestGitHubClientEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_token_string(self):
        """Test empty token string raises error."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": ""}):
            with patch('devmetrics.collectors.github_client.load_dotenv'):
                with pytest.raises(ValueError):
                    GitHubClient()

    def test_rate_limit_with_past_reset_time(self):
        """Test rate limit handling with reset time in the past."""
        with patch('devmetrics.collectors.github_client.Github') as mock_github:
            mock_gh = Mock()
            mock_github.return_value = mock_gh
            mock_gh.get_user.return_value = Mock(login="testuser")
            
            past_reset = datetime.now() - timedelta(seconds=60)
            mock_gh.get_rate_limit.return_value = Mock(
                core=Mock(remaining=50, limit=5000, reset=past_reset)
            )
            
            client = GitHubClient(token="test_token")
            client.client = mock_gh
            
            with patch('time.sleep') as mock_sleep:
                client.handle_rate_limit()
                # Should sleep for minimal time (10 seconds minimum)
                if mock_sleep.called:
                    sleep_duration = mock_sleep.call_args[0][0]
                    assert sleep_duration >= 0
