"""Subscription Instances CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Subscription Instances", page_icon="📅", layout="wide")

st.title("📅 Subscription Instances Management")

# Initialize session state
if 'subscription_instances_data' not in st.session_state:
    st.session_state.subscription_instances_data = None
if 'subscriptions_list' not in st.session_state:
    st.session_state.subscriptions_list = []
if 'transactions_list' not in st.session_state:
    st.session_state.transactions_list = []


def load_subscription_instances():
    """Load subscription instances from API"""
    success, data = api_client.get_subscription_instances()
    if success and data:
        df = pd.DataFrame(data)
        # Date is already in string format from API
        st.session_state.subscription_instances_data = df
        return df
    elif success:
        st.session_state.subscription_instances_data = pd.DataFrame(columns=[
            "uid", "subscription_uid", "subscription_name", "amount", "due_date",
            "transaction_uid", "transaction_name", "status"
        ])
        return st.session_state.subscription_instances_data
    else:
        st.error(f"Failed to fetch subscription instances: {data}")
        return pd.DataFrame(columns=[
            "uid", "subscription_uid", "subscription_name", "amount", "due_date",
            "transaction_uid", "transaction_name", "status"
        ])


def load_subscriptions():
    """Load subscriptions for dropdown"""
    success, data = api_client.get_subscriptions()
    if success and data:
        st.session_state.subscriptions_list = [(sub['name'], sub['uid']) for sub in data]
    else:
        st.session_state.subscriptions_list = []
    return st.session_state.subscriptions_list


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
    st.subheader("All Subscription Instances")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_instances"):
            load_subscription_instances()
            load_subscriptions()
            load_transactions()
            st.rerun()
    
    # Load and display subscription instances
    df = load_subscription_instances()
    
    if not df.empty:
        # Color code by status
        def highlight_status(row):
            if row['status'] == 'paid':
                return ['background-color: #90EE90; color: #000000'] * len(row)
            elif row['status'] == 'overdue':
                return ['background-color: #FF6B6B; color: #000000'] * len(row)
            elif row['status'] == 'due':
                return ['background-color: #FFD700; color: #000000'] * len(row)
            return [''] * len(row)
        
        # Hide UUID columns, show only names
        display_columns = ["uid", "subscription_name", "amount", "due_date", "transaction_name", "status"]
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        st.dataframe(
            display_df.style.apply(highlight_status, axis=1),
            width='stretch',
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="small"),
                "subscription_name": st.column_config.TextColumn("Subscription", width="medium"),
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
            due_count = (df['status'] == 'due').sum() if 'status' in df.columns else 0
            st.metric("Due", due_count)
        with col3:
            paid_count = (df['status'] == 'paid').sum() if 'status' in df.columns else 0
            st.metric("Paid", paid_count)
    else:
        st.info("No subscription instances found. Create your first instance!")

with tab2:
    st.subheader("Create New Subscription Instance")
    
    # Load subscriptions and transactions
    subscriptions = load_subscriptions()
    transactions = load_transactions()
    
    if not subscriptions:
        st.warning("⚠️ No subscriptions found. Please create a subscription first!")
    else:
        with st.form("create_instance_form", clear_on_submit=True):
            subscription_options = {f"{sub[0]} ({sub[1]})": sub[1] for sub in subscriptions}
            selected_subscription = st.selectbox("Subscription *", options=list(subscription_options.keys()))
            
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            due_date = st.date_input("Due Date *", value=datetime.now())
            
            # Optional transaction link
            link_transaction = st.checkbox("Link to Transaction")
            selected_transaction = None
            if link_transaction and transactions:
                transaction_options = {f"{txn[0]} ({txn[1]})": txn[1] for txn in transactions}
                selected_transaction = st.selectbox("Transaction", options=list(transaction_options.keys()))
            
            status = st.radio("Status *", options=["due", "paid", "overdue"], horizontal=True)
            
            submitted = st.form_submit_button("➕ Create Instance", type="primary", width='stretch')
            
            if submitted:
                if not selected_subscription:
                    st.error("❌ Please select a subscription")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                else:
                    subscription_uid = subscription_options[selected_subscription]
                    transaction_uid = transaction_options[selected_transaction] if selected_transaction else None
                    date_str = due_date.strftime('%Y-%m-%d')
                    
                    success, data = api_client.create_subscription_instance(
                        subscription_uid, amount, date_str, transaction_uid, status
                    )
                    if success:
                        st.success(f"✅ Subscription instance created")
                        load_subscription_instances()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create instance: {data}")

with tab3:
    st.subheader("Update Subscription Instance")
    
    # Load subscriptions and transactions
    subscriptions = load_subscriptions()
    transactions = load_transactions()
    
    if not subscriptions:
        st.warning("⚠️ No subscriptions found. Please create a subscription first!")
    else:
        with st.form("update_instance_form"):
            uid = st.text_input("Instance UID *", placeholder="Enter UID to update")
            
            subscription_options = {f"{sub[0]} ({sub[1]})": sub[1] for sub in subscriptions}
            selected_subscription = st.selectbox("Subscription *", options=list(subscription_options.keys()))
            
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            due_date = st.date_input("Due Date *", value=datetime.now())
            
            # Optional transaction link
            link_transaction = st.checkbox("Link to Transaction")
            selected_transaction = None
            if link_transaction and transactions:
                transaction_options = {f"{txn[0]} ({txn[1]})": txn[1] for txn in transactions}
                selected_transaction = st.selectbox("Transaction", options=list(transaction_options.keys()))
            
            status = st.radio("Status *", options=["due", "paid", "overdue"], horizontal=True)
            
            submitted = st.form_submit_button("✏️ Update Instance", type="secondary", width='stretch')
            
            if submitted:
                if not uid or not uid.strip():
                    st.error("❌ Instance UID is required")
                elif not selected_subscription:
                    st.error("❌ Please select a subscription")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                else:
                    subscription_uid = subscription_options[selected_subscription]
                    transaction_uid = transaction_options[selected_transaction] if selected_transaction else None
                    date_str = due_date.strftime('%Y-%m-%d')
                    
                    success, data = api_client.update_subscription_instance(
                        uid.strip(), subscription_uid, amount, date_str, transaction_uid, status
                    )
                    if success:
                        st.success(f"✅ Subscription instance updated")
                        load_subscription_instances()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update instance: {data}")

with tab4:
    st.subheader("Delete Subscription Instance")
    
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
                success, data = api_client.delete_subscription_instance(uid.strip())
                if success:
                    st.success("✅ Subscription instance deleted successfully")
                    load_subscription_instances()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete instance: {data}")

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Track individual subscription payments
    - Link instances to transactions when paid
    - Status: 'due' (upcoming), 'paid' (completed), 'overdue' (missed)
    - Automatically generated from subscription plans
    
    **Workflow:**
    1. Subscription instances are created based on subscription frequency
    2. Mark as 'paid' and link to transaction when payment is made
    3. System can auto-mark as 'overdue' if past due date
    """)

# Made with Bob
