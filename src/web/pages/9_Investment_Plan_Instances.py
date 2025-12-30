"""Investment Plan Instances CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Investment Plan Instances", page_icon="🎯", layout="wide")

st.title("🎯 Investment Plan Instances Management")

# Initialize session state
if 'plan_instances_data' not in st.session_state:
    st.session_state.plan_instances_data = None
if 'investment_plans_list' not in st.session_state:
    st.session_state.investment_plans_list = []
if 'transactions_list' not in st.session_state:
    st.session_state.transactions_list = []


def load_plan_instances():
    """Load investment plan instances from API"""
    success, data = api_client.get_investment_plan_instances()
    if success and data:
        df = pd.DataFrame(data)
        # Date is already in string format from API
        st.session_state.plan_instances_data = df
        return df
    elif success:
        st.session_state.plan_instances_data = pd.DataFrame(columns=[
            "uid", "investment_plan_uid", "plan_name", "amount", "due_date",
            "transaction_uid", "transaction_name", "status"
        ])
        return st.session_state.plan_instances_data
    else:
        st.error(f"Failed to fetch plan instances: {data}")
        return pd.DataFrame(columns=[
            "uid", "investment_plan_uid", "plan_name", "amount", "due_date",
            "transaction_uid", "transaction_name", "status"
        ])


def load_investment_plans():
    """Load investment plans for dropdown"""
    success, data = api_client.get_investment_plans()
    if success and data:
        st.session_state.investment_plans_list = [(plan['investment_name'], plan['uid']) for plan in data]
    else:
        st.session_state.investment_plans_list = []
    return st.session_state.investment_plans_list


def load_transactions():
    """Load transactions for dropdown"""
    success, data = api_client.get_transactions()
    if success and data:
        st.session_state.transactions_list = [(txn['name'], txn['uid']) for txn in data]
    else:
        st.session_state.transactions_list = []
    return st.session_state.transactions_list


# Create tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View All", "➕ Create", "✏️ Update", "🗑️ Delete"])

with tab1:
    st.subheader("All Investment Plan Instances")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_instances"):
            load_plan_instances()
            load_investment_plans()
            load_transactions()
            st.rerun()
    
    # Load and display plan instances
    df = load_plan_instances()
    
    if not df.empty:
        # Color code by status
        def highlight_status(row):
            if row['status'] == 'executed':
                return ['background-color: #90EE90; color: #000000'] * len(row)
            elif row['status'] == 'skipped':
                return ['background-color: #FF6B6B; color: #000000'] * len(row)
            elif row['status'] == 'planned':
                return ['background-color: #FFD700; color: #000000'] * len(row)
            return [''] * len(row)
        
        # Hide UUID columns, show only names
        display_columns = ["uid", "plan_name", "amount", "due_date", "transaction_name", "status"]
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        st.dataframe(
            display_df.style.apply(highlight_status, axis=1),
            width='stretch',
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="small"),
                "plan_name": st.column_config.TextColumn("Plan", width="medium"),
                "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                "due_date": st.column_config.TextColumn("Due Date", width="medium"),
                "transaction_name": st.column_config.TextColumn("Transaction", width="medium"),
                "status": st.column_config.TextColumn("Status", width="small"),
            }
        )
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Instances", len(df))
        with col2:
            planned_count = (df['status'] == 'planned').sum() if 'status' in df.columns else 0
            st.metric("Planned", planned_count)
        with col3:
            executed_count = (df['status'] == 'executed').sum() if 'status' in df.columns else 0
            st.metric("Executed", executed_count)
    else:
        st.info("No plan instances found. Create your first instance!")

with tab2:
    st.subheader("Create New Plan Instance")
    
    # Load investment plans and transactions
    plans = load_investment_plans()
    transactions = load_transactions()
    
    if not plans:
        st.warning("⚠️ No investment plans found. Please create an investment plan first!")
    else:
        with st.form("create_instance_form", clear_on_submit=True):
            plan_options = {f"{plan[0]} ({plan[1]})": plan[1] for plan in plans}
            selected_plan = st.selectbox("Investment Plan *", options=list(plan_options.keys()))
            
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            due_date = st.date_input("Due Date *", value=datetime.now())
            
            # Optional transaction link
            link_transaction = st.checkbox("Link to Transaction")
            selected_transaction = None
            if link_transaction and transactions:
                transaction_options = {f"{txn[0]} ({txn[1]})": txn[1] for txn in transactions}
                selected_transaction = st.selectbox("Transaction", options=list(transaction_options.keys()))
            
            status = st.radio("Status *", options=["planned", "executed", "skipped"], horizontal=True)
            
            submitted = st.form_submit_button("➕ Create Instance", type="primary", width='stretch')
            
            if submitted:
                if not selected_plan:
                    st.error("❌ Please select an investment plan")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                else:
                    plan_uid = plan_options[selected_plan]
                    transaction_uid = transaction_options[selected_transaction] if selected_transaction else None
                    date_str = due_date.strftime('%Y-%m-%d')
                    
                    success, data = api_client.create_investment_plan_instance(
                        plan_uid, amount, date_str, transaction_uid, status
                    )
                    if success:
                        st.success(f"✅ Plan instance created")
                        load_plan_instances()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create instance: {data}")

with tab3:
    st.subheader("Update Plan Instance")
    
    # Load investment plans and transactions
    plans = load_investment_plans()
    transactions = load_transactions()
    
    if not plans:
        st.warning("⚠️ No investment plans found. Please create an investment plan first!")
    else:
        with st.form("update_instance_form"):
            uid = st.text_input("Instance UID *", placeholder="Enter UID to update")
            
            plan_options = {f"{plan[0]} ({plan[1]})": plan[1] for plan in plans}
            selected_plan = st.selectbox("Investment Plan *", options=list(plan_options.keys()))
            
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            due_date = st.date_input("Due Date *", value=datetime.now())
            
            # Optional transaction link
            link_transaction = st.checkbox("Link to Transaction")
            selected_transaction = None
            if link_transaction and transactions:
                transaction_options = {f"{txn[0]} ({txn[1]})": txn[1] for txn in transactions}
                selected_transaction = st.selectbox("Transaction", options=list(transaction_options.keys()))
            
            status = st.radio("Status *", options=["planned", "executed", "skipped"], horizontal=True)
            
            submitted = st.form_submit_button("✏️ Update Instance", type="secondary", width='stretch')
            
            if submitted:
                if not uid or not uid.strip():
                    st.error("❌ Instance UID is required")
                elif not selected_plan:
                    st.error("❌ Please select an investment plan")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                else:
                    plan_uid = plan_options[selected_plan]
                    transaction_uid = transaction_options[selected_transaction] if selected_transaction else None
                    date_str = due_date.strftime('%Y-%m-%d')
                    
                    success, data = api_client.update_investment_plan_instance(
                        uid.strip(), plan_uid, amount, date_str, transaction_uid, status
                    )
                    if success:
                        st.success(f"✅ Plan instance updated")
                        load_plan_instances()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update instance: {data}")

with tab4:
    st.subheader("Delete Plan Instance")
    
    with st.form("delete_instance_form"):
        uid = st.text_input("Instance UID *", placeholder="Enter UID to delete")
        
        confirm = st.checkbox("I understand this action cannot be undone")
        
        submitted = st.form_submit_button("🗑️ Delete Instance", type="primary", width='stretch')
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Instance UID is required")
            elif not confirm:
                st.error("❌ Please confirm deletion")
            else:
                success, data = api_client.delete_investment_plan_instance(uid.strip())
                if success:
                    st.success("✅ Plan instance deleted successfully")
                    load_plan_instances()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete instance: {data}")

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Track individual investment contributions
    - Link instances to transactions when executed
    - Status: 'planned' (upcoming), 'executed' (completed), 'skipped' (missed)
    - Automatically generated from investment plans
    
    **Workflow:**
    1. Plan instances are created based on investment plan frequency
    2. Mark as 'executed' and link to transaction when contribution is made
    3. Mark as 'skipped' if you decide not to invest for that period
    4. Track your investment discipline and consistency
    """)

# Made with Bob
