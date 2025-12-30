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


def load_subscriptions():
    """Load subscriptions from API"""
    success, data = api_client.get_subscriptions()
    if success and data:
        st.session_state.subscriptions_data = pd.DataFrame(data)
        return st.session_state.subscriptions_data
    elif success:
        st.session_state.subscriptions_data = pd.DataFrame(columns=[
            "uid", "name", "amount", "frequency", "interval", "status"
        ])
        return st.session_state.subscriptions_data
    else:
        st.error(f"Failed to fetch subscriptions: {data}")
        return pd.DataFrame(columns=[
            "uid", "name", "amount", "frequency", "interval", "status"
        ])


# Create tabs for different operations
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 View All", "➕ Create", "✏️ Update", "🗑️ Delete", "📁 Import/Export"])

with tab1:
    st.subheader("All Subscriptions")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_subscriptions"):
            load_subscriptions()
            st.rerun()
    
    # Load and display subscriptions
    df = load_subscriptions()
    
    if not df.empty:
        # Color code by status
        def highlight_status(row):
            if row['status'] == 'active':
                return ['background-color: #90EE90; color: #000000'] * len(row)
            elif row['status'] == 'cancelled':
                return ['background-color: #FF6B6B; color: #000000'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            df.style.apply(highlight_status, axis=1),
            width='stretch',
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                "frequency": st.column_config.TextColumn("Frequency", width="small"),
                "interval": st.column_config.NumberColumn("Interval", width="small"),
                "status": st.column_config.TextColumn("Status", width="small"),
            }
        )
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Subscriptions", len(df))
        with col2:
            active_count = (df['status'] == 'active').sum() if 'status' in df.columns else 0
            st.metric("Active", active_count)
        with col3:
            total_amount = df[df['status'] == 'active']['amount'].sum() if 'status' in df.columns else 0
            st.metric("Total Active Amount", f"₹{total_amount:.2f}")
    else:
        st.info("No subscriptions found. Create your first subscription!")

with tab2:
    st.subheader("Create New Subscription")
    
    with st.form("create_subscription_form", clear_on_submit=True):
        name = st.text_input("Subscription Name *", placeholder="Enter subscription name")
        amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
        
        col1, col2 = st.columns(2)
        with col1:
            frequency = st.selectbox("Frequency *", options=["monthly", "yearly"])
        with col2:
            interval = st.number_input("Interval *", min_value=1, value=1, step=1)
        
        status = st.radio("Status *", options=["active", "cancelled"], horizontal=True)
        
        submitted = st.form_submit_button("➕ Create Subscription", type="primary", width='stretch')
        
        if submitted:
            if not name or not name.strip():
                st.error("❌ Subscription name is required")
            elif amount <= 0:
                st.error("❌ Amount must be greater than 0")
            elif interval < 1:
                st.error("❌ Interval must be at least 1")
            else:
                success, data = api_client.create_subscription(
                    name.strip(), amount, frequency, interval, status
                )
                if success:
                    st.success(f"✅ Subscription created: {data['name']}")
                    load_subscriptions()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create subscription: {data}")

with tab3:
    st.subheader("Update Subscription")
    
    with st.form("update_subscription_form"):
        uid = st.text_input("Subscription UID *", placeholder="Enter UID to update")
        name = st.text_input("New Name *", placeholder="Enter new name")
        amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
        
        col1, col2 = st.columns(2)
        with col1:
            frequency = st.selectbox("Frequency *", options=["monthly", "yearly"])
        with col2:
            interval = st.number_input("Interval *", min_value=1, value=1, step=1)
        
        status = st.radio("Status *", options=["active", "cancelled"], horizontal=True)
        
        submitted = st.form_submit_button("✏️ Update Subscription", type="secondary", width='stretch')
        
        if submitted:
            if not uid or not uid.strip():
                st.error("❌ Subscription UID is required")
            elif not name or not name.strip():
                st.error("❌ Name is required")
            elif amount <= 0:
                st.error("❌ Amount must be greater than 0")
            elif interval < 1:
                st.error("❌ Interval must be at least 1")
            else:
                success, data = api_client.update_subscription(
                    uid.strip(), name.strip(), amount, frequency, interval, status
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
            - `frequency`: monthly or yearly
            - `interval`: Integer >= 1
            - `status`: active or cancelled
            
            **Example:**
            ```
            name,amount,frequency,interval,status
            Netflix,999,monthly,1,active
            Amazon Prime,1499,yearly,1,active
            ```
            """)

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Manage recurring subscriptions
    - Set frequency (monthly, yearly) and interval
    - Change status to cancelled to pause without deleting
    - Track total monthly/yearly subscription costs
    
    **CSV Import/Export:**
    - Use Export to backup your subscriptions
    - Import CSV to bulk add subscriptions
    - Status must be 'active' or 'cancelled'
    """)
