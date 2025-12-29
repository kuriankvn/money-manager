"""Transactions CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Transactions", page_icon="💳", layout="wide")

st.title("💳 Transactions Management")

# Initialize session state
if 'transactions_data' not in st.session_state:
    st.session_state.transactions_data = None
if 'users_list' not in st.session_state:
    st.session_state.users_list = []
if 'categories_list' not in st.session_state:
    st.session_state.categories_list = []


def load_transactions():
    """Load transactions from API"""
    success, data = api_client.get_transactions()
    if success and data:
        df = pd.DataFrame(data)
        # Convert timestamp to readable format
        if 'datetime' in df.columns:
            df['datetime'] = df['datetime'].apply(
                lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
            )
        st.session_state.transactions_data = df
        return df
    elif success:
        st.session_state.transactions_data = pd.DataFrame(columns=[
            "uid", "name", "amount", "datetime", "type",
            "user_uid", "user_name", "category_uid", "category_name"
        ])
        return st.session_state.transactions_data
    else:
        st.error(f"Failed to fetch transactions: {data}")
        return pd.DataFrame(columns=[
            "uid", "name", "amount", "datetime", "type",
            "user_uid", "user_name", "category_uid", "category_name"
        ])


def load_users():
    """Load users for dropdown"""
    success, data = api_client.get_users()
    if success and data:
        st.session_state.users_list = [(user['name'], user['uid']) for user in data]
    else:
        st.session_state.users_list = []
    return st.session_state.users_list


def load_categories():
    """Load categories for dropdown"""
    success, data = api_client.get_categories()
    if success and data:
        st.session_state.categories_list = [(cat['name'], cat['uid']) for cat in data]
    else:
        st.session_state.categories_list = []
    return st.session_state.categories_list


# Create tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View All", "➕ Create", "✏️ Update", "🗑️ Delete"])

with tab1:
    st.subheader("All Transactions")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_transactions"):
            load_transactions()
            load_users()
            load_categories()
            st.rerun()
    
    # Load and display transactions
    df = load_transactions()
    
    if not df.empty:
        # Color code by type
        def highlight_type(row):
            if row['type'] == 'income':
                return ['background-color: #d4edda'] * len(row)
            elif row['type'] == 'expense':
                return ['background-color: #f8d7da'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            df.style.apply(highlight_type, axis=1),
            use_container_width=True,
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                "datetime": st.column_config.TextColumn("Date/Time", width="medium"),
                "type": st.column_config.TextColumn("Type", width="small"),
                "user_name": st.column_config.TextColumn("User", width="small"),
                "category_name": st.column_config.TextColumn("Category", width="small"),
            }
        )
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Transactions", len(df))
        with col2:
            income = df[df['type'] == 'income']['amount'].sum() if 'income' in df['type'].values else 0
            st.metric("Total Income", f"${income:.2f}")
        with col3:
            expense = df[df['type'] == 'expense']['amount'].sum() if 'expense' in df['type'].values else 0
            st.metric("Total Expenses", f"${expense:.2f}")
    else:
        st.info("No transactions found. Create your first transaction!")

with tab2:
    st.subheader("Create New Transaction")
    
    # Load users and categories
    users = load_users()
    categories = load_categories()
    
    if not users:
        st.warning("⚠️ No users found. Please create a user first!")
    elif not categories:
        st.warning("⚠️ No categories found. Please create a category first!")
    else:
        with st.form("create_transaction_form", clear_on_submit=True):
            name = st.text_input("Transaction Name *", placeholder="Enter transaction name")
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            transaction_type = st.radio("Type *", options=["income", "expense"], horizontal=True)
            
            user_options = {f"{user[0]} ({user[1]})": user[1] for user in users}
            selected_user = st.selectbox("User *", options=list(user_options.keys()))
            
            category_options = {f"{cat[0]} ({cat[1]})": cat[1] for cat in categories}
            selected_category = st.selectbox("Category *", options=list(category_options.keys()))
            
            submitted = st.form_submit_button("➕ Create Transaction", type="primary", use_container_width=True)
            
            if submitted:
                if not name or not name.strip():
                    st.error("❌ Transaction name is required")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                elif not selected_user:
                    st.error("❌ Please select a user")
                elif not selected_category:
                    st.error("❌ Please select a category")
                else:
                    user_uid = user_options[selected_user]
                    category_uid = category_options[selected_category]
                    timestamp = datetime.now().timestamp()
                    
                    success, data = api_client.create_transaction(
                        name.strip(), amount, timestamp, transaction_type, user_uid, category_uid
                    )
                    if success:
                        st.success(f"✅ Transaction created: {data['name']}")
                        load_transactions()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create transaction: {data}")

with tab3:
    st.subheader("Update Transaction")
    
    # Load users and categories
    users = load_users()
    categories = load_categories()
    
    if not users:
        st.warning("⚠️ No users found. Please create a user first!")
    elif not categories:
        st.warning("⚠️ No categories found. Please create a category first!")
    else:
        with st.form("update_transaction_form"):
            uid = st.text_input("Transaction UID *", placeholder="Enter UID to update")
            name = st.text_input("New Name *", placeholder="Enter new name")
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            transaction_type = st.radio("Type *", options=["income", "expense"], horizontal=True)
            
            user_options = {f"{user[0]} ({user[1]})": user[1] for user in users}
            selected_user = st.selectbox("User *", options=list(user_options.keys()))
            
            category_options = {f"{cat[0]} ({cat[1]})": cat[1] for cat in categories}
            selected_category = st.selectbox("Category *", options=list(category_options.keys()))
            
            submitted = st.form_submit_button("✏️ Update Transaction", type="secondary", use_container_width=True)
            
            if submitted:
                if not uid or not uid.strip():
                    st.error("❌ Transaction UID is required")
                elif not name or not name.strip():
                    st.error("❌ Name is required")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                elif not selected_user:
                    st.error("❌ Please select a user")
                elif not selected_category:
                    st.error("❌ Please select a category")
                else:
                    user_uid = user_options[selected_user]
                    category_uid = category_options[selected_category]
                    timestamp = datetime.now().timestamp()
                    
                    success, data = api_client.update_transaction(
                        uid.strip(), name.strip(), amount, timestamp, transaction_type, user_uid, category_uid
                    )
                    if success:
                        st.success(f"✅ Transaction updated: {data['name']}")
                        load_transactions()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update transaction: {data}")

with tab4:
    st.subheader("Delete Transaction")
    
    with st.form("delete_transaction_form"):
        uid = st.text_input("Transaction UID *", placeholder="Enter UID to delete")
        
        confirm = st.checkbox("I understand this action cannot be undone")
        
        submitted = st.form_submit_button("🗑️ Delete Transaction", type="primary", use_container_width=True)
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Transaction UID is required")
            elif not confirm:
                st.error("❌ Please confirm deletion")
            else:
                success, data = api_client.delete_transaction(uid.strip())
                if success:
                    st.success("✅ Transaction deleted successfully")
                    load_transactions()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete transaction: {data}")

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    - 🟢 Income transactions are highlighted in green
    - 🔴 Expense transactions are highlighted in red
    - Timestamps are automatically set to current time
    - Copy UID from the table for update/delete
    - All fields marked with * are required
    """)
