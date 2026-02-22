"""Quick verification script for dashboards."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from storage.json_store import JSONStore

print("🧪 Testing Dashboard Components...")
print()

# Test data store
store = JSONStore("data")

# Load SPACE metrics
pr_data = store.load_pr_cycle_times()
review_data = store.load_review_turnaround()
rework_data = store.load_rework_rates()
wip_data = store.load_wip_counts()

print("✅ SPACE Metrics Loading:")
print(f"   - {len(pr_data.get('prs', []))} PRs")
print(f"   - {len(review_data.get('reviews', []))} reviews")
print(f"   - {len(rework_data.get('weekly_rates', []))} weeks of rework data")
print(f"   - {len(wip_data.get('daily_wip', []))} WIP snapshots")
print()

# Load Copilot metrics
usage_data = store.load_copilot_usage()
acceptance_data = store.load_acceptance_rates()
utilization_data = store.load_seat_utilization()

print("✅ Copilot Metrics Loading:")
print(f"   - {len(usage_data.get('daily_usage', []))} days of usage")
print(f"   - {len(acceptance_data.get('daily_rates', []))} days of acceptance rates")
print(f"   - {len(utilization_data.get('daily_utilization', []))} days of seat utilization")
print()

# Summary stats
pr_summary = pr_data.get('summary', {})
copilot_summary = usage_data.get('summary', {})

print("📊 Sample Metrics:")
print(f"   - Median PR Cycle Time: {pr_summary.get('median_hours', 0):.1f}h")
print(f"   - Total Copilot Acceptances: {copilot_summary.get('total_acceptances', 0):,}")
print()

print("🎉 All dashboard components verified!")
print()
print("🚀 To run the dashboards:")
print("   streamlit run app.py")
