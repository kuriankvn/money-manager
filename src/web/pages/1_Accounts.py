"""Accounts CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Accounts", page_icon="🏦", layout="wide")

st.title("🏦 Accounts Management")

# Initialize session state
if 'accounts_data' not in st.session_state:
    st.session_state.accounts_data = None


def load_accounts():
    """Load accounts from API"""
    success, data = api_client.get_accounts()
    if success and data:
        st.session_state.accounts_data = pd.DataFrame(data)
        return st.session_state.accounts_data
    elif success:
        st.session_state.accounts_data = pd.DataFrame(columns=["uid", "name"])
        return st.session_state.accounts_data
    else:
        st.error(f"Failed to fetch accounts: {data}")
        return pd.DataFrame(columns=["uid", "name"])


# Create tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View All", "➕ Create", "✏️ Update", "🗑️ Delete"])

with tab1:
    st.subheader("All Accounts")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_accounts"):
            load_accounts()
            st.rerun()
    
    # Load and display accounts
    df = load_accounts()
    
    if not df.empty:
        st.dataframe(
            df,
            width='stretch',
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="medium"),
                "name": st.column_config.TextColumn("Name", width="large"),
            }
        )
        st.info(f"Total accounts: {len(df)}")
    else:
        st.info("No accounts found. Create your first account!")

with tab2:
    st.subheader("Create New Account")
    
    with st.form("create_account_form", clear_on_submit=True):
        name = st.text_input("Name *", placeholder="Enter account name")
        
        submitted = st.form_submit_button("➕ Create Account", type="primary", width='stretch')
        
        if submitted:
            if not name or not name.strip():
                st.error("❌ Name is required")
            else:
                success, data = api_client.create_account(name.strip())
                if success:
                    st.success(f"✅ Account created: {data['name']}")
                    load_accounts()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create account: {data}")

with tab3:
    st.subheader("Update Account")
    
    with st.form("update_account_form"):
        uid = st.text_input("Account UID *", placeholder="Enter UID to update")
        name = st.text_input("New Name *", placeholder="Enter new name")
        
        submitted = st.form_submit_button("✏️ Update Account", type="secondary", width='stretch')
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Account UID is required")
            elif not name or not name.strip():
                st.error("❌ Name is required")
            else:
                success, data = api_client.update_account(uid.strip(), name.strip())
                if success:
                    st.success(f"✅ Account updated: {data['name']}")
                    load_accounts()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update account: {data}")

with tab4:
    st.subheader("Delete Account")
    
    st.warning("⚠️ Warning: Deleting an account will also delete all associated transactions!")
    
    with st.form("delete_account_form"):
        uid = st.text_input("Account UID *", placeholder="Enter UID to delete")
        
        confirm = st.checkbox("I understand this action cannot be undone")
        
        submitted = st.form_submit_button("🗑️ Delete Account", type="primary", width='stretch')
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Account UID is required")
            elif not confirm:
                st.error("❌ Please confirm deletion")
            else:
                success, data = api_client.delete_account(uid.strip())
                if success:
                    st.success("✅ Account deleted successfully")
                    load_accounts()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete account: {data}")

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Accounts represent your financial accounts (bank, wallet, credit card, etc.)
    - Each transaction is linked to an account
    - Account names should be unique and descriptive
    - Examples: "Checking Account", "Savings", "Credit Card", "Cash"
    """)
