"""SPACE Dashboard - Engineering velocity metrics."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from storage.json_store import JSONStore
from data_source_banner import show_data_source_banner

st.set_page_config(
    page_title="SPACE Metrics",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SPACE Dashboard")
st.markdown("### Engineering Velocity & Efficiency Metrics")

# Initialize data store
@st.cache_resource
def get_store():
    return JSONStore(data_dir="data")

store = get_store()

# Load all SPACE data
@st.cache_data
def load_space_data():
    return {
        'pr_cycle_times': store.load_pr_cycle_times(),
        'review_turnaround': store.load_review_turnaround(),
        'rework_rates': store.load_rework_rates(),
        'wip_counts': store.load_wip_counts()
    }

data = load_space_data()

show_data_source_banner(data)

# Display data refresh timestamp
if data['pr_cycle_times'].get('generated_at'):
    timestamp = datetime.fromisoformat(data['pr_cycle_times']['generated_at'])
    st.caption(f"📅 Data refreshed: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

st.divider()

# Filters
st.sidebar.header("Filters")

# Date range filter
if data['pr_cycle_times'].get('prs'):
    all_dates = [datetime.fromisoformat(pr['created_at']).date() 
                 for pr in data['pr_cycle_times']['prs']]
    min_date = min(all_dates)
    max_date = max(all_dates)
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0]
else:
    start_date = end_date = datetime.now().date()

# Repo filter
if data['pr_cycle_times'].get('prs'):
    all_repos = sorted(set(pr['repo'] for pr in data['pr_cycle_times']['prs']))
    selected_repos = st.sidebar.multiselect(
        "Repositories",
        options=all_repos,
        default=all_repos
    )
else:
    selected_repos = []

# KPI Summary Cards
st.header("📊 Key Performance Indicators")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    median_cycle = data['pr_cycle_times'].get('summary', {}).get('median_hours', 0)
    st.metric(
        label="Median PR Cycle Time",
        value=f"{median_cycle:.1f}h",
        delta=None,
        help="Median time from PR creation to merge"
    )

with kpi_col2:
    median_review = data['review_turnaround'].get('summary', {}).get('median_hours', 0)
    st.metric(
        label="Median Review Time",
        value=f"{median_review:.1f}h",
        delta=None,
        help="Median time to first review"
    )

with kpi_col3:
    rework_rate = data['rework_rates'].get('summary', {}).get('overall_rate', 0)
    trend = data['rework_rates'].get('summary', {}).get('trend', 'stable')
    delta_color = "inverse" if trend == "improving" else "normal"
    st.metric(
        label="Rework Rate",
        value=f"{rework_rate*100:.1f}%",
        delta=trend.capitalize(),
        delta_color=delta_color,
        help="Percentage of PRs requiring changes"
    )

with kpi_col4:
    avg_wip = data['wip_counts'].get('summary', {}).get('avg_wip_per_repo', 0)
    st.metric(
        label="Avg WIP per Repo",
        value=f"{avg_wip:.1f}",
        delta=None,
        help="Average open PRs per repository"
    )

st.divider()

# PR Cycle Time Trends
st.header("⏱️ PR Cycle Time Trends")

if data['pr_cycle_times'].get('prs'):
    prs = data['pr_cycle_times']['prs']
    
    # Filter by date and repo
    filtered_prs = [
        pr for pr in prs
        if pr['repo'] in selected_repos
        and start_date <= datetime.fromisoformat(pr['created_at']).date() <= end_date
    ]
    
    if filtered_prs:
        # Convert to DataFrame
        df_prs = pd.DataFrame(filtered_prs)
        df_prs['created_date'] = pd.to_datetime(df_prs['created_at']).dt.date
        
        # Daily aggregation
        daily_cycle = df_prs.groupby('created_date').agg({
            'cycle_time_hours': ['mean', 'median', 'count']
        }).reset_index()
        daily_cycle.columns = ['date', 'mean', 'median', 'count']
        
        # Line chart
        fig_cycle = go.Figure()
        
        fig_cycle.add_trace(go.Scatter(
            x=daily_cycle['date'],
            y=daily_cycle['median'],
            mode='lines+markers',
            name='Median',
            line=dict(color='#1f77b4', width=3),
            hovertemplate='<b>%{x}</b><br>Median: %{y:.1f}h<extra></extra>'
        ))
        
        fig_cycle.add_trace(go.Scatter(
            x=daily_cycle['date'],
            y=daily_cycle['mean'],
            mode='lines',
            name='Mean',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            hovertemplate='<b>%{x}</b><br>Mean: %{y:.1f}h<extra></extra>'
        ))
        
        fig_cycle.update_layout(
            title="PR Cycle Time Over Time",
            xaxis_title="Date",
            yaxis_title="Hours",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_cycle, use_container_width=True)
        
        # Summary stats
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📈 Total PRs: **{len(filtered_prs)}**")
        with col2:
            p95 = df_prs['cycle_time_hours'].quantile(0.95)
            st.info(f"📊 P95 Cycle Time: **{p95:.1f}h**")
    else:
        st.warning("No data available for selected filters.")
else:
    st.error("No PR cycle time data found.")

st.divider()

# Review Turnaround Distribution
st.header("📝 Review Turnaround Time")

if data['review_turnaround'].get('reviews'):
    reviews = data['review_turnaround']['reviews']
    
    # Filter by date and repo
    filtered_reviews = [
        r for r in reviews
        if r['repo'] in selected_repos
        and start_date <= datetime.fromisoformat(r['created_at']).date() <= end_date
    ]
    
    if filtered_reviews:
        df_reviews = pd.DataFrame(filtered_reviews)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Box plot by repo
            fig_review_box = px.box(
                df_reviews,
                x='repo',
                y='turnaround_hours',
                title="Review Turnaround Distribution by Repository",
                labels={'turnaround_hours': 'Hours', 'repo': 'Repository'},
                color='repo'
            )
            fig_review_box.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_review_box, use_container_width=True)
        
        with col2:
            st.markdown("#### Summary Stats")
            st.metric("Median", f"{df_reviews['turnaround_hours'].median():.1f}h")
            st.metric("Mean", f"{df_reviews['turnaround_hours'].mean():.1f}h")
            st.metric("P95", f"{df_reviews['turnaround_hours'].quantile(0.95):.1f}h")
            st.metric("Total Reviews", len(filtered_reviews))
    else:
        st.warning("No data available for selected filters.")
else:
    st.error("No review turnaround data found.")

st.divider()

# Rework Rate Trends
st.header("🔄 Rework Rate Trends")

if data['rework_rates'].get('weekly_rates'):
    weekly_rates = data['rework_rates']['weekly_rates']
    
    df_rework = pd.DataFrame(weekly_rates)
    df_rework['week_start'] = pd.to_datetime(df_rework['week_start'])
    
    # Bar chart
    fig_rework = go.Figure()
    
    fig_rework.add_trace(go.Bar(
        x=df_rework['week_start'],
        y=df_rework['rework_rate'] * 100,
        name='Rework Rate',
        marker_color='#d62728',
        hovertemplate='<b>Week of %{x}</b><br>Rework Rate: %{y:.1f}%<br>Changes Requested: %{customdata[0]}<br>Total Merged: %{customdata[1]}<extra></extra>',
        customdata=df_rework[['changes_requested', 'total_merged']]
    ))
    
    # Add trend line
    fig_rework.add_trace(go.Scatter(
        x=df_rework['week_start'],
        y=df_rework['rework_rate'].rolling(window=3).mean() * 100,
        mode='lines',
        name='3-week Moving Avg',
        line=dict(color='#2ca02c', width=3),
        hovertemplate='<b>%{x}</b><br>Avg: %{y:.1f}%<extra></extra>'
    ))
    
    fig_rework.update_layout(
        title="Weekly Rework Rate with Moving Average",
        xaxis_title="Week",
        yaxis_title="Rework Rate (%)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_rework, use_container_width=True)
    
    trend = data['rework_rates']['summary']['trend']
    if trend == "improving":
        st.success(f"✅ Trend: **{trend.upper()}** - Rework rate is decreasing over time.")
    elif trend == "worsening":
        st.error(f"⚠️ Trend: **{trend.upper()}** - Rework rate is increasing over time.")
    else:
        st.info(f"➡️ Trend: **{trend.upper()}** - Rework rate is relatively stable.")
else:
    st.error("No rework rate data found.")

st.divider()

# WIP Counts
st.header("📦 Work in Progress by Repository")

if data['wip_counts'].get('daily_wip'):
    daily_wip = data['wip_counts']['daily_wip']
    
    df_wip = pd.DataFrame(daily_wip)
    df_wip['date'] = pd.to_datetime(df_wip['date'])
    
    # Filter by date and repo
    df_wip_filtered = df_wip[
        (df_wip['date'].dt.date >= start_date) &
        (df_wip['date'].dt.date <= end_date) &
        (df_wip['repo'].isin(selected_repos))
    ]
    
    if not df_wip_filtered.empty:
        # Stacked area chart
        fig_wip = px.area(
            df_wip_filtered,
            x='date',
            y='open_prs',
            color='repo',
            title="Daily Open PRs by Repository",
            labels={'open_prs': 'Open PRs', 'date': 'Date'}
        )
        
        fig_wip.update_layout(
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_wip, use_container_width=True)
        
        # Current WIP summary
        latest_date = df_wip_filtered['date'].max()
        latest_wip = df_wip_filtered[df_wip_filtered['date'] == latest_date]
        
        st.markdown("#### Current Open PRs by Repository")
        wip_cols = st.columns(len(selected_repos))
        for idx, repo in enumerate(selected_repos):
            repo_wip = latest_wip[latest_wip['repo'] == repo]['open_prs'].values
            if len(repo_wip) > 0:
                with wip_cols[idx]:
                    st.metric(repo, repo_wip[0])
    else:
        st.warning("No data available for selected filters.")
else:
    st.error("No WIP count data found.")

st.divider()

# Footer
st.markdown("---")
st.caption("🚀 SPACE Dashboard | DevMetrics v1.0")
