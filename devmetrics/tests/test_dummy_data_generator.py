"""Tests for DummyDataGenerator - data validation, determinism with seed."""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from devmetrics.collectors.dummy_data_generator import DummyDataGenerator


class TestDummyDataGeneratorInit:
    """Test DummyDataGenerator initialization."""

    def test_init_with_default_seed(self, tmp_path):
        """Test initialization with default seed."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        
        assert generator.seed == 42
        assert generator.days_history == 90
        assert len(generator.repos) == 5

    def test_init_creates_directories(self, tmp_path):
        """Test initialization creates necessary directories."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator._ensure_directories()
        
        assert (tmp_path / "space").exists()
        assert (tmp_path / "copilot").exists()
        assert (tmp_path / "snapshots").exists()

    def test_init_with_custom_seed(self, tmp_path):
        """Test initialization with custom seed."""
        generator = DummyDataGenerator(seed=123, data_dir=str(tmp_path))
        
        assert generator.seed == 123


class TestDummyDataGeneratorDeterminism:
    """Test deterministic behavior with seeds."""

    def test_same_seed_produces_same_data(self, tmp_path):
        """Test that same seed produces identical data."""
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        
        gen1 = DummyDataGenerator(seed=42, data_dir=str(dir1))
        gen1.generate_pr_cycle_times()
        
        gen2 = DummyDataGenerator(seed=42, data_dir=str(dir2))
        gen2.generate_pr_cycle_times()
        
        with open(dir1 / "space" / "pr_cycle_times.json") as f1:
            data1 = json.load(f1)
        with open(dir2 / "space" / "pr_cycle_times.json") as f2:
            data2 = json.load(f2)
        
        # Compare PR data (excluding timestamps)
        assert len(data1["prs"]) == len(data2["prs"])
        assert data1["prs"][0]["cycle_time_hours"] == data2["prs"][0]["cycle_time_hours"]
        assert data1["summary"]["median_hours"] == data2["summary"]["median_hours"]

    def test_different_seed_produces_different_data(self, tmp_path):
        """Test that different seeds produce different data."""
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        
        gen1 = DummyDataGenerator(seed=42, data_dir=str(dir1))
        gen1.generate_pr_cycle_times()
        
        gen2 = DummyDataGenerator(seed=99, data_dir=str(dir2))
        gen2.generate_pr_cycle_times()
        
        with open(dir1 / "space" / "pr_cycle_times.json") as f1:
            data1 = json.load(f1)
        with open(dir2 / "space" / "pr_cycle_times.json") as f2:
            data2 = json.load(f2)
        
        # Data should be different
        assert data1["prs"][0]["cycle_time_hours"] != data2["prs"][0]["cycle_time_hours"]


class TestGeneratePRCycleTimes:
    """Test PR cycle time generation."""

    def test_generate_pr_cycle_times_creates_file(self, tmp_path):
        """Test that PR cycle times file is created."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_pr_cycle_times()
        
        file_path = tmp_path / "space" / "pr_cycle_times.json"
        assert file_path.exists()

    def test_generate_pr_cycle_times_schema(self, tmp_path):
        """Test PR cycle times data matches expected schema."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_pr_cycle_times()
        
        with open(tmp_path / "space" / "pr_cycle_times.json") as f:
            data = json.load(f)
        
        assert "prs" in data
        assert "summary" in data
        assert "generated_at" in data
        assert "seed" in data
        
        # Check summary fields
        assert "median_hours" in data["summary"]
        assert "p95_hours" in data["summary"]
        assert "total_prs" in data["summary"]
        
        # Check PR fields
        if len(data["prs"]) > 0:
            pr = data["prs"][0]
            assert "repo" in pr
            assert "pr_number" in pr
            assert "created_at" in pr
            assert "merged_at" in pr
            assert "cycle_time_hours" in pr
            assert "author" in pr

    def test_generate_pr_cycle_times_data_validity(self, tmp_path):
        """Test that generated PR data is valid."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_pr_cycle_times()
        
        with open(tmp_path / "space" / "pr_cycle_times.json") as f:
            data = json.load(f)
        
        for pr in data["prs"]:
            # Cycle time should be positive
            assert pr["cycle_time_hours"] > 0
            
            # Cycle time should be between 1 and 168 hours
            assert 1.0 <= pr["cycle_time_hours"] <= 168.0
            
            # Repo should be from configured list
            assert pr["repo"] in generator.repos
            
            # Author should be valid
            assert pr["author"].startswith("dev")
            
            # Timestamps should be valid ISO format
            datetime.fromisoformat(pr["created_at"])
            datetime.fromisoformat(pr["merged_at"])

    def test_generate_pr_cycle_times_count(self, tmp_path):
        """Test that reasonable number of PRs are generated."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_pr_cycle_times()
        
        with open(tmp_path / "space" / "pr_cycle_times.json") as f:
            data = json.load(f)
        
        # Should have PRs (90 days * ~3-8 per weekday)
        assert len(data["prs"]) > 100
        assert data["summary"]["total_prs"] == len(data["prs"])


