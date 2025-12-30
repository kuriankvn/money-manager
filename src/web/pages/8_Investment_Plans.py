"""Investment Plans CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Investment Plans", page_icon="📝", layout="wide")

st.title("📝 Investment Plans Management")

# Initialize session state
if 'investment_plans_data' not in st.session_state:
    st.session_state.investment_plans_data = None
if 'investments_list' not in st.session_state:
    st.session_state.investments_list = []


def load_investment_plans():
    """Load investment plans from API"""
    success, data = api_client.get_investment_plans()
    if success and data:
        st.session_state.investment_plans_data = pd.DataFrame(data)
        return st.session_state.investment_plans_data
    elif success:
        st.session_state.investment_plans_data = pd.DataFrame(columns=[
            "uid", "investment_uid", "investment_name", "amount", "frequency", "interval", "status"
        ])
        return st.session_state.investment_plans_data
    else:
        st.error(f"Failed to fetch investment plans: {data}")
        return pd.DataFrame(columns=[
            "uid", "investment_uid", "investment_name", "amount", "frequency", "interval", "status"
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
    st.subheader("All Investment Plans")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_plans"):
            load_investment_plans()
            load_investments()
            st.rerun()
    
    # Load and display investment plans
    df = load_investment_plans()
    
    if not df.empty:
        # Color code by status
        def highlight_status(row):
            if row['status'] == 'active':
                return ['background-color: #90EE90; color: #000000'] * len(row)
            elif row['status'] == 'closed':
                return ['background-color: #FF6B6B; color: #000000'] * len(row)
            return [''] * len(row)
        
        # Hide UUID columns, show only names
        display_columns = ["uid", "investment_name", "amount", "frequency", "interval", "status"]
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        st.dataframe(
            display_df.style.apply(highlight_status, axis=1),
            width='stretch',
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="small"),
                "investment_name": st.column_config.TextColumn("Investment", width="medium"),
                "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                "frequency": st.column_config.TextColumn("Frequency", width="small"),
                "interval": st.column_config.NumberColumn("Interval", width="small"),
                "status": st.column_config.TextColumn("Status", width="small"),
            }
        )
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Plans", len(df))
        with col2:
            active_count = (df['status'] == 'active').sum() if 'status' in df.columns else 0
            st.metric("Active", active_count)
        with col3:
            total_amount = df[df['status'] == 'active']['amount'].sum() if 'status' in df.columns else 0
            st.metric("Total Active Amount", f"₹{total_amount:.2f}")
    else:
        st.info("No investment plans found. Create your first plan!")

with tab2:
    st.subheader("Create New Investment Plan")
    
    # Load investments
    investments = load_investments()
    
    if not investments:
        st.warning("⚠️ No investments found. Please create an investment first!")
    else:
        with st.form("create_plan_form", clear_on_submit=True):
            investment_options = {f"{inv[0]} ({inv[1]})": inv[1] for inv in investments}
            selected_investment = st.selectbox("Investment *", options=list(investment_options.keys()))
            
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            
            col1, col2 = st.columns(2)
            with col1:
                frequency = st.selectbox("Frequency *", options=["monthly", "yearly"])
            with col2:
                interval = st.number_input("Interval *", min_value=1, value=1, step=1)
            
            status = st.radio("Status *", options=["active", "closed"], horizontal=True)
            
            submitted = st.form_submit_button("➕ Create Plan", type="primary", width='stretch')
            
            if submitted:
                if not selected_investment:
                    st.error("❌ Please select an investment")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                elif interval < 1:
                    st.error("❌ Interval must be at least 1")
                else:
                    investment_uid = investment_options[selected_investment]
                    
                    success, data = api_client.create_investment_plan(
                        investment_uid, amount, frequency, interval, status
                    )
                    if success:
                        st.success(f"✅ Investment plan created")
                        load_investment_plans()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create plan: {data}")

with tab3:
    st.subheader("Update Investment Plan")
    
    # Load investments
    investments = load_investments()
    
    if not investments:
        st.warning("⚠️ No investments found. Please create an investment first!")
    else:
        with st.form("update_plan_form"):
            uid = st.text_input("Plan UID *", placeholder="Enter UID to update")
            
            investment_options = {f"{inv[0]} ({inv[1]})": inv[1] for inv in investments}
            selected_investment = st.selectbox("Investment *", options=list(investment_options.keys()))
            
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            
            col1, col2 = st.columns(2)
            with col1:
                frequency = st.selectbox("Frequency *", options=["monthly", "yearly"])
            with col2:
                interval = st.number_input("Interval *", min_value=1, value=1, step=1)
            
            status = st.radio("Status *", options=["active", "closed"], horizontal=True)
            
            submitted = st.form_submit_button("✏️ Update Plan", type="secondary", width='stretch')
            
            if submitted:
                if not uid or not uid.strip():
                    st.error("❌ Plan UID is required")
                elif not selected_investment:
                    st.error("❌ Please select an investment")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                elif interval < 1:
                    st.error("❌ Interval must be at least 1")
                else:
                    investment_uid = investment_options[selected_investment]
                    
                    success, data = api_client.update_investment_plan(
                        uid.strip(), investment_uid, amount, frequency, interval, status
                    )
                    if success:
                        st.success(f"✅ Investment plan updated")
                        load_investment_plans()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update plan: {data}")

with tab4:
    st.subheader("Delete Investment Plan")
    
    st.warning("⚠️ Warning: Deleting a plan will also delete all associated plan instances!")
    
    with st.form("delete_plan_form"):
        uid = st.text_input("Plan UID *", placeholder="Enter UID to delete")
        
        confirm = st.checkbox("I understand this action cannot be undone")
        
        submitted = st.form_submit_button("🗑️ Delete Plan", type="primary", width='stretch')
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Plan UID is required")
            elif not confirm:
                st.error("❌ Please confirm deletion")
            else:
                success, data = api_client.delete_investment_plan(uid.strip())
                if success:
                    st.success("✅ Investment plan deleted successfully")
                    load_investment_plans()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete plan: {data}")

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Set up recurring investment contributions
    - Automate your investment strategy
    - Track planned vs actual investments
    - Frequency: monthly or yearly
    - Interval: how often (e.g., every 1 month, every 3 months)
    
    **Examples:**
    - Monthly SIP (Systematic Investment Plan)
    - Quarterly contributions
    - Annual lump sum investments
    - Dollar-cost averaging strategy
    """)

# Made with Bob
