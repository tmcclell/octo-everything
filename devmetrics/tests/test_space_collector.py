"""Tests for SpaceCollector - PR cycle time calculation, review parsing."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import numpy as np

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from devmetrics.collectors.space_collector import SpaceCollector
from devmetrics.collectors.github_client import GitHubClient


class TestSpaceCollectorInit:
    """Test SpaceCollector initialization."""

    def test_init_with_repos(self):
        """Test initialization with repository list."""
        mock_client = Mock(spec=GitHubClient)
        repos = ["owner/repo1", "owner/repo2"]
        
        collector = SpaceCollector(mock_client, repos)
        
        assert collector.client == mock_client
        assert collector.repos == repos

    def test_init_with_empty_repos(self):
        """Test initialization with empty repository list."""
        mock_client = Mock(spec=GitHubClient)
        repos = []
        
        collector = SpaceCollector(mock_client, repos)
        
        assert collector.repos == []


class TestCollectPRCycleTimes:
    """Test PR cycle time collection."""

    @pytest.fixture
    def mock_collector(self):
        """Create mock collector with client."""
        mock_client = Mock(spec=GitHubClient)
        repos = ["owner/repo1"]
        return SpaceCollector(mock_client, repos), mock_client

    def test_collect_pr_cycle_times_success(self, mock_collector):
        """Test successful PR cycle time collection."""
        collector, mock_client = mock_collector
        
        # Mock PRs
        mock_pr1 = Mock()
        mock_pr1.number = 1
        mock_pr1.created_at = datetime.now() - timedelta(days=2)
        mock_pr1.merged_at = datetime.now() - timedelta(days=1)
        mock_pr1.user.login = "dev1"
        
        mock_pr2 = Mock()
        mock_pr2.number = 2
        mock_pr2.created_at = datetime.now() - timedelta(days=3)
        mock_pr2.merged_at = datetime.now() - timedelta(hours=24)
        mock_pr2.user.login = "dev2"
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = [mock_pr1, mock_pr2]
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_pr_cycle_times()
        
        assert "prs" in result
        assert "summary" in result
        assert len(result["prs"]) == 2
        assert result["summary"]["total_prs"] == 2
        assert "median_hours" in result["summary"]
        assert "p95_hours" in result["summary"]

    def test_collect_pr_cycle_times_filters_unmerged(self, mock_collector):
        """Test that unmerged PRs are filtered out."""
        collector, mock_client = mock_collector
        
        mock_pr_merged = Mock()
        mock_pr_merged.number = 1
        mock_pr_merged.created_at = datetime.now() - timedelta(days=2)
        mock_pr_merged.merged_at = datetime.now() - timedelta(days=1)
        mock_pr_merged.user.login = "dev1"
        
        mock_pr_unmerged = Mock()
        mock_pr_unmerged.number = 2
        mock_pr_unmerged.created_at = datetime.now() - timedelta(days=1)
        mock_pr_unmerged.merged_at = None
        mock_pr_unmerged.user.login = "dev2"
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = [mock_pr_merged, mock_pr_unmerged]
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_pr_cycle_times()
        
        assert len(result["prs"]) == 1
        assert result["prs"][0]["pr_number"] == 1

    def test_collect_pr_cycle_times_date_range_filter(self, mock_collector):
        """Test date range filtering works correctly."""
        collector, mock_client = mock_collector
        
        # PR within range
        mock_pr1 = Mock()
        mock_pr1.number = 1
        mock_pr1.created_at = datetime(2024, 1, 15)
        mock_pr1.merged_at = datetime(2024, 1, 16)
        mock_pr1.user.login = "dev1"
        
        # PR outside range
        mock_pr2 = Mock()
        mock_pr2.number = 2
        mock_pr2.created_at = datetime(2023, 12, 1)
        mock_pr2.merged_at = datetime(2023, 12, 2)
        mock_pr2.user.login = "dev2"
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = [mock_pr1, mock_pr2]
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_pr_cycle_times(
            since=datetime(2024, 1, 1),
            until=datetime(2024, 1, 31)
        )
        
        assert len(result["prs"]) == 1
        assert result["prs"][0]["pr_number"] == 1

    def test_collect_pr_cycle_times_empty_results(self, mock_collector):
        """Test handling of empty PR results."""
        collector, mock_client = mock_collector
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = []
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_pr_cycle_times()
        
        assert result["prs"] == []
        assert result["summary"]["total_prs"] == 0
        assert result["summary"]["median_hours"] == 0.0
        assert result["summary"]["p95_hours"] == 0.0

    def test_collect_pr_cycle_times_handles_error(self, mock_collector):
        """Test error handling during collection."""
        collector, mock_client = mock_collector
        mock_client.get_repository.side_effect = Exception("API Error")
        
        result = collector.collect_pr_cycle_times()
        
        # Should return empty results on error
        assert result["prs"] == []
        assert result["summary"]["total_prs"] == 0


class TestCollectReviewTurnaround:
    """Test review turnaround time collection."""

    @pytest.fixture
    def mock_collector(self):
        """Create mock collector."""
        mock_client = Mock(spec=GitHubClient)
        repos = ["owner/repo1"]
        return SpaceCollector(mock_client, repos), mock_client

    def test_collect_review_turnaround_success(self, mock_collector):
        """Test successful review turnaround collection."""
        collector, mock_client = mock_collector
        
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.created_at = datetime.now() - timedelta(hours=48)
        
        mock_review = Mock()
        mock_review.submitted_at = datetime.now() - timedelta(hours=44)
        
        mock_pr.get_reviews.return_value = Mock(totalCount=1)
        mock_pr.get_reviews.return_value.__iter__ = Mock(return_value=iter([mock_review]))
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = [mock_pr]
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_review_turnaround()
        
        assert "reviews" in result
        assert "summary" in result
        assert len(result["reviews"]) == 1
        assert result["reviews"][0]["pr_number"] == 1
        assert "turnaround_hours" in result["reviews"][0]

    def test_collect_review_turnaround_no_reviews(self, mock_collector):
        """Test handling PRs with no reviews."""
        collector, mock_client = mock_collector
        
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.created_at = datetime.now() - timedelta(hours=48)
        mock_pr.get_reviews.return_value = Mock(totalCount=0)
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = [mock_pr]
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_review_turnaround()
        
        assert result["reviews"] == []

    def test_collect_review_turnaround_empty_summary(self, mock_collector):
        """Test summary calculation with no data."""
        collector, mock_client = mock_collector
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = []
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_review_turnaround()
        
        assert result["summary"]["total_reviews"] == 0
        assert result["summary"]["median_hours"] == 0.0


class TestCollectReworkRates:
    """Test rework rate collection."""

    @pytest.fixture
    def mock_collector(self):
        """Create mock collector."""
        mock_client = Mock(spec=GitHubClient)
        repos = ["owner/repo1"]
        return SpaceCollector(mock_client, repos), mock_client

    def test_collect_rework_rates_with_changes_requested(self, mock_collector):
        """Test rework rate calculation with changes requested."""
        collector, mock_client = mock_collector
        
        # PR with changes requested
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.created_at = datetime.now() - timedelta(days=7)
        mock_pr.merged_at = datetime.now() - timedelta(days=5)
        
        mock_review = Mock()
        mock_review.state = "CHANGES_REQUESTED"
        mock_pr.get_reviews.return_value = [mock_review]
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = [mock_pr]
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_rework_rates()
        
        assert "weekly_rates" in result
        assert len(result["weekly_rates"]) > 0
        assert result["weekly_rates"][0]["changes_requested"] == 1
        assert result["weekly_rates"][0]["total_merged"] == 1
        assert result["weekly_rates"][0]["rework_rate"] == 1.0

    def test_collect_rework_rates_without_changes(self, mock_collector):
        """Test rework rate calculation without changes requested."""
        collector, mock_client = mock_collector
        
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.created_at = datetime.now() - timedelta(days=7)
        mock_pr.merged_at = datetime.now() - timedelta(days=5)
        
        mock_review = Mock()
        mock_review.state = "APPROVED"
        mock_pr.get_reviews.return_value = [mock_review]
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = [mock_pr]
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_rework_rates()
        
        assert result["weekly_rates"][0]["changes_requested"] == 0
        assert result["weekly_rates"][0]["rework_rate"] == 0.0

    def test_collect_rework_rates_trend_calculation(self, mock_collector):
        """Test trend calculation logic."""
        collector, mock_client = mock_collector
        
        # Create multiple PRs over time to test trend
        prs = []
        for i in range(20):
            mock_pr = Mock()
            mock_pr.number = i
            mock_pr.created_at = datetime.now() - timedelta(days=30-i)
            mock_pr.merged_at = datetime.now() - timedelta(days=29-i)
            
            # First half has more changes requested
            if i < 10:
                mock_review = Mock()
                mock_review.state = "CHANGES_REQUESTED"
                mock_pr.get_reviews.return_value = [mock_review]
            else:
                mock_review = Mock()
                mock_review.state = "APPROVED"
                mock_pr.get_reviews.return_value = [mock_review]
            
            prs.append(mock_pr)
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = prs
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_rework_rates()
        
        assert "summary" in result
        assert result["summary"]["trend"] in ["improving", "worsening", "stable"]


class TestCollectWIPCounts:
    """Test WIP count collection."""

    @pytest.fixture
    def mock_collector(self):
        """Create mock collector."""
        mock_client = Mock(spec=GitHubClient)
        repos = ["owner/repo1", "owner/repo2"]
        return SpaceCollector(mock_client, repos), mock_client

    def test_collect_wip_counts_success(self, mock_collector):
        """Test successful WIP count collection."""
        collector, mock_client = mock_collector
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = Mock(totalCount=5)
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_wip_counts()
        
        assert "daily_wip" in result
        assert len(result["daily_wip"]) == 2  # Two repos
        assert result["summary"]["max_wip"] == 5

    def test_collect_wip_counts_empty_repos(self, mock_collector):
        """Test WIP counts with no open PRs."""
        collector, mock_client = mock_collector
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = Mock(totalCount=0)
        mock_client.get_repository.return_value = mock_repo
        
        result = collector.collect_wip_counts()
        
        assert result["summary"]["max_wip"] == 0
        assert result["summary"]["avg_wip_per_repo"] == 0.0


class TestSpaceCollectorEdgeCases:
    """Test edge cases and error scenarios."""

    def test_multiple_repos_partial_failure(self):
        """Test handling when some repos fail."""
        mock_client = Mock(spec=GitHubClient)
        repos = ["owner/repo1", "owner/repo2"]
        collector = SpaceCollector(mock_client, repos)
        
        # First repo succeeds, second fails
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.created_at = datetime.now() - timedelta(days=2)
        mock_pr.merged_at = datetime.now() - timedelta(days=1)
        mock_pr.user.login = "dev1"
        
        mock_repo1 = Mock()
        mock_repo1.get_pulls.return_value = [mock_pr]
        
        def get_repo_side_effect(name):
            if name == "owner/repo1":
                return mock_repo1
            else:
                raise Exception("API Error")
        
        mock_client.get_repository.side_effect = get_repo_side_effect
        
        result = collector.collect_pr_cycle_times()
        
        # Should have data from repo1 only
        assert len(result["prs"]) == 1

    def test_date_range_defaults(self):
        """Test default date range is 90 days."""
        mock_client = Mock(spec=GitHubClient)
        repos = ["owner/repo1"]
        collector = SpaceCollector(mock_client, repos)
        
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = []
        mock_client.get_repository.return_value = mock_repo
        
        # Should not raise error with default dates
        result = collector.collect_pr_cycle_times()
        
        assert "collected_at" in result
        assert result["source"] == "github_api"