class TestGenerateReviewTurnaround:
    """Test review turnaround generation."""

    def test_generate_review_turnaround_schema(self, tmp_path):
        """Test review turnaround data matches expected schema."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_review_turnaround()
        
        with open(tmp_path / "space" / "review_turnaround.json") as f:
            data = json.load(f)
        
        assert "reviews" in data
        assert "summary" in data
        
        if len(data["reviews"]) > 0:
            review = data["reviews"][0]
            assert "repo" in review
            assert "pr_number" in review
            assert "created_at" in review
            assert "first_review_at" in review
            assert "turnaround_hours" in review

    def test_generate_review_turnaround_validity(self, tmp_path):
        """Test that review turnaround data is valid."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_review_turnaround()
        
        with open(tmp_path / "space" / "review_turnaround.json") as f:
            data = json.load(f)
        
        for review in data["reviews"]:
            # Turnaround should be positive and reasonable
            assert 0.5 <= review["turnaround_hours"] <= 72.0


class TestGenerateReworkRates:
    """Test rework rate generation."""

    def test_generate_rework_rates_schema(self, tmp_path):
        """Test rework rates data matches expected schema."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_rework_rates()
        
        with open(tmp_path / "space" / "rework_rates.json") as f:
            data = json.load(f)
        
        assert "weekly_rates" in data
        assert "summary" in data
        assert "overall_rate" in data["summary"]
        assert "trend" in data["summary"]
        
        if len(data["weekly_rates"]) > 0:
            week = data["weekly_rates"][0]
            assert "week_start" in week
            assert "total_merged" in week
            assert "changes_requested" in week
            assert "rework_rate" in week

    def test_generate_rework_rates_validity(self, tmp_path):
        """Test that rework rate data is valid."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_rework_rates()
        
        with open(tmp_path / "space" / "rework_rates.json") as f:
            data = json.load(f)
        
        for week in data["weekly_rates"]:
            # Rework rate should be between 0 and 1
            assert 0.0 <= week["rework_rate"] <= 1.0
            
            # Changes requested should not exceed total merged
            assert week["changes_requested"] <= week["total_merged"]


class TestGenerateWIPCounts:
    """Test WIP count generation."""

    def test_generate_wip_counts_schema(self, tmp_path):
        """Test WIP counts data matches expected schema."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_wip_counts()
        
        with open(tmp_path / "space" / "wip_counts.json") as f:
            data = json.load(f)
        
        assert "daily_wip" in data
        assert "summary" in data
        
        if len(data["daily_wip"]) > 0:
            day = data["daily_wip"][0]
            assert "date" in day
            assert "repo" in day
            assert "open_prs" in day


class TestGenerateCopilotMetrics:
    """Test Copilot metrics generation."""

    def test_generate_copilot_usage_schema(self, tmp_path):
        """Test Copilot usage data matches expected schema."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_copilot_usage()
        
        with open(tmp_path / "copilot" / "usage.json") as f:
            data = json.load(f)
        
        assert "daily_usage" in data
        assert "summary" in data
        
        if len(data["daily_usage"]) > 0:
            day = data["daily_usage"][0]
            assert "date" in day
            assert "active_users" in day
            assert "suggestions" in day
            assert "acceptances" in day

    def test_generate_acceptance_rates_schema(self, tmp_path):
        """Test acceptance rates data matches expected schema."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_acceptance_rates()
        
        with open(tmp_path / "copilot" / "acceptance_rates.json") as f:
            data = json.load(f)
        
        assert "daily_rates" in data
        assert "summary" in data

    def test_generate_seat_utilization_schema(self, tmp_path):
        """Test seat utilization data matches expected schema."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_seat_utilization()
        
        with open(tmp_path / "copilot" / "seat_utilization.json") as f:
            data = json.load(f)
        
        assert "daily_utilization" in data
        assert "summary" in data


class TestGenerateAll:
    """Test complete data generation."""

    def test_generate_all_creates_all_files(self, tmp_path):
        """Test that generate_all creates all expected files."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.generate_all()
        
        # Check SPACE files
        assert (tmp_path / "space" / "pr_cycle_times.json").exists()
        assert (tmp_path / "space" / "review_turnaround.json").exists()
        assert (tmp_path / "space" / "rework_rates.json").exists()
        assert (tmp_path / "space" / "wip_counts.json").exists()
        
        # Check Copilot files
        assert (tmp_path / "copilot" / "usage.json").exists()
        assert (tmp_path / "copilot" / "acceptance_rates.json").exists()
        assert (tmp_path / "copilot" / "seat_utilization.json").exists()


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_repos_list(self, tmp_path):
        """Test handling empty repos list."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.repos = []
        
        # Should not crash, but may produce empty/minimal data
        generator.generate_pr_cycle_times()
        
        with open(tmp_path / "space" / "pr_cycle_times.json") as f:
            data = json.load(f)
        
        assert "prs" in data

    def test_zero_days_history(self, tmp_path):
        """Test handling zero days history."""
        generator = DummyDataGenerator(seed=42, data_dir=str(tmp_path))
        generator.days_history = 0
        
        generator.generate_pr_cycle_times()
        
        with open(tmp_path / "space" / "pr_cycle_times.json") as f:
            data = json.load(f)
        
        # Should have no PRs
        assert len(data["prs"]) == 0
