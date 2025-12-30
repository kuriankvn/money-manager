"""Investment Value Snapshots CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Investment Snapshots", page_icon="📊", layout="wide")

st.title("📊 Investment Value Snapshots")

# Initialize session state
if 'snapshots_data' not in st.session_state:
    st.session_state.snapshots_data = None
if 'investments_list' not in st.session_state:
    st.session_state.investments_list = []


def load_snapshots():
    """Load investment snapshots from API"""
    success, data = api_client.get_investment_snapshots()
    if success and data:
        df = pd.DataFrame(data)
        # Date is already in string format from API
        st.session_state.snapshots_data = df
        return df
    elif success:
        st.session_state.snapshots_data = pd.DataFrame(columns=[
            "uid", "investment_uid", "investment_name", "date", "current_value"
        ])
        return st.session_state.snapshots_data
    else:
        st.error(f"Failed to fetch snapshots: {data}")
        return pd.DataFrame(columns=[
            "uid", "investment_uid", "investment_name", "date", "current_value"
        ])


def load_investments():
    """Load investments for dropdown"""
    success, data = api_client.get_investments()
    if success and data:
        st.session_state.investments_list = [(inv['name'], inv['uid']) for inv in data]
    else:
        st.session_state.investments_list = []
    return st.session_state.investments_list


# Create tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View All", "➕ Create", "✏️ Update", "🗑️ Delete"])

with tab1:
    st.subheader("All Investment Snapshots")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_snapshots"):
            load_snapshots()
            load_investments()
            st.rerun()
    
    # Load and display snapshots
    df = load_snapshots()
    
    if not df.empty:
        # Hide UUID columns, show only names
        display_columns = ["uid", "investment_name", "date", "current_value"]
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="small"),
                "investment_name": st.column_config.TextColumn("Investment", width="medium"),
                "date": st.column_config.TextColumn("Date", width="medium"),
                "current_value": st.column_config.NumberColumn("Current Value", format="₹%.2f"),
            }
        )
        
        # Summary statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Snapshots", len(df))
        with col2:
            if 'current_value' in df.columns and not df.empty:
                latest_total = df.groupby('investment_name')['current_value'].last().sum()
                st.metric("Latest Total Value", f"₹{latest_total:.2f}")
    else:
        st.info("No snapshots found. Create your first snapshot!")

with tab2:
    st.subheader("Create New Snapshot")
    
    # Load investments
    investments = load_investments()
    
    if not investments:
        st.warning("⚠️ No investments found. Please create an investment first!")
    else:
        with st.form("create_snapshot_form", clear_on_submit=True):
            investment_options = {f"{inv[0]} ({inv[1]})": inv[1] for inv in investments}
            selected_investment = st.selectbox("Investment *", options=list(investment_options.keys()))
            
            snapshot_date = st.date_input("Date *", value=datetime.now())
            current_value = st.number_input("Current Value *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            
            submitted = st.form_submit_button("➕ Create Snapshot", type="primary", width='stretch')
            
            if submitted:
                if not selected_investment:
                    st.error("❌ Please select an investment")
                elif current_value <= 0:
                    st.error("❌ Current value must be greater than 0")
                else:
                    investment_uid = investment_options[selected_investment]
                    date_str = snapshot_date.strftime('%Y-%m-%d')
                    
                    success, data = api_client.create_investment_snapshot(
                        investment_uid, date_str, current_value
                    )
                    if success:
                        st.success(f"✅ Snapshot created")
                        load_snapshots()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create snapshot: {data}")

with tab3:
    st.subheader("Update Snapshot")
    
    # Load investments
    investments = load_investments()
    
    if not investments:
        st.warning("⚠️ No investments found. Please create an investment first!")
    else:
        with st.form("update_snapshot_form"):
            uid = st.text_input("Snapshot UID *", placeholder="Enter UID to update")
            
            investment_options = {f"{inv[0]} ({inv[1]})": inv[1] for inv in investments}
            selected_investment = st.selectbox("Investment *", options=list(investment_options.keys()))
            
            snapshot_date = st.date_input("Date *", value=datetime.now())
            current_value = st.number_input("Current Value *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            
            submitted = st.form_submit_button("✏️ Update Snapshot", type="secondary", width='stretch')
            
            if submitted:
                if not uid or not uid.strip():
                    st.error("❌ Snapshot UID is required")
                elif not selected_investment:
                    st.error("❌ Please select an investment")
                elif current_value <= 0:
                    st.error("❌ Current value must be greater than 0")
                else:
                    investment_uid = investment_options[selected_investment]
                    date_str = snapshot_date.strftime('%Y-%m-%d')
                    
                    success, data = api_client.update_investment_snapshot(
                        uid.strip(), investment_uid, date_str, current_value
                    )
                    if success:
                        st.success(f"✅ Snapshot updated")
                        load_snapshots()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update snapshot: {data}")

with tab4:
    st.subheader("Delete Snapshot")
    
    with st.form("delete_snapshot_form"):
        uid = st.text_input("Snapshot UID *", placeholder="Enter UID to delete")
        
        confirm = st.checkbox("I understand this action cannot be undone")
        
        submitted = st.form_submit_button("🗑️ Delete Snapshot", type="primary", width='stretch')
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Snapshot UID is required")
            elif not confirm:
                st.error("❌ Please confirm deletion")
            else:
                success, data = api_client.delete_investment_snapshot(uid.strip())
                if success:
                    st.success("✅ Snapshot deleted successfully")
                    load_snapshots()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete snapshot: {data}")

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Track investment value over time
    - Record snapshots periodically (daily, weekly, monthly)
    - Monitor growth and performance
    - Compare values across different dates
    
    **Best Practices:**
    - Record snapshots at consistent intervals
    - Include all fees and charges in value
    - Keep historical records for analysis
    - Use for calculating returns and performance
    """)

# Made with Bob
