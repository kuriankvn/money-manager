"""Streamlit Home page."""
import streamlit as st
from app.storage.db import get_connection
from app.dashboard.monthly import MonthlyDashboard
from app.dashboard.yearly import YearlyDashboard
from app.dashboard.investments import InvestmentDashboard
from app.accounts.repository import TransactionRepository
from app.subscriptions.repository import SubscriptionInstanceRepository
from app.investments.repository import (
    InvestmentRepository,
    InvestmentContributionRepository,
    InvestmentValueSnapshotRepository
)
from app.investments.calculator import InvestmentCalculator
from datetime import date


st.set_page_config(
    page_title="Personal Finance Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💰 Personal Finance Manager")

st.markdown("""
Welcome to **Personal Finance Manager**! Track your finances with ease.

---

## 📋 Features

Use the sidebar to navigate between sections:

- **🏦 Accounts**: Manage accounts and transactions
- **🔄 Subscriptions**: Track recurring payments with import/export
- **📈 Investments**: Monitor portfolio with import/export

---

## 🚀 Getting Started

### Prerequisites

1. **Backend must be running**:
   ```bash
   uvicorn app.api.main:app --reload
   ```
   Backend URL: http://localhost:8000

2. **API Documentation**: http://localhost:8000/docs

### Usage Tips

- 📝 Create accounts first before adding transactions
- 🔄 Subscriptions auto-generate payment instances
- 📊 Track investment performance with snapshots
- 💾 Use import/export for bulk data operations
- ⏰ All dates use ISO format (YYYY-MM-DD)

---

## 🎨 Dashboard Overview

""")


def get_dashboards():
    """Get fresh dashboard instances with new connection."""
    conn = get_connection()
    
    txn_repo = TransactionRepository(conn=conn)
    sub_inst_repo = SubscriptionInstanceRepository(conn=conn)
    
    monthly_dash = MonthlyDashboard(
        transaction_repo=txn_repo,
        subscription_instance_repo=sub_inst_repo
    )
    
    yearly_dash = YearlyDashboard(
        transaction_repo=txn_repo,
        subscription_instance_repo=sub_inst_repo
    )
    
    inv_repo = InvestmentRepository(conn=conn)
    contrib_repo = InvestmentContributionRepository(conn=conn)
    snapshot_repo = InvestmentValueSnapshotRepository(conn=conn)
    calculator = InvestmentCalculator()
    
    inv_dash = InvestmentDashboard(
        investment_repo=inv_repo,
        contribution_repo=contrib_repo,
        snapshot_repo=snapshot_repo,
        calculator=calculator
    )
    
    return monthly_dash, yearly_dash, inv_dash


monthly_dash, yearly_dash, inv_dash = get_dashboards()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Monthly Overview")
    today = date.today()
    overview = monthly_dash.get_monthly_overview(year=today.year, month=today.month)
    
    st.metric("Income", f"₹{overview['transactions']['income']:,.2f}")
    st.metric("Expenses", f"₹{overview['transactions']['expenses']:,.2f}")
    st.metric("Net", f"₹{overview['transactions']['net']:,.2f}")
    
    st.markdown("**Subscriptions**")
    st.write(f"Total Due: ₹{overview['subscriptions']['total_due']:,.2f}")
    st.write(f"Unpaid: {overview['subscriptions']['unpaid_count']}")

with col2:
    st.subheader("📊 Portfolio Overview")
    portfolio = inv_dash.get_portfolio_overview()
    
    total_invested = portfolio['portfolio_total']['total_invested']
    total_current = portfolio['portfolio_total']['total_current_value']
    total_gain = portfolio['portfolio_total']['total_gain_loss']
    
    st.metric("Total Invested", f"₹{total_invested:,.2f}")
    st.metric("Current Value", f"₹{total_current:,.2f}" if total_current else "N/A")
    st.metric("Gain/Loss", f"₹{total_gain:,.2f}" if total_gain else "N/A")

st.markdown("---")

with st.sidebar:
    st.markdown("### 🔗 Quick Links")
    st.markdown("- [Backend API](http://localhost:8000)")
    st.markdown("- [API Docs](http://localhost:8000/docs)")
    
    st.markdown("---")
    st.markdown("### ℹ️ System Info")
    st.info("Backend: http://localhost:8000")
    st.info("Streamlit UI: http://localhost:8501")
