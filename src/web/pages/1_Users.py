"""Users CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Users", page_icon="👤", layout="wide")

st.title("👤 Users Management")

# Initialize session state
if 'users_data' not in st.session_state:
    st.session_state.users_data = None


def load_users():
    """Load users from API"""
    success, data = api_client.get_users()
    if success and data:
        st.session_state.users_data = pd.DataFrame(data)
        return st.session_state.users_data
    elif success:
        st.session_state.users_data = pd.DataFrame(columns=["uid", "name"])
        return st.session_state.users_data
    else:
        st.error(f"Failed to fetch users: {data}")
        return pd.DataFrame(columns=["uid", "name"])


# Create tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View All", "➕ Create", "✏️ Update", "🗑️ Delete"])

with tab1:
    st.subheader("All Users")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_users"):
            load_users()
            st.rerun()
    
    # Load and display users
    df = load_users()
    
    if not df.empty:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="medium"),
                "name": st.column_config.TextColumn("Name", width="large"),
            }
        )
        st.info(f"Total users: {len(df)}")
    else:
        st.info("No users found. Create your first user!")

with tab2:
    st.subheader("Create New User")
    
    with st.form("create_user_form", clear_on_submit=True):
        name = st.text_input("Name *", placeholder="Enter user name")
        
        submitted = st.form_submit_button("➕ Create User", type="primary", use_container_width=True)
        
        if submitted:
            if not name or not name.strip():
                st.error("❌ Name is required")
            else:
                success, data = api_client.create_user(name.strip())
                if success:
                    st.success(f"✅ User created: {data['name']}")
                    load_users()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create user: {data}")

with tab3:
    st.subheader("Update User")
    
    with st.form("update_user_form"):
        uid = st.text_input("User UID *", placeholder="Enter UID to update")
        name = st.text_input("New Name *", placeholder="Enter new name")
        
        submitted = st.form_submit_button("✏️ Update User", type="secondary", use_container_width=True)
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ User UID is required")
            elif not name or not name.strip():
                st.error("❌ Name is required")
            else:
                success, data = api_client.update_user(uid.strip(), name.strip())
                if success:
                    st.success(f"✅ User updated: {data['name']}")
                    load_users()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update user: {data}")

with tab4:
    st.subheader("Delete User")
    
    st.warning("⚠️ Warning: Deleting a user will also delete all associated categories, transactions, and subscriptions!")
    
    with st.form("delete_user_form"):
        uid = st.text_input("User UID *", placeholder="Enter UID to delete")
        
        confirm = st.checkbox("I understand this action cannot be undone")
        
        submitted = st.form_submit_button("🗑️ Delete User", type="primary", use_container_width=True)
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ User UID is required")
            elif not confirm:
                st.error("❌ Please confirm deletion")
            else:
                success, data = api_client.delete_user(uid.strip())
                if success:
                    st.success("✅ User deleted successfully")
                    load_users()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete user: {data}")

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Copy UID from the table for update/delete
    - All fields marked with * are required
    - Names should be unique and descriptive
    """)
