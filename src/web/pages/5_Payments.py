"""Payments interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Payments", page_icon="💰", layout="wide")

st.title("💰 Payments")

# Initialize session state
if 'payments_data' not in st.session_state:
    st.session_state.payments_data = None
if 'users_list' not in st.session_state:
    st.session_state.users_list = []

# Get current month and year
current_date = datetime.now()
current_month = current_date.month
current_year = current_date.year


def load_users():
    """Load users for dropdown"""
    success, data = api_client.get_users()
    if success and data:
        st.session_state.users_list = [(user['name'], user['uid']) for user in data]
    else:
        st.session_state.users_list = []
    return st.session_state.users_list


def load_payments(month: int, year: int, user_uid: str | None = None):
    """Load payments from API"""
    success, data = api_client.get_payments(month=month, year=year, user_uid=user_uid)
    if success and data:
        return pd.DataFrame(data)
    elif success:
        return pd.DataFrame(columns=[
            "uid", "amount", "due_date", "user_uid", "user_name",
            "subscription_uid", "subscription_name", "paid_date", "paid"
        ])
    else:
        st.error(f"Failed to fetch payments: {data}")
        return pd.DataFrame(columns=[
            "uid", "amount", "due_date", "user_uid", "user_name",
            "subscription_uid", "subscription_name", "paid_date", "paid"
        ])


def load_statistics(month: int, year: int, user_uid: str | None = None):
    """Load payment statistics"""
    success, data = api_client.get_payment_statistics(month=month, year=year, user_uid=user_uid)
    if success:
        return data
    else:
        return {
            "total_due": 0,
            "total_paid": 0,
            "total_pending": 0,
            "paid_count": 0,
            "pending_count": 0,
            "overdue_count": 0,
            "total_count": 0
        }


# Sidebar for filters
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    # Load users
    users = load_users()
    
    # User filter
    user_options = {"All Users": None}
    if users:
        user_options.update({f"{user[0]}": user[1] for user in users})
    selected_user_name = st.selectbox("Filter by User", options=list(user_options.keys()))
    selected_user_uid = user_options[selected_user_name]
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Generate payments at the start of each month
    - Mark payments as paid when completed
    - View payment history for any past month
    - Green = Paid, Yellow = Pending, Red = Overdue
    """)


# Create tabs
tab1, tab2 = st.tabs(["📅 Current Month", "📜 Payment History"])

with tab1:
    st.subheader(f"Payments for {current_date.strftime('%B %Y')}")
    
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_current"):
            st.rerun()
    
    # Generate payments button
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        if st.button("🔔 Generate Payments", type="primary", use_container_width=True):
            with st.spinner("Generating payments..."):
                success, data = api_client.generate_payments(
                    month=current_month,
                    year=current_year,
                    user_uid=selected_user_uid
                )
                if success:
                    msg = f"✅ Generated {data.get('created', 0)} payments"
                    if data.get('skipped', 0) > 0:
                        msg += f" (Skipped {data.get('skipped', 0)} existing)"
                    if data.get('skipped_interval', 0) > 0:
                        msg += f" (Skipped {data.get('skipped_interval', 0)} yearly subscriptions - only generate in January)"
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(f"❌ Failed to generate payments: {data}")
    
    # Load statistics
    stats = load_statistics(current_month, current_year, selected_user_uid)
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Due", f"₹{stats['total_due']:.2f}")
    with col2:
        st.metric("Paid", f"{stats['paid_count']} (₹{stats['total_paid']:.2f})")
    with col3:
        st.metric("Pending", f"{stats['pending_count']} (₹{stats['total_pending']:.2f})")
    with col4:
        st.metric("Overdue", stats['overdue_count'], delta=None if stats['overdue_count'] == 0 else "⚠️")
    
    st.markdown("---")
    
    # Load and display payments
    df = load_payments(current_month, current_year, selected_user_uid)
    
    if not df.empty:
        # Convert due_date and paid_date to datetime
        df['due_date'] = pd.to_datetime(df['due_date'])
        if 'paid_date' in df.columns:
            df['paid_date'] = pd.to_datetime(df['paid_date'], errors='coerce')
        
        # Add status column for display
        now = datetime.now()
        df['status'] = df.apply(
            lambda row: 'Paid' if row['paid'] else ('Overdue' if row['due_date'] < now else 'Pending'),
            axis=1
        )
        
        # Color code by status
        def highlight_status(row):
            if row['status'] == 'Paid':
                return ['background-color: #90EE90; color: #000000'] * len(row)
            elif row['status'] == 'Overdue':
                return ['background-color: #FF6B6B; color: #000000'] * len(row)
            else:
                return ['background-color: #FFD700; color: #000000'] * len(row)
        
        # Display columns
        display_columns = ["subscription_name", "user_name", "amount", "due_date", "status", "paid_date", "uid"]
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        st.dataframe(
            display_df.style.apply(highlight_status, axis=1),
            width='stretch',
            hide_index=True,
            column_config={
                "subscription_name": st.column_config.TextColumn("Subscription", width="medium"),
                "user_name": st.column_config.TextColumn("User", width="medium"),
                "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                "due_date": st.column_config.DatetimeColumn("Due Date", format="DD MMM YYYY"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "paid_date": st.column_config.DatetimeColumn("Paid Date", format="DD MMM YYYY"),
                "uid": st.column_config.TextColumn("UID", width="small"),
            }
        )
        
        # Mark as paid section
        st.markdown("---")
        st.subheader("Mark Payment as Paid")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            payment_uid = st.text_input("Payment UID", placeholder="Enter UID to mark as paid")
        with col2:
            paid_date = st.date_input("Paid Date", value=datetime.now())
        with col3:
            st.write("")
            st.write("")
            if st.button("✅ Mark Paid", type="primary", use_container_width=True):
                if payment_uid:
                    success, data = api_client.mark_payment_as_paid(
                        uid=payment_uid,
                        paid_date=paid_date.isoformat()
                    )
                    if success:
                        st.success("✅ Payment marked as paid!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed: {data}")
                else:
                    st.error("❌ Please enter a payment UID")
    else:
        st.info("No payments found for this month. Click 'Generate Payments' to create them.")

