"""Tests for CopilotCollector - usage metric parsing, seat analysis."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from devmetrics.collectors.copilot_collector import CopilotCollector


class TestCopilotCollectorInit:
    """Test CopilotCollector initialization."""

    def test_init_with_token(self):
        """Test initialization with explicit token."""
        collector = CopilotCollector(token="test_token", org="test-org")
        
        assert collector.token == "test_token"
        assert collector.org == "test-org"
        assert "Authorization" in collector.headers

    def test_init_without_token_raises_error(self):
        """Test initialization without token raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('devmetrics.collectors.copilot_collector.load_dotenv'):
                with pytest.raises(ValueError, match="GitHub token required"):
                    CopilotCollector()

    def test_init_with_env_vars(self):
        """Test initialization reads from environment."""
        with patch.dict(os.environ, {
            "GITHUB_TOKEN": "env_token",
            "GITHUB_ORG": "env_org",
            "GITHUB_ENTERPRISE": "env_enterprise"
        }):
            collector = CopilotCollector()
            
            assert collector.token == "env_token"
            assert collector.org == "env_org"
            assert collector.enterprise == "env_enterprise"

    def test_init_with_enterprise(self):
        """Test initialization with enterprise slug."""
        collector = CopilotCollector(token="test", enterprise="my-enterprise")
        
        assert collector.enterprise == "my-enterprise"


