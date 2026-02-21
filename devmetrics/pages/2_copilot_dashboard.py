"""Copilot Dashboard - AI productivity and ROI metrics."""

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

st.set_page_config(
    page_title="Copilot Metrics",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Copilot Dashboard")
st.markdown("### AI Productivity & ROI Analytics")

# Initialize data store
@st.cache_resource
def get_store():
    return JSONStore(data_dir="devmetrics/data")

store = get_store()

# Load all Copilot data
@st.cache_data
def load_copilot_data():
    return {
        'usage': store.load_copilot_usage(),
        'acceptance_rates': store.load_acceptance_rates(),
        'seat_utilization': store.load_seat_utilization()
    }

data = load_copilot_data()

# Display data refresh timestamp
if data['usage'].get('generated_at'):
    timestamp = datetime.fromisoformat(data['usage']['generated_at'])
    st.caption(f"📅 Data refreshed: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

st.divider()

# Filters
st.sidebar.header("Filters")

# Date range filter
if data['usage'].get('daily_usage'):
    all_dates = [datetime.fromisoformat(d['date']).date() 
                 for d in data['usage']['daily_usage']]
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

# ROI calculation parameters
st.sidebar.header("ROI Parameters")
hourly_rate = st.sidebar.number_input(
    "Developer Hourly Rate ($)",
    min_value=50,
    max_value=300,
    value=100,
    step=10,
    help="Average fully-loaded hourly cost per developer"
)

seat_cost = st.sidebar.number_input(
    "Copilot Seat Cost ($/month)",
    min_value=10,
    max_value=50,
    value=19,
    step=1,
    help="Monthly cost per Copilot seat"
)

# KPI Summary Cards
st.header("📊 Key Performance Indicators")

# Calculate current metrics from latest data
if data['usage'].get('daily_usage'):
    latest_usage = data['usage']['daily_usage'][-1]
    current_active = latest_usage['active_users']
else:
    current_active = 0

if data['acceptance_rates'].get('summary'):
    overall_acceptance = data['acceptance_rates']['summary']['overall_rate']
else:
    overall_acceptance = 0

if data['seat_utilization'].get('summary'):
    current_utilization = data['seat_utilization']['summary']['current_utilization']
    total_seats = data['seat_utilization']['summary']['total_seats']
else:
    current_utilization = 0
    total_seats = 0

# Calculate time saved (rough estimate: 1 accepted suggestion = 2 minutes saved)
if data['usage'].get('summary'):
    total_acceptances = data['usage']['summary']['total_acceptances']
    time_saved_hours = (total_acceptances * 2) / 60  # 2 min per acceptance
    cost_saved = time_saved_hours * hourly_rate
    
    # Calculate seat cost
    days_history = len(data['usage']['daily_usage']) if data['usage'].get('daily_usage') else 90
    monthly_seat_cost = total_seats * seat_cost
    total_seat_cost = (monthly_seat_cost / 30) * days_history
    
    roi_ratio = cost_saved / total_seat_cost if total_seat_cost > 0 else 0
else:
    time_saved_hours = 0
    cost_saved = 0
    total_seat_cost = 0
    roi_ratio = 0

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.metric(
        label="Active Users (Current)",
        value=current_active,
        delta=f"{(current_active/total_seats*100):.0f}% of seats" if total_seats > 0 else None,
        help="Developers actively using Copilot"
    )

with kpi_col2:
    trend = data['acceptance_rates'].get('summary', {}).get('trend', 'stable')
    delta_color = "normal" if trend == "improving" else "inverse" if trend == "declining" else "off"
    st.metric(
        label="Acceptance Rate",
        value=f"{overall_acceptance*100:.1f}%",
        delta=trend.capitalize(),
        delta_color=delta_color,
        help="Percentage of suggestions accepted"
    )

with kpi_col3:
    st.metric(
        label="Seat Utilization",
        value=f"{current_utilization*100:.0f}%",
        delta=f"{int(current_active)}/{total_seats} seats",
        help="Percentage of seats actively used"
    )

with kpi_col4:
    st.metric(
        label="ROI Ratio",
        value=f"{roi_ratio:.1f}x",
        delta=f"${cost_saved:,.0f} saved",
        delta_color="normal",
        help="Return on investment (value saved / seat cost)"
    )

st.divider()

# Active Users Trends
st.header("👥 Active Users Over Time")

if data['usage'].get('daily_usage'):
    usage_data = data['usage']['daily_usage']
    
    # Filter by date
    filtered_usage = [
        u for u in usage_data
        if start_date <= datetime.fromisoformat(u['date']).date() <= end_date
    ]
    
    if filtered_usage:
        df_usage = pd.DataFrame(filtered_usage)
        df_usage['date'] = pd.to_datetime(df_usage['date'])
        
        fig_users = go.Figure()
        
        fig_users.add_trace(go.Scatter(
            x=df_usage['date'],
            y=df_usage['active_users'],
            mode='lines+markers',
            name='Active Users',
            line=dict(color='#1f77b4', width=3),
            fill='tonexty',
            hovertemplate='<b>%{x}</b><br>Active: %{y}<extra></extra>'
        ))
        
        fig_users.add_trace(go.Scatter(
            x=df_usage['date'],
            y=df_usage['engaged_users'],
            mode='lines',
            name='Engaged Users',
            line=dict(color='#2ca02c', width=2, dash='dash'),
            hovertemplate='<b>%{x}</b><br>Engaged: %{y}<extra></extra>'
        ))
        
        fig_users.update_layout(
            title="Daily Active and Engaged Users",
            xaxis_title="Date",
            yaxis_title="Users",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_users, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_active = df_usage['active_users'].mean()
            st.info(f"📊 Avg Active Users: **{avg_active:.1f}**")
        with col2:
            avg_engaged = df_usage['engaged_users'].mean()
            st.info(f"💡 Avg Engaged Users: **{avg_engaged:.1f}**")
        with col3:
            engagement_rate = (avg_engaged / avg_active * 100) if avg_active > 0 else 0
            st.info(f"🎯 Engagement Rate: **{engagement_rate:.0f}%**")
    else:
        st.warning("No data available for selected date range.")
else:
    st.error("No usage data found.")

st.divider()

# Acceptance Rate Trends
st.header("✅ Acceptance Rate Trends")

if data['acceptance_rates'].get('daily_rates'):
    acceptance_data = data['acceptance_rates']['daily_rates']
    
    # Filter by date
    filtered_acceptance = [
        a for a in acceptance_data
        if start_date <= datetime.fromisoformat(a['date']).date() <= end_date
    ]
    
    if filtered_acceptance:
        df_acceptance = pd.DataFrame(filtered_acceptance)
        df_acceptance['date'] = pd.to_datetime(df_acceptance['date'])
        
        fig_acceptance = go.Figure()
        
        # Daily acceptance rate
        fig_acceptance.add_trace(go.Scatter(
            x=df_acceptance['date'],
            y=df_acceptance['acceptance_rate'] * 100,
            mode='markers',
            name='Daily Rate',
            marker=dict(color='#1f77b4', size=6, opacity=0.5),
            hovertemplate='<b>%{x}</b><br>Rate: %{y:.1f}%<extra></extra>'
        ))
        
        # 7-day moving average
        df_acceptance['ma7'] = df_acceptance['acceptance_rate'].rolling(window=7).mean() * 100
        fig_acceptance.add_trace(go.Scatter(
            x=df_acceptance['date'],
            y=df_acceptance['ma7'],
            mode='lines',
            name='7-day Moving Avg',
            line=dict(color='#ff7f0e', width=3),
            hovertemplate='<b>%{x}</b><br>7-day Avg: %{y:.1f}%<extra></extra>'
        ))
        
        fig_acceptance.update_layout(
            title="Acceptance Rate with 7-day Moving Average",
            xaxis_title="Date",
            yaxis_title="Acceptance Rate (%)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_acceptance, use_container_width=True)
        
        trend = data['acceptance_rates']['summary']['trend']
        if trend == "improving":
            st.success(f"✅ Trend: **{trend.upper()}** - Acceptance rate is increasing over time.")
        elif trend == "declining":
            st.warning(f"⚠️ Trend: **{trend.upper()}** - Acceptance rate is decreasing over time.")
        else:
            st.info(f"➡️ Trend: **{trend.upper()}** - Acceptance rate is relatively stable.")
    else:
        st.warning("No data available for selected date range.")
else:
    st.error("No acceptance rate data found.")

st.divider()

# Seat Utilization
st.header("💺 Seat Utilization")

if data['seat_utilization'].get('daily_utilization'):
    utilization_data = data['seat_utilization']['daily_utilization']
    
    # Filter by date
    filtered_util = [
        u for u in utilization_data
        if start_date <= datetime.fromisoformat(u['date']).date() <= end_date
    ]
    
    if filtered_util:
        df_util = pd.DataFrame(filtered_util)
        df_util['date'] = pd.to_datetime(df_util['date'])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Line chart
            fig_util = go.Figure()
            
            fig_util.add_trace(go.Scatter(
                x=df_util['date'],
                y=df_util['utilization_rate'] * 100,
                mode='lines+markers',
                name='Utilization Rate',
                line=dict(color='#2ca02c', width=3),
                fill='tozeroy',
                hovertemplate='<b>%{x}</b><br>Utilization: %{y:.1f}%<br>Active: %{customdata[0]}/{customdata[1]} seats<extra></extra>',
                customdata=df_util[['active_seats', 'total_seats']]
            ))
            
            # Add target line at 80%
            fig_util.add_hline(
                y=80,
                line_dash="dash",
                line_color="orange",
                annotation_text="Target: 80%",
                annotation_position="right"
            )
            
            fig_util.update_layout(
                title="Seat Utilization Over Time",
                xaxis_title="Date",
                yaxis_title="Utilization (%)",
                yaxis_range=[0, 100],
                height=400
            )
            
            st.plotly_chart(fig_util, use_container_width=True)
        
        with col2:
            st.markdown("#### Current Status")
            
            current = filtered_util[-1]
            current_util = current['utilization_rate'] * 100
            
            # Gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=current_util,
                title={'text': "Current Utilization"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "lightyellow"},
                        {'range': [80, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.metric("Active Seats", f"{current['active_seats']}/{current['total_seats']}")
            st.metric("Unused Seats", current['total_seats'] - current['active_seats'])
    else:
        st.warning("No data available for selected date range.")
else:
    st.error("No seat utilization data found.")

st.divider()

# ROI Analysis
st.header("💰 Return on Investment Analysis")

if data['usage'].get('daily_usage'):
    usage_data = data['usage']['daily_usage']
    
    # Filter by date
    filtered_usage = [
        u for u in usage_data
        if start_date <= datetime.fromisoformat(u['date']).date() <= end_date
    ]
    
    if filtered_usage:
        df_roi = pd.DataFrame(filtered_usage)
        df_roi['date'] = pd.to_datetime(df_roi['date'])
        
        # Calculate time saved per day (2 min per acceptance)
        df_roi['time_saved_hours'] = (df_roi['acceptances'] * 2) / 60
        df_roi['value_saved'] = df_roi['time_saved_hours'] * hourly_rate
        
        # Calculate daily seat cost
        df_roi['daily_seat_cost'] = (total_seats * seat_cost) / 30
        
        # Cumulative values
        df_roi['cumulative_value'] = df_roi['value_saved'].cumsum()
        df_roi['cumulative_cost'] = df_roi['daily_seat_cost'].cumsum()
        df_roi['cumulative_roi'] = df_roi['cumulative_value'] - df_roi['cumulative_cost']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # KPI Cards
            st.markdown("#### Time Savings")
            total_time = df_roi['time_saved_hours'].sum()
            st.metric("Total Time Saved", f"{total_time:,.0f}h", help="Based on 2 min per accepted suggestion")
            st.metric("Avg Time Saved/Day", f"{total_time/len(df_roi):.1f}h")
            
            st.markdown("#### Financial Impact")
            total_value = df_roi['value_saved'].sum()
            total_cost = df_roi['daily_seat_cost'].sum()
            net_roi = total_value - total_cost
            roi_pct = ((total_value / total_cost) - 1) * 100 if total_cost > 0 else 0
            
            st.metric("Total Value Saved", f"${total_value:,.0f}")
            st.metric("Total Seat Cost", f"${total_cost:,.0f}")
            st.metric("Net ROI", f"${net_roi:,.0f}", delta=f"{roi_pct:.0f}%")
        
        with col2:
            # Cumulative ROI chart
            fig_roi = go.Figure()
            
            fig_roi.add_trace(go.Scatter(
                x=df_roi['date'],
                y=df_roi['cumulative_value'],
                mode='lines',
                name='Cumulative Value',
                line=dict(color='#2ca02c', width=3),
                hovertemplate='<b>%{x}</b><br>Value: $%{y:,.0f}<extra></extra>'
            ))
            
            fig_roi.add_trace(go.Scatter(
                x=df_roi['date'],
                y=df_roi['cumulative_cost'],
                mode='lines',
                name='Cumulative Cost',
                line=dict(color='#d62728', width=3, dash='dash'),
                hovertemplate='<b>%{x}</b><br>Cost: $%{y:,.0f}<extra></extra>'
            ))
            
            fig_roi.add_trace(go.Scatter(
                x=df_roi['date'],
                y=df_roi['cumulative_roi'],
                mode='lines',
                name='Net ROI',
                line=dict(color='#1f77b4', width=3),
                fill='tozeroy',
                hovertemplate='<b>%{x}</b><br>Net ROI: $%{y:,.0f}<extra></extra>'
            ))
            
            fig_roi.update_layout(
                title="Cumulative ROI Over Time",
                xaxis_title="Date",
                yaxis_title="Amount ($)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_roi, use_container_width=True)
        
        # ROI Breakdown
        st.markdown("#### ROI Assumptions")
        st.info(
            f"**Calculation Method:**\n"
            f"- Time Saved: 2 minutes per accepted suggestion\n"
            f"- Developer Rate: ${hourly_rate}/hour\n"
            f"- Seat Cost: ${seat_cost}/month ({total_seats} seats)\n"
            f"- Period: {len(filtered_usage)} days"
        )
    else:
        st.warning("No data available for selected date range.")
else:
    st.error("No usage data found.")

st.divider()

# Footer
st.markdown("---")
st.caption("🤖 Copilot Dashboard | DevMetrics v1.0")
