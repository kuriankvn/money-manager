"""Subscriptions CRUD interface with import/export"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.web import api_client


st.set_page_config(page_title="Subscriptions", page_icon="🔄", layout="wide")

st.title("🔄 Subscriptions Management")

if 'subscriptions_data' not in st.session_state:
    st.session_state.subscriptions_data = None
if 'instances_data' not in st.session_state:
    st.session_state.instances_data = None


def load_subscriptions():
    """Load subscriptions from API"""
    success, data = api_client.get_subscriptions()
    if success and data:
        st.session_state.subscriptions_data = pd.DataFrame(data)
        return st.session_state.subscriptions_data
    elif success:
        st.session_state.subscriptions_data = pd.DataFrame(columns=[
            "id", "name", "type", "frequency", "due_day", "expected_amount",
            "start_date", "end_date", "notes"
        ])
        return st.session_state.subscriptions_data
    else:
        st.error(f"Failed to fetch subscriptions: {data}")
        return pd.DataFrame()


def load_due_instances():
    """Load due subscription instances"""
    success, data = api_client.get_due_instances()
    if success and data:
        st.session_state.instances_data = pd.DataFrame(data)
        return st.session_state.instances_data
    elif success:
        st.session_state.instances_data = pd.DataFrame(columns=[
            "id", "subscription_id", "period", "due_date", "amount", "status", "paid_date"
        ])
        return st.session_state.instances_data
    else:
        st.error(f"Failed to fetch instances: {data}")
        return pd.DataFrame()


tab1, tab2, tab3, tab4 = st.tabs(["📋 View All", "➕ Create", "💰 Due Payments", "📁 Import/Export"])

with tab1:
    st.subheader("All Subscriptions")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_subscriptions"):
            load_subscriptions()
            st.rerun()
    
    df = load_subscriptions()
    
    if not df.empty:
        def highlight_active(row):
            if pd.notna(row.get('end_date')) and row['end_date'] < str(date.today()):
                return ['background-color: #FF6B6B; color: #000000'] * len(row)
            else:
                return ['background-color: #90EE90; color: #000000'] * len(row)
        
        display_columns = ["id", "name", "type", "frequency", "due_day", "expected_amount", "start_date", "end_date"]
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        st.dataframe(
            display_df.style.apply(highlight_active, axis=1),
            width='stretch',
            hide_index=True,
            column_config={
                "id": st.column_config.TextColumn("ID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "type": st.column_config.TextColumn("Type", width="small"),
                "frequency": st.column_config.TextColumn("Frequency", width="small"),
                "due_day": st.column_config.NumberColumn("Due Day", width="small"),
                "expected_amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                "start_date": st.column_config.TextColumn("Start Date", width="medium"),
                "end_date": st.column_config.TextColumn("End Date", width="medium"),
            }
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Subscriptions", len(df))
        with col2:
            active_count = len(df[df['end_date'].isna() | (df['end_date'] >= str(date.today()))])
            st.metric("Active", active_count)
        with col3:
            total_amount = df['expected_amount'].sum()
            st.metric("Total Expected", f"₹{total_amount:.2f}")
    else:
        st.info("No subscriptions found. Create your first subscription!")

with tab2:
    st.subheader("Create New Subscription")
    
    with st.form("create_subscription_form", clear_on_submit=True):
        name = st.text_input("Subscription Name *", placeholder="e.g., Netflix")
        
        col1, col2 = st.columns(2)
        with col1:
            sub_type = st.selectbox("Type *", options=["EXPENSE", "INCOME"])
        with col2:
            frequency = st.selectbox("Frequency *", options=["MONTHLY", "YEARLY"])
        
        col1, col2 = st.columns(2)
        with col1:
            due_day = st.number_input("Due Day *", min_value=1, max_value=31, value=1)
        with col2:
            expected_amount = st.number_input("Expected Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date *", value=date.today())
        with col2:
            end_date = st.date_input("End Date (Optional)", value=None)
        
        notes = st.text_area("Notes", height=100)
        generate_instances = st.checkbox("Generate payment instances", value=True)
        
        submitted = st.form_submit_button("➕ Create Subscription", type="primary", use_container_width=True)
        
        if submitted:
            if not name or not name.strip():
                st.error("❌ Subscription name is required")
            elif expected_amount <= 0:
                st.error("❌ Amount must be greater than 0")
            else:
                success, data = api_client.create_subscription(
                    name=name.strip(),
                    sub_type=sub_type,
                    frequency=frequency,
                    due_day=int(due_day),
                    expected_amount=float(expected_amount),
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat() if end_date else None,
                    notes=notes.strip() if notes else None,
                    generate_instances=generate_instances
                )
                if success:
                    st.success(f"✅ Subscription created: {data['name']}")
                    load_subscriptions()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create subscription: {data}")

with tab3:
    st.subheader("Due Payments")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_instances"):
            load_due_instances()
            st.rerun()
    
    inst_df = load_due_instances()
    
    if not inst_df.empty:
        def highlight_status(row):
            if row['status'] == 'PAID':
                return ['background-color: #90EE90; color: #000000'] * len(row)
            elif row['status'] == 'OVERDUE':
                return ['background-color: #FF6B6B; color: #000000'] * len(row)
            else:
                return ['background-color: #FFD700; color: #000000'] * len(row)
        
        display_columns = ["id", "subscription_id", "period", "due_date", "amount", "status", "paid_date"]
        display_df = inst_df[display_columns] if all(col in inst_df.columns for col in display_columns) else inst_df
        
        st.dataframe(
            display_df.style.apply(highlight_status, axis=1),
            width='stretch',
            hide_index=True,
            column_config={
                "id": st.column_config.TextColumn("ID", width="small"),
                "subscription_id": st.column_config.TextColumn("Subscription", width="medium"),
                "period": st.column_config.TextColumn("Period", width="medium"),
                "due_date": st.column_config.TextColumn("Due Date", width="medium"),
                "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "paid_date": st.column_config.TextColumn("Paid Date", width="medium"),
            }
        )
        
        st.markdown("---")
        st.subheader("Mark Payment as Paid")
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            instance_id = st.text_input("Instance ID", placeholder="Enter ID to mark as paid")
        with col2:
            paid_date = st.date_input("Paid Date", value=date.today())
        with col3:
            actual_amount = st.number_input("Actual Amount (Optional)", min_value=0.0, value=0.0, step=0.01)
        with col4:
            st.write("")
            st.write("")
            if st.button("✅ Mark Paid", type="primary", use_container_width=True):
                if instance_id:
                    success, data = api_client.mark_instance_paid(
                        instance_id=instance_id,
                        paid_date=paid_date.isoformat(),
                        actual_amount=float(actual_amount) if actual_amount > 0 else None
                    )
                    if success:
                        st.success("✅ Payment marked as paid!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed: {data}")
                else:
                    st.error("❌ Please enter an instance ID")
    else:
        st.info("No due payments found.")

with tab4:
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
            - `type`: EXPENSE or INCOME
            - `frequency`: MONTHLY or YEARLY
            - `due_day`: Day of month (1-31)
            - `expected_amount`: Amount (positive number)
            - `start_date`: Date in YYYY-MM-DD format
            - `end_date`: Date in YYYY-MM-DD format (optional)
            - `notes`: Additional notes (optional)
            
            **Example:**
            ```
            name,type,frequency,due_day,expected_amount,start_date,end_date,notes
            Netflix,EXPENSE,MONTHLY,15,999,2024-01-01,,Streaming service
            Salary,INCOME,MONTHLY,1,50000,2024-01-01,,Monthly salary
            ```
            """)

with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Manage recurring payments and income
    - Set frequency (MONTHLY, YEARLY) and due day
    - System auto-generates payment instances
    - Track payment status (DUE, PAID, OVERDUE)
    
    **CSV Import/Export:**
    - Use Export to backup your subscriptions
    - Import CSV to bulk add subscriptions
    - Date format must be YYYY-MM-DD
    - Type must be EXPENSE or INCOME
    - Frequency must be MONTHLY or YEARLY
    """)

# Made with Bob
