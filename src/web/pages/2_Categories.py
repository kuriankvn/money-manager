"""Categories CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Categories", page_icon="📁", layout="wide")

st.title("📁 Categories Management")

# Initialize session state
if 'categories_data' not in st.session_state:
    st.session_state.categories_data = None
if 'users_list' not in st.session_state:
    st.session_state.users_list = []


def load_categories():
    """Load categories from API"""
    success, data = api_client.get_categories()
    if success and data:
        st.session_state.categories_data = pd.DataFrame(data)
        return st.session_state.categories_data
    elif success:
        st.session_state.categories_data = pd.DataFrame(columns=["uid", "name", "user_uid", "user_name"])
        return st.session_state.categories_data
    else:
        st.error(f"Failed to fetch categories: {data}")
        return pd.DataFrame(columns=["uid", "name", "user_uid", "user_name"])


def load_users():
    """Load users for dropdown"""
    success, data = api_client.get_users()
    if success and data:
        st.session_state.users_list = [(user['name'], user['uid']) for user in data]
    else:
        st.session_state.users_list = []
    return st.session_state.users_list


# Create tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View All", "➕ Create", "✏️ Update", "🗑️ Delete"])

with tab1:
    st.subheader("All Categories")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_categories"):
            load_categories()
            load_users()
            st.rerun()
    
    # Load and display categories
    df = load_categories()
    
    if not df.empty:
        # Hide UUID column, show only names
        display_columns = ["uid", "name", "user_name"]
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "user_name": st.column_config.TextColumn("User", width="medium"),
            }
        )
        st.info(f"Total categories: {len(df)}")
    else:
        st.info("No categories found. Create your first category!")

with tab2:
    st.subheader("Create New Category")
    
    # Load users for dropdown
    users = load_users()
    
    if not users:
        st.warning("⚠️ No users found. Please create a user first!")
    else:
        with st.form("create_category_form", clear_on_submit=True):
            name = st.text_input("Category Name *", placeholder="Enter category name")
            
            user_options = {f"{user[0]} ({user[1]})": user[1] for user in users}
            selected_user = st.selectbox("User *", options=list(user_options.keys()))
            
            submitted = st.form_submit_button("➕ Create Category", type="primary", width='stretch')
            
            if submitted:
                if not name or not name.strip():
                    st.error("❌ Category name is required")
                elif not selected_user:
                    st.error("❌ Please select a user")
                else:
                    user_uid = user_options[selected_user]
                    success, data = api_client.create_category(name.strip(), user_uid)
                    if success:
                        st.success(f"✅ Category created: {data['name']}")
                        load_categories()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create category: {data}")

with tab3:
    st.subheader("Update Category")
    
    # Load users for dropdown
    users = load_users()
    
    if not users:
        st.warning("⚠️ No users found. Please create a user first!")
    else:
        with st.form("update_category_form"):
            uid = st.text_input("Category UID *", placeholder="Enter UID to update")
            name = st.text_input("New Name *", placeholder="Enter new name")
            
            user_options = {f"{user[0]} ({user[1]})": user[1] for user in users}
            selected_user = st.selectbox("User *", options=list(user_options.keys()))
            
            submitted = st.form_submit_button("✏️ Update Category", type="secondary", width='stretch')
            
            if submitted:
                if not uid or not uid.strip():
                    st.error("❌ Category UID is required")
                elif not name or not name.strip():
                    st.error("❌ Name is required")
                elif not selected_user:
                    st.error("❌ Please select a user")
                else:
                    user_uid = user_options[selected_user]
                    success, data = api_client.update_category(uid.strip(), name.strip(), user_uid)
                    if success:
                        st.success(f"✅ Category updated: {data['name']}")
                        load_categories()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update category: {data}")

with tab4:
    st.subheader("Delete Category")
    
    st.warning("⚠️ Warning: Deleting a category will also delete all associated transactions and subscriptions!")
    
    with st.form("delete_category_form"):
        uid = st.text_input("Category UID *", placeholder="Enter UID to delete")
        
        confirm = st.checkbox("I understand this action cannot be undone")
        
        submitted = st.form_submit_button("🗑️ Delete Category", type="primary", width='stretch')
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Category UID is required")
            elif not confirm:
                st.error("❌ Please confirm deletion")
            else:
                success, data = api_client.delete_category(uid.strip())
                if success:
                    st.success("✅ Category deleted successfully")
                    load_categories()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete category: {data}")

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    - TODO
    """)