class TestCollectUsageMetrics:
    """Test Copilot usage metrics collection."""

    @pytest.fixture
    def mock_collector(self):
        """Create mock collector."""
        return CopilotCollector(token="test_token", enterprise="test-ent")

    def test_collect_usage_metrics_no_enterprise(self, mock_collector):
        """Test usage collection without enterprise returns empty."""
        mock_collector.enterprise = None
        
        result = mock_collector.collect_usage_metrics()
        
        assert result["daily_usage"] == []
        assert result["source"] == "unavailable"
        assert result["summary"]["total_suggestions"] == 0

    @patch('devmetrics.collectors.copilot_collector.requests.get')
    def test_collect_usage_metrics_success(self, mock_get, mock_collector):
        """Test successful usage metrics collection."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "date": "2024-01-15",
                    "total_suggestions": 1000,
                    "total_acceptances": 600,
                    "active_users": 25
                }
            ]
        }
        mock_get.return_value = mock_response
        
        with patch.object(mock_collector, '_format_usage_data', return_value=[]):
            result = mock_collector.collect_usage_metrics()
        
        assert "daily_usage" in result
        assert result["source"] == "github_enterprise_api"

    @patch('devmetrics.collectors.copilot_collector.requests.get')
    def test_collect_usage_metrics_api_error(self, mock_get, mock_collector):
        """Test handling API errors during usage collection."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        result = mock_collector.collect_usage_metrics()
        
        assert result["daily_usage"] == []
        assert result["source"] == "unavailable"

    def test_collect_usage_metrics_date_range(self, mock_collector):
        """Test usage collection respects date range."""
        since = datetime(2024, 1, 1)
        until = datetime(2024, 1, 31)
        
        with patch('devmetrics.collectors.copilot_collector.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": []}
            mock_get.return_value = mock_response
            
            mock_collector.collect_usage_metrics(since=since, until=until)
            
            # Verify date parameters were passed
            call_args = mock_get.call_args
            assert call_args[1]["params"]["since"] == "2024-01-01"
            assert call_args[1]["params"]["until"] == "2024-01-31"


class TestCollectAcceptanceRates:
    """Test Copilot acceptance rate collection."""

    @pytest.fixture
    def mock_collector(self):
        """Create mock collector."""
        return CopilotCollector(token="test_token", enterprise="test-ent")

    def test_collect_acceptance_rates_success(self, mock_collector):
        """Test successful acceptance rate calculation."""
        mock_usage = {
            "daily_usage": [
                {"date": "2024-01-15", "suggestions": 1000, "acceptances": 600},
                {"date": "2024-01-16", "suggestions": 1200, "acceptances": 720}
            ]
        }
        
        with patch.object(mock_collector, 'collect_usage_metrics', return_value=mock_usage):
            result = mock_collector.collect_acceptance_rates()
        
        assert "daily_rates" in result
        assert len(result["daily_rates"]) == 2
        assert result["daily_rates"][0]["acceptance_rate"] == 0.6
        assert result["daily_rates"][1]["acceptance_rate"] == 0.6

    def test_collect_acceptance_rates_zero_suggestions(self, mock_collector):
        """Test handling zero suggestions."""
        mock_usage = {
            "daily_usage": [
                {"date": "2024-01-15", "suggestions": 0, "acceptances": 0}
            ]
        }
        
        with patch.object(mock_collector, 'collect_usage_metrics', return_value=mock_usage):
            result = mock_collector.collect_acceptance_rates()
        
        assert result["daily_rates"][0]["acceptance_rate"] == 0.0

    def test_collect_acceptance_rates_trend_improving(self, mock_collector):
        """Test trend calculation for improving acceptance rates."""
        # Create data with improving trend
        daily_usage = []
        for i in range(20):
            acceptance_rate = 0.5 + (i * 0.02)  # Improving over time
            daily_usage.append({
                "date": f"2024-01-{i+1:02d}",
                "suggestions": 1000,
                "acceptances": int(1000 * acceptance_rate)
            })
        
        mock_usage = {"daily_usage": daily_usage}
        
        with patch.object(mock_collector, 'collect_usage_metrics', return_value=mock_usage):
            result = mock_collector.collect_acceptance_rates()
        
        assert result["summary"]["trend"] == "improving"

    def test_collect_acceptance_rates_trend_declining(self, mock_collector):
        """Test trend calculation for declining acceptance rates."""
        daily_usage = []
        for i in range(20):
            acceptance_rate = 0.8 - (i * 0.02)  # Declining over time
            daily_usage.append({
                "date": f"2024-01-{i+1:02d}",
                "suggestions": 1000,
                "acceptances": int(1000 * acceptance_rate)
            })
        
        mock_usage = {"daily_usage": daily_usage}
        
        with patch.object(mock_collector, 'collect_usage_metrics', return_value=mock_usage):
            result = mock_collector.collect_acceptance_rates()
        
        assert result["summary"]["trend"] == "declining"

    def test_collect_acceptance_rates_trend_stable(self, mock_collector):
        """Test trend calculation for stable acceptance rates."""
        daily_usage = []
        for i in range(20):
            daily_usage.append({
                "date": f"2024-01-{i+1:02d}",
                "suggestions": 1000,
                "acceptances": 600  # Stable rate
            })
        
        mock_usage = {"daily_usage": daily_usage}
        
        with patch.object(mock_collector, 'collect_usage_metrics', return_value=mock_usage):
            result = mock_collector.collect_acceptance_rates()
        
        assert result["summary"]["trend"] == "stable"


class TestCollectSeatUtilization:
    """Test Copilot seat utilization collection."""

    @pytest.fixture
    def mock_collector(self):
        """Create mock collector."""
        return CopilotCollector(token="test_token", org="test-org")

    def test_collect_seat_utilization_no_org(self, mock_collector):
        """Test seat collection without org returns empty."""
        mock_collector.org = None
        
        result = mock_collector.collect_seat_utilization()
        
        assert result["daily_utilization"] == []
        assert result["source"] == "unavailable"

    @patch('devmetrics.collectors.copilot_collector.requests.get')
    def test_collect_seat_utilization_success(self, mock_get, mock_collector):
        """Test successful seat utilization collection."""
        now = datetime.now()
        active_time = (now - timedelta(days=3)).isoformat()
        inactive_time = (now - timedelta(days=10)).isoformat()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_seats": 100,
            "seats": [
                {"login": "user1", "last_activity_at": active_time},
                {"login": "user2", "last_activity_at": active_time},
                {"login": "user3", "last_activity_at": inactive_time}
            ]
        }
        mock_get.return_value = mock_response
        
        result = mock_collector.collect_seat_utilization()
        
        assert "daily_utilization" in result
        assert result["summary"]["total_seats"] == 100
        # 2 out of 3 users active in last 7 days
        assert result["summary"]["current_utilization"] > 0

    @patch('devmetrics.collectors.copilot_collector.requests.get')
    def test_collect_seat_utilization_api_error(self, mock_get, mock_collector):
        """Test handling API errors during seat collection."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        result = mock_collector.collect_seat_utilization()
        
        assert result["daily_utilization"] == []
        assert result["source"] == "unavailable"

    @patch('devmetrics.collectors.copilot_collector.requests.get')
    def test_collect_seat_utilization_zero_seats(self, mock_get, mock_collector):
        """Test handling zero seats."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_seats": 0,
            "seats": []
        }
        mock_get.return_value = mock_response
        
        result = mock_collector.collect_seat_utilization()
        
        assert result["summary"]["current_utilization"] == 0.0

    @patch('devmetrics.collectors.copilot_collector.requests.get')
    def test_collect_seat_utilization_all_inactive(self, mock_get, mock_collector):
        """Test handling all inactive seats."""
        now = datetime.now()
        old_time = (now - timedelta(days=30)).isoformat()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_seats": 10,
            "seats": [
                {"login": f"user{i}", "last_activity_at": old_time}
                for i in range(10)
            ]
        }
        mock_get.return_value = mock_response
        
        result = mock_collector.collect_seat_utilization()
        
        assert result["summary"]["current_utilization"] == 0.0


