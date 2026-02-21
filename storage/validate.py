"""
Validation script for storage layer and data schemas.
Run this to verify all data files are valid and storage API works.
"""

from storage import JSONStore
from pathlib import Path


def validate_all():
    """Validate all data files and print summary."""
    store = JSONStore("data")
    
    files_to_check = [
        "space/pr_cycle_times.json",
        "space/review_turnaround.json",
        "space/rework_rates.json",
        "space/wip_counts.json",
        "copilot/usage_metrics.json",
        "copilot/acceptance_rates.json",
        "copilot/seat_utilization.json",
        "snapshots/2025-01-22.json",
    ]
    
    print("=" * 60)
    print("Storage Layer Validation")
    print("=" * 60)
    print()
    
    all_valid = True
    
    for filepath in files_to_check:
        is_valid = store.validate_structure(filepath)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        
        if is_valid:
            stats = store.get_stats(filepath)
            count = stats.get('count', 0)
            source = stats.get('source', 'unknown')
            print(f"{status:10} | {filepath:40} | {count:3} records | {source}")
        else:
            print(f"{status:10} | {filepath:40} | ERROR")
            all_valid = False
    
    print()
    print("=" * 60)
    
    if all_valid:
        print("✅ All data files are valid!")
    else:
        print("❌ Some files have validation errors")
        return False
    
    # Test query operations
    print()
    print("Testing Query Operations:")
    print("-" * 60)
    
    # Test date range query
    recent_prs = store.query_by_date_range(
        "space/pr_cycle_times.json",
        start_date="2025-01-20",
        end_date="2025-01-22",
        date_field="merged_at"
    )
    print(f"✅ Date range query: Found {len(recent_prs)} PRs (2025-01-20 to 2025-01-22)")
    
    # Test repo query
    backend_prs = store.query_by_repo("space/pr_cycle_times.json", "org/backend-api")
    print(f"✅ Repo query: Found {len(backend_prs)} PRs for org/backend-api")
    
    # Test snapshot operations
    latest = store.get_latest_snapshot()
    if latest:
        print(f"✅ Latest snapshot: {latest['date']}")
    
    snapshots = store.list_snapshots()
    print(f"✅ Total snapshots: {len(snapshots)}")
    
    print()
    print("=" * 60)
    print("✅ Storage layer is fully operational!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = validate_all()
    exit(0 if success else 1)
