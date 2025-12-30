"""Investments CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Investments", page_icon="💼", layout="wide")

st.title("💼 Investments Management")

# Initialize session state
if 'investments_data' not in st.session_state:
    st.session_state.investments_data = None


def load_investments():
    """Load investments from API"""
    success, data = api_client.get_investments()
    if success and data:
        df = pd.DataFrame(data)
        # Date is already in string format from API
        st.session_state.investments_data = df
        return df
    elif success:
        st.session_state.investments_data = pd.DataFrame(columns=[
            "uid", "name", "start_date", "status"
        ])
        return st.session_state.investments_data
    else:
        st.error(f"Failed to fetch investments: {data}")
        return pd.DataFrame(columns=[
            "uid", "name", "start_date", "status"
        ])


# Create tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View All", "➕ Create", "✏️ Update", "🗑️ Delete"])

with tab1:
    st.subheader("All Investments")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_investments"):
            load_investments()
            st.rerun()
    
    # Load and display investments
    df = load_investments()
    
    if not df.empty:
        # Color code by status
        def highlight_status(row):
            if row['status'] == 'active':
                return ['background-color: #90EE90; color: #000000'] * len(row)
            elif row['status'] == 'closed':
                return ['background-color: #FF6B6B; color: #000000'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            df.style.apply(highlight_status, axis=1),
            width='stretch',
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="medium"),
                "name": st.column_config.TextColumn("Name", width="large"),
                "start_date": st.column_config.TextColumn("Start Date", width="medium"),
                "status": st.column_config.TextColumn("Status", width="small"),
            }
        )
        
        # Summary statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Investments", len(df))
        with col2:
            active_count = (df['status'] == 'active').sum() if 'status' in df.columns else 0
            st.metric("Active", active_count)
    else:
        st.info("No investments found. Create your first investment!")

with tab2:
    st.subheader("Create New Investment")
    
    with st.form("create_investment_form", clear_on_submit=True):
        name = st.text_input("Investment Name *", placeholder="Enter investment name")
        start_date = st.date_input("Start Date *", value=datetime.now())
        status = st.radio("Status *", options=["active", "closed"], horizontal=True)
        
        submitted = st.form_submit_button("➕ Create Investment", type="primary", width='stretch')
        
        if submitted:
            if not name or not name.strip():
                st.error("❌ Investment name is required")
            else:
                date_str = start_date.strftime('%Y-%m-%d')
                success, data = api_client.create_investment(name.strip(), date_str, status)
                if success:
                    st.success(f"✅ Investment created: {data['name']}")
                    load_investments()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create investment: {data}")

with tab3:
    st.subheader("Update Investment")
    
    with st.form("update_investment_form"):
        uid = st.text_input("Investment UID *", placeholder="Enter UID to update")
        name = st.text_input("New Name *", placeholder="Enter new name")
        start_date = st.date_input("Start Date *", value=datetime.now())
        status = st.radio("Status *", options=["active", "closed"], horizontal=True)
        
        submitted = st.form_submit_button("✏️ Update Investment", type="secondary", width='stretch')
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Investment UID is required")
            elif not name or not name.strip():
                st.error("❌ Name is required")
            else:
                date_str = start_date.strftime('%Y-%m-%d')
                success, data = api_client.update_investment(uid.strip(), name.strip(), date_str, status)
                if success:
                    st.success(f"✅ Investment updated: {data['name']}")
                    load_investments()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update investment: {data}")

with tab4:
    st.subheader("Delete Investment")
    
    st.warning("⚠️ Warning: Deleting an investment will also delete all associated snapshots, plans, and plan instances!")
    
    with st.form("delete_investment_form"):
        uid = st.text_input("Investment UID *", placeholder="Enter UID to delete")
        
        confirm = st.checkbox("I understand this action cannot be undone")
        
        submitted = st.form_submit_button("🗑️ Delete Investment", type="primary", width='stretch')
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Investment UID is required")
            elif not confirm:
                st.error("❌ Please confirm deletion")
            else:
                success, data = api_client.delete_investment(uid.strip())
                if success:
                    st.success("✅ Investment deleted successfully")
                    load_investments()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete investment: {data}")

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Track your investment portfolios
    - Each investment can have multiple value snapshots
    - Set up recurring investment plans
    - Status: 'active' (ongoing), 'closed' (completed)
    
    **Examples:**
    - Mutual Funds
    - Stocks
    - Fixed Deposits
    - Real Estate
    - Retirement Accounts
    """)

# Made with Bob
