"""DevMetrics Dashboard - Main Streamlit Application."""

import streamlit as st

st.set_page_config(
    page_title="DevMetrics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 DevMetrics Dashboard")
st.markdown("### Engineering metrics and Copilot ROI analytics")

st.sidebar.title("Navigation")
st.sidebar.info(
    "Select a dashboard from the pages above:\n\n"
    "- **SPACE Dashboard**: Engineering velocity metrics\n"
    "- **Copilot Dashboard**: AI productivity & ROI metrics"
)

# Welcome content
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 🚀 SPACE Metrics")
    st.markdown("""
    Track key engineering velocity indicators:
    - **PR Cycle Time**: How fast code moves from open to merge
    - **Review Turnaround**: Speed of first review feedback
    - **Rework Rate**: Quality and efficiency of changes
    - **Work in Progress**: Flow efficiency across repos
    """)
    
with col2:
    st.markdown("## 🤖 Copilot Metrics")
    st.markdown("""
    Measure AI-assisted development impact:
    - **Active Users**: Copilot adoption trends
    - **Acceptance Rate**: AI suggestion quality
    - **Seat Utilization**: License efficiency
    - **ROI Analysis**: Time & cost savings
    """)

st.divider()

st.markdown("### 📁 Data Source")
st.info("Currently using generated dummy data. Switch to live GitHub API in production.")

st.markdown("### 🎯 Getting Started")
st.markdown("Use the sidebar or pages menu above to navigate to a dashboard.")
