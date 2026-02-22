"""Copilot metrics collector for GitHub Enterprise API.

Collects metrics for:
- Usage (active users, suggestions, acceptances)
- Acceptance rates
- Seat utilization
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class CopilotCollector:
    """Collector for GitHub Copilot metrics from Enterprise API."""

    def __init__(self, token: Optional[str] = None, enterprise: Optional[str] = None, org: Optional[str] = None):
        """Initialize Copilot collector.
        
        Args:
            token: GitHub personal access token (requires manage_billing:copilot or read:enterprise)
            enterprise: GitHub Enterprise slug (for enterprise-level metrics)
            org: GitHub organization name (for org-level metrics)
        """
        load_dotenv()
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.enterprise = enterprise or os.getenv("GITHUB_ENTERPRISE")
        self.org = org or os.getenv("GITHUB_ORG")
        
        if not self.token:
            raise ValueError("GitHub token required for Copilot metrics")
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        logger.info(f"Initialized CopilotCollector (enterprise={self.enterprise}, org={self.org})")

    def collect_usage_metrics(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict:
        """Collect Copilot usage metrics (active users, suggestions, acceptances).
        
        Args:
            since: Start date for data collection (default: 90 days ago)
            until: End date for data collection (default: now)
            
        Returns:
            dict: Usage metrics with schema matching dummy_data_generator
        """
        if since is None:
            since = datetime.now() - timedelta(days=90)
        if until is None:
            until = datetime.now()
        
        logger.info(f"Collecting Copilot usage metrics from {since.date()} to {until.date()}")
        
        # Note: This requires enterprise API access
        # For now, this is a stub that would call the real API
        if not self.enterprise:
            logger.warning("No enterprise slug configured - cannot collect Copilot metrics")
            return self._empty_usage_response()
        
        try:
            # Copilot Metrics API (available until April 2026)
            # GET /enterprises/{enterprise}/copilot/metrics
            url = f"https://api.github.com/enterprises/{self.enterprise}/copilot/metrics"
            
            params = {
                "since": since.date().isoformat(),
                "until": until.date().isoformat(),
                "page": 1,
                "per_page": 100
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Parse API response and format to match dummy data schema
            api_data = response.json()
            daily_usage = self._format_usage_data(api_data)
            
            logger.info(f"Collected {len(daily_usage)} days of usage data")
            
            return {
                "daily_usage": daily_usage,
                "summary": self._calculate_usage_summary(daily_usage),
                "collected_at": datetime.now().isoformat(),
                "source": "github_enterprise_api"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error collecting Copilot usage metrics: {e}")
            return self._empty_usage_response()

    def collect_acceptance_rates(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict:
        """Collect Copilot acceptance rate trends.
        
        Args:
            since: Start date for data collection (default: 90 days ago)
            until: End date for data collection (default: now)
            
        Returns:
            dict: Acceptance rate data with schema matching dummy_data_generator
        """
        if since is None:
            since = datetime.now() - timedelta(days=90)
        if until is None:
            until = datetime.now()
        
        logger.info(f"Collecting Copilot acceptance rates from {since.date()} to {until.date()}")
        
        # This would derive from usage metrics API
        usage_data = self.collect_usage_metrics(since, until)
        
        daily_rates = []
        for day in usage_data.get("daily_usage", []):
            suggestions = day.get("suggestions", 0)
            acceptances = day.get("acceptances", 0)
            acceptance_rate = acceptances / suggestions if suggestions > 0 else 0.0
            
            daily_rates.append({
                "date": day["date"],
                "acceptance_rate": round(acceptance_rate, 3),
                "suggestions": suggestions,
                "acceptances": acceptances
            })
        
        # Calculate trend
        if len(daily_rates) >= 2:
            import numpy as np
            first_half = np.mean([d["acceptance_rate"] for d in daily_rates[:len(daily_rates)//2]])
            second_half = np.mean([d["acceptance_rate"] for d in daily_rates[len(daily_rates)//2:]])
            
            if second_half > first_half + 0.02:
                trend = "improving"
            elif second_half < first_half - 0.02:
                trend = "declining"
            else:
                trend = "stable"
            
            overall_rate = np.mean([d["acceptance_rate"] for d in daily_rates])
        else:
            trend = "unknown"
            overall_rate = 0.0
        
        return {
            "daily_rates": daily_rates,
            "summary": {
                "overall_rate": round(float(overall_rate), 3),
                "trend": trend
            },
            "collected_at": datetime.now().isoformat(),
            "source": "github_enterprise_api"
        }

    def collect_seat_utilization(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict:
        """Collect Copilot seat utilization data.
        
        Args:
            since: Start date for data collection (default: 90 days ago)
            until: End date for data collection (default: now)
            
        Returns:
            dict: Seat utilization data with schema matching dummy_data_generator
        """
        if since is None:
            since = datetime.now() - timedelta(days=90)
        if until is None:
            until = datetime.now()
        
        logger.info(f"Collecting Copilot seat utilization from {since.date()} to {until.date()}")
        
        if not self.org:
            logger.warning("No organization configured - cannot collect seat data")
            return self._empty_seat_response()
        
        try:
            # Org API endpoint for seat data
            # GET /orgs/{org}/copilot/billing/seats
            url = f"https://api.github.com/orgs/{self.org}/copilot/billing/seats"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            seat_data = response.json()
            
            # Format seat utilization data
            total_seats = seat_data.get("total_seats", 0)
            seats = seat_data.get("seats", [])
            
            # Count active seats (those with recent activity)
            active_threshold = datetime.now() - timedelta(days=7)
            active_seats = sum(
                1 for seat in seats 
                if seat.get("last_activity_at") and 
                datetime.fromisoformat(seat["last_activity_at"].replace("Z", "+00:00")) > active_threshold
            )
            
            utilization_rate = active_seats / total_seats if total_seats > 0 else 0.0
            
            daily_utilization = [{
                "date": datetime.now().date().isoformat(),
                "total_seats": total_seats,
                "active_seats": active_seats,
                "utilization_rate": round(utilization_rate, 3)
            }]
            
            logger.info(f"Collected seat data: {active_seats}/{total_seats} active")
            
            return {
                "daily_utilization": daily_utilization,
                "summary": {
                    "current_utilization": round(utilization_rate, 3),
                    "avg_utilization": round(utilization_rate, 3),
                    "total_seats": total_seats
                },
                "collected_at": datetime.now().isoformat(),
                "source": "github_org_api"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error collecting seat utilization: {e}")
            return self._empty_seat_response()

    def _format_usage_data(self, api_data) -> list:
        """Format Copilot Metrics API response to match dashboard schema.

        The /copilot/metrics endpoint returns a list of daily metric objects.
        Each object has top-level ``total_active_users``, ``total_engaged_users``,
        and nested IDE code-completion stats we aggregate into suggestions/acceptances.
        """
        if not api_data or not isinstance(api_data, list):
            return []

        daily_usage = []
        for day in api_data:
            suggestions = 0
            acceptances = 0
            lines_suggested = 0
            lines_accepted = 0

            completions = day.get("copilot_ide_code_completions") or {}
            for editor in completions.get("editors", []):
                for model in editor.get("models", []):
                    for lang in model.get("languages", []):
                        suggestions += lang.get("total_code_suggestions", 0)
                        acceptances += lang.get("total_code_acceptances", 0)
                        lines_suggested += lang.get("total_code_lines_suggested", 0)
                        lines_accepted += lang.get("total_code_lines_accepted", 0)

            daily_usage.append({
                "date": day.get("date", ""),
                "active_users": day.get("total_active_users", 0),
                "engaged_users": day.get("total_engaged_users", 0),
                "suggestions": suggestions,
                "acceptances": acceptances,
                "lines_suggested": lines_suggested,
                "lines_accepted": lines_accepted,
            })

        return daily_usage

    def _calculate_usage_summary(self, daily_usage: list) -> Dict:
        """Calculate summary statistics from daily usage data."""
        if not daily_usage:
            return {
                "total_suggestions": 0,
                "total_acceptances": 0,
                "avg_active_users": 0.0
            }
        
        import numpy as np
        return {
            "total_suggestions": sum(d.get("suggestions", 0) for d in daily_usage),
            "total_acceptances": sum(d.get("acceptances", 0) for d in daily_usage),
            "avg_active_users": round(float(np.mean([d.get("active_users", 0) for d in daily_usage])), 2)
        }

    def _empty_usage_response(self) -> Dict:
        """Return empty usage response structure."""
        return {
            "daily_usage": [],
            "summary": {
                "total_suggestions": 0,
                "total_acceptances": 0,
                "avg_active_users": 0.0
            },
            "collected_at": datetime.now().isoformat(),
            "source": "unavailable"
        }

    def _empty_seat_response(self) -> Dict:
        """Return empty seat response structure."""
        return {
            "daily_utilization": [],
            "summary": {
                "current_utilization": 0.0,
                "avg_utilization": 0.0,
                "total_seats": 0
            },
            "collected_at": datetime.now().isoformat(),
            "source": "unavailable"
        }
