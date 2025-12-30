"""Subscriptions CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Subscriptions", page_icon="🔄", layout="wide")

st.title("🔄 Subscriptions Management")

# Initialize session state
if 'subscriptions_data' not in st.session_state:
    st.session_state.subscriptions_data = None
if 'users_list' not in st.session_state:
    st.session_state.users_list = []
if 'categories_list' not in st.session_state:
    st.session_state.categories_list = []


def load_subscriptions():
    """Load subscriptions from API"""
    success, data = api_client.get_subscriptions()
    if success and data:
        st.session_state.subscriptions_data = pd.DataFrame(data)
        return st.session_state.subscriptions_data
    elif success:
        st.session_state.subscriptions_data = pd.DataFrame(columns=[
            "uid", "name", "amount", "interval", "multiplier",
            "user_uid", "user_name", "category_uid", "category_name", "active"
        ])
        return st.session_state.subscriptions_data
    else:
        st.error(f"Failed to fetch subscriptions: {data}")
        return pd.DataFrame(columns=[
            "uid", "name", "amount", "interval", "multiplier",
            "user_uid", "user_name", "category_uid", "category_name", "active"
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 View All", "➕ Create", "✏️ Update", "🗑️ Delete", "📁 Import/Export"])

with tab1:
    st.subheader("All Subscriptions")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_subscriptions"):
            load_subscriptions()
            load_users()
            load_categories()
            st.rerun()
    
    # Load and display subscriptions
    df = load_subscriptions()
    
    if not df.empty:
        # Color code by active status
        def highlight_active(row):
            if row['active']:
                return ['background-color: #90EE90; color: #000000'] * len(row)
            else:
                return ['background-color: #FF6B6B; color: #000000'] * len(row)
        
        # Hide UUID columns, show only names
        display_columns = ["uid", "name", "amount", "interval", "multiplier", "user_name", "category_name", "active"]
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        st.dataframe(
            display_df.style.apply(highlight_active, axis=1),
            width='stretch',
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                "interval": st.column_config.TextColumn("Interval", width="small"),
                "multiplier": st.column_config.NumberColumn("Multiplier", width="small"),
                "user_name": st.column_config.TextColumn("User", width="medium"),
                "category_name": st.column_config.TextColumn("Category", width="medium"),
                "active": st.column_config.CheckboxColumn("Active", width="small"),
            }
        )
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Subscriptions", len(df))
        with col2:
            active_count = df['active'].sum() if 'active' in df.columns else 0
            st.metric("Active", active_count)
        with col3:
            total_amount = df[df['active']]['amount'].sum() if 'active' in df.columns else 0
            st.metric("Total Active Amount", f"₹{total_amount:.2f}")
    else:
        st.info("No subscriptions found. Create your first subscription!")

with tab2:
    st.subheader("Create New Subscription")
    
    # Load users and categories
    users = load_users()
    categories = load_categories()
    
    if not users:
        st.warning("⚠️ No users found. Please create a user first!")
    elif not categories:
        st.warning("⚠️ No categories found. Please create a category first!")
    else:
        with st.form("create_subscription_form", clear_on_submit=True):
            name = st.text_input("Subscription Name *", placeholder="Enter subscription name")
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            
            col1, col2 = st.columns(2)
            with col1:
                interval = st.selectbox("Interval *", options=["monthly", "yearly"])
            with col2:
                multiplier = st.number_input("Multiplier *", min_value=1, value=1, step=1)
            
            user_options = {f"{user[0]} ({user[1]})": user[1] for user in users}
            selected_user = st.selectbox("User *", options=list(user_options.keys()))
            
            category_options = {f"{cat[0]} ({cat[1]})": cat[1] for cat in categories}
            selected_category = st.selectbox("Category *", options=list(category_options.keys()))
            
            active = st.checkbox("Active", value=True)
            
            submitted = st.form_submit_button("➕ Create Subscription", type="primary", width='stretch')
            
            if submitted:
                if not name or not name.strip():
                    st.error("❌ Subscription name is required")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                elif multiplier < 1:
                    st.error("❌ Multiplier must be at least 1")
                elif not selected_user:
                    st.error("❌ Please select a user")
                elif not selected_category:
                    st.error("❌ Please select a category")
                else:
                    user_uid = user_options[selected_user]
                    category_uid = category_options[selected_category]
                    
                    success, data = api_client.create_subscription(
                        name.strip(), amount, interval, multiplier, user_uid, category_uid, active
                    )
                    if success:
                        st.success(f"✅ Subscription created: {data['name']}")
                        load_subscriptions()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create subscription: {data}")

with tab3:
    st.subheader("Update Subscription")
    
    # Load users and categories
    users = load_users()
    categories = load_categories()
    
    if not users:
        st.warning("⚠️ No users found. Please create a user first!")
    elif not categories:
        st.warning("⚠️ No categories found. Please create a category first!")
    else:
        with st.form("update_subscription_form"):
            uid = st.text_input("Subscription UID *", placeholder="Enter UID to update")
            name = st.text_input("New Name *", placeholder="Enter new name")
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            
            col1, col2 = st.columns(2)
            with col1:
                interval = st.selectbox("Interval *", options=["monthly", "yearly"])
            with col2:
                multiplier = st.number_input("Multiplier *", min_value=1, value=1, step=1)
            
            user_options = {f"{user[0]} ({user[1]})": user[1] for user in users}
            selected_user = st.selectbox("User *", options=list(user_options.keys()))
            
            category_options = {f"{cat[0]} ({cat[1]})": cat[1] for cat in categories}
            selected_category = st.selectbox("Category *", options=list(category_options.keys()))
            
            active = st.checkbox("Active", value=True)
            
            submitted = st.form_submit_button("✏️ Update Subscription", type="secondary", width='stretch')
            
            if submitted:
                if not uid or not uid.strip():
                    st.error("❌ Subscription UID is required")
                elif not name or not name.strip():
                    st.error("❌ Name is required")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                elif multiplier < 1:
                    st.error("❌ Multiplier must be at least 1")
                elif not selected_user:
                    st.error("❌ Please select a user")
                elif not selected_category:
                    st.error("❌ Please select a category")
                else:
                    user_uid = user_options[selected_user]
                    category_uid = category_options[selected_category]
                    
                    success, data = api_client.update_subscription(
                        uid.strip(), name.strip(), amount, interval, multiplier, user_uid, category_uid, active
                    )
                    if success:
                        st.success(f"✅ Subscription updated: {data['name']}")
                        load_subscriptions()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update subscription: {data}")

with tab4:
    st.subheader("Delete Subscription")
    
    with st.form("delete_subscription_form"):
        uid = st.text_input("Subscription UID *", placeholder="Enter UID to delete")
        
        confirm = st.checkbox("I understand this action cannot be undone")
        
        submitted = st.form_submit_button("🗑️ Delete Subscription", type="primary", width='stretch')
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Subscription UID is required")
            elif not confirm:
                st.error("❌ Please confirm deletion")
            else:
                success, data = api_client.delete_subscription(uid.strip())
                if success:
                    st.success("✅ Subscription deleted successfully")
                    load_subscriptions()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete subscription: {data}")

with tab5:
    st.subheader("Import/Export CSV")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Export")
        st.markdown("Download all subscriptions as CSV file")
        
        if st.button("📥 Download CSV", type="primary", use_container_width=True):
            success, data = api_client.export_subscriptions_csv()
            if success:
                st.download_button(
                    label="💾 Save File",
                    data=data,
                    file_name="subscriptions.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success("✅ CSV ready for download")
            else:
                st.error(f"❌ Export failed: {data}")
    
    with col2:
        st.markdown("### 📥 Import")
        st.markdown("Upload CSV file to import subscriptions")
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], key="import_subscriptions")
        
        if uploaded_file is not None:
            try:
                csv_content = uploaded_file.read().decode('utf-8')
                
                if st.button("📤 Import CSV", type="primary", use_container_width=True):
                    success, data = api_client.import_subscriptions_csv(csv_content)
                    if success:
                        st.success(f"✅ Import completed!")
                        st.json(data)
                        if data.get('errors'):
                            st.warning("⚠️ Some rows had errors:")
                            for error in data['errors']:
                                st.text(f"- {error}")
                        load_subscriptions()
                    else:
                        st.error(f"❌ Import failed: {data}")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
        
        with st.expander("📋 CSV Format Guide"):
            st.markdown("""
            **Required columns:**
            - `name`: Subscription name
            - `amount`: Amount (positive number)
            - `interval`: monthly or yearly
            - `multiplier`: Integer >= 1 (optional, defaults to 1)
            - `user`: User name (must exist)
            - `category`: Category name (must exist)
            - `active`: true/false (optional, defaults to true)
            
            **Example:**
            ```
            name,amount,interval,multiplier,user,category,active
            Netflix,999,monthly,1,John Doe,Entertainment,true
            Amazon Prime,1499,yearly,1,John Doe,Entertainment,true
            ```
            """)

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Manage recurring payments and subscriptions
    - Set interval (daily, weekly, monthly, yearly) and multiplier
    - Toggle active status to pause without deleting
    - Track total monthly/yearly subscription costs
    
    **CSV Import/Export:**
    - Use Export to backup your subscriptions
    - Import CSV to bulk add subscriptions
    - Ensure user and category names exist before importing
    - User and category names are case-sensitive
    """)