class TestCopilotCollectorHelpers:
    """Test helper methods."""

    def test_format_usage_data_empty(self):
        """Test formatting empty usage data."""
        collector = CopilotCollector(token="test", org="test")
        
        result = collector._format_usage_data({})
        
        assert result == []

    def test_calculate_usage_summary_empty(self):
        """Test summary calculation with empty data."""
        collector = CopilotCollector(token="test", org="test")
        
        result = collector._calculate_usage_summary([])
        
        assert result["total_suggestions"] == 0
        assert result["total_acceptances"] == 0
        assert result["avg_active_users"] == 0.0

    def test_calculate_usage_summary_with_data(self):
        """Test summary calculation with data."""
        collector = CopilotCollector(token="test", org="test")
        
        daily_usage = [
            {"suggestions": 1000, "acceptances": 600, "active_users": 25},
            {"suggestions": 1200, "acceptances": 720, "active_users": 30}
        ]
        
        result = collector._calculate_usage_summary(daily_usage)
        
        assert result["total_suggestions"] == 2200
        assert result["total_acceptances"] == 1320
        assert result["avg_active_users"] == 27.5

    def test_empty_usage_response(self):
        """Test empty usage response structure."""
        collector = CopilotCollector(token="test", org="test")
        
        result = collector._empty_usage_response()
        
        assert "daily_usage" in result
        assert "summary" in result
        assert result["source"] == "unavailable"

    def test_empty_seat_response(self):
        """Test empty seat response structure."""
        collector = CopilotCollector(token="test", org="test")
        
        result = collector._empty_seat_response()
        
        assert "daily_utilization" in result
        assert "summary" in result
        assert result["source"] == "unavailable"


class TestCopilotCollectorEdgeCases:
    """Test edge cases and error scenarios."""

    def test_missing_fields_in_usage_data(self):
        """Test handling missing fields in usage data."""
        collector = CopilotCollector(token="test", enterprise="test")
        
        mock_usage = {
            "daily_usage": [
                {"date": "2024-01-15"}  # Missing suggestions/acceptances
            ]
        }
        
        with patch.object(collector, 'collect_usage_metrics', return_value=mock_usage):
            result = collector.collect_acceptance_rates()
        
        # Should handle missing fields gracefully
        assert len(result["daily_rates"]) == 1

    @patch('devmetrics.collectors.copilot_collector.requests.get')
    def test_seats_without_last_activity(self, mock_get):
        """Test handling seats without last_activity_at field."""
        collector = CopilotCollector(token="test", org="test")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_seats": 2,
            "seats": [
                {"login": "user1"},  # Missing last_activity_at
                {"login": "user2", "last_activity_at": None}
            ]
        }
        mock_get.return_value = mock_response
        
        result = collector.collect_seat_utilization()
        
        # Should handle missing/null last_activity gracefully
        assert result["summary"]["current_utilization"] == 0.0

    def test_date_range_defaults(self):
        """Test default date range is 90 days."""
        collector = CopilotCollector(token="test", enterprise="test")
        collector.enterprise = None  # Force empty response
        
        result = collector.collect_usage_metrics()
        
        assert "collected_at" in result