with tab2:
    st.subheader("Payment History")
    
    # Month/Year selector
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        history_month = st.selectbox(
            "Month",
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime('%B'),
            index=current_month - 1
        )
    with col2:
        history_year = st.selectbox(
            "Year",
            options=list(range(2020, current_year + 2)),
            index=list(range(2020, current_year + 2)).index(current_year)
        )
    with col3:
        st.write("")
        st.write("")
        if st.button("🔍 Load History", type="primary", use_container_width=True):
            st.rerun()
    
    # Load statistics for selected month
    hist_stats = load_statistics(history_month, history_year, selected_user_uid)
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Due", f"₹{hist_stats['total_due']:.2f}")
    with col2:
        st.metric("Paid", f"{hist_stats['paid_count']} (₹{hist_stats['total_paid']:.2f})")
    with col3:
        st.metric("Pending", f"{hist_stats['pending_count']} (₹{hist_stats['total_pending']:.2f})")
    with col4:
        st.metric("Total Payments", hist_stats['total_count'])
    
    st.markdown("---")
    
    # Load and display historical payments
    hist_df = load_payments(history_month, history_year, selected_user_uid)
    
    if not hist_df.empty:
        # Convert dates
        hist_df['due_date'] = pd.to_datetime(hist_df['due_date'])
        if 'paid_date' in hist_df.columns:
            hist_df['paid_date'] = pd.to_datetime(hist_df['paid_date'], errors='coerce')
        
        # Add status column
        hist_df['status'] = hist_df['paid'].apply(lambda x: 'Paid' if x else 'Pending')
        
        # Color code
        def highlight_status_hist(row):
            if row['status'] == 'Paid':
                return ['background-color: #90EE90; color: #000000'] * len(row)
            else:
                return ['background-color: #FFD700; color: #000000'] * len(row)
        
        # Display columns
        display_columns = ["subscription_name", "user_name", "amount", "due_date", "status", "paid_date"]
        display_df = hist_df[display_columns] if all(col in hist_df.columns for col in display_columns) else hist_df
        
        st.dataframe(
            display_df.style.apply(highlight_status_hist, axis=1),
            width='stretch',
            hide_index=True,
            column_config={
                "subscription_name": st.column_config.TextColumn("Subscription", width="medium"),
                "user_name": st.column_config.TextColumn("User", width="medium"),
                "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                "due_date": st.column_config.DatetimeColumn("Due Date", format="DD MMM YYYY"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "paid_date": st.column_config.DatetimeColumn("Paid Date", format="DD MMM YYYY"),
            }
        )
    else:
        st.info(f"No payments found for {datetime(history_year, history_month, 1).strftime('%B %Y')}")

# Made with Bob
