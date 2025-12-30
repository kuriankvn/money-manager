"""Transactions CRUD interface"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from web import api_client


st.set_page_config(page_title="Transactions", page_icon="💳", layout="wide")

st.title("💳 Transactions Management")

# Initialize session state
if 'transactions_data' not in st.session_state:
    st.session_state.transactions_data = None
if 'accounts_list' not in st.session_state:
    st.session_state.accounts_list = []
if 'categories_list' not in st.session_state:
    st.session_state.categories_list = []


def load_transactions():
    """Load transactions from API"""
    success, data = api_client.get_transactions()
    if success and data:
        df = pd.DataFrame(data)
        # Date is already in string format from API
        st.session_state.transactions_data = df
        return df
    elif success:
        st.session_state.transactions_data = pd.DataFrame(columns=[
            "uid", "name", "amount", "date",
            "account_uid", "account_name", "category_uid", "category_name"
        ])
        return st.session_state.transactions_data
    else:
        st.error(f"Failed to fetch transactions: {data}")
        return pd.DataFrame(columns=[
            "uid", "name", "amount", "date",
            "account_uid", "account_name", "category_uid", "category_name"
        ])


def load_accounts():
    """Load accounts for dropdown"""
    success, data = api_client.get_accounts()
    if success and data:
        st.session_state.accounts_list = [(account['name'], account['uid']) for account in data]
    else:
        st.session_state.accounts_list = []
    return st.session_state.accounts_list


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
    st.subheader("All Transactions")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_transactions"):
            load_transactions()
            load_accounts()
            load_categories()
            st.rerun()
    
    # Load and display transactions
    df = load_transactions()
    
    if not df.empty:
        # Hide UUID columns, show only names
        display_columns = ["uid", "name", "amount", "date", "account_name", "category_name"]
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True,
            column_config={
                "uid": st.column_config.TextColumn("UID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                "date": st.column_config.TextColumn("Date", width="medium"),
                "account_name": st.column_config.TextColumn("Account", width="medium"),
                "category_name": st.column_config.TextColumn("Category", width="medium"),
            }
        )
        
        # Summary statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Transactions", len(df))
        with col2:
            total = df['amount'].sum() if 'amount' in df.columns else 0
            st.metric("Total Amount", f"₹{total:.2f}")
    else:
        st.info("No transactions found. Create your first transaction!")

with tab2:
    st.subheader("Create New Transaction")
    
    # Load accounts and categories
    accounts = load_accounts()
    categories = load_categories()
    
    if not accounts:
        st.warning("⚠️ No accounts found. Please create an account first!")
    elif not categories:
        st.warning("⚠️ No categories found. Please create a category first!")
    else:
        with st.form("create_transaction_form", clear_on_submit=True):
            name = st.text_input("Transaction Name *", placeholder="Enter transaction name")
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            transaction_date = st.date_input("Transaction Date *", value=datetime.now())
            
            account_options = {f"{account[0]} ({account[1]})": account[1] for account in accounts}
            selected_account = st.selectbox("Account *", options=list(account_options.keys()))
            
            category_options = {f"{cat[0]} ({cat[1]})": cat[1] for cat in categories}
            selected_category = st.selectbox("Category *", options=list(category_options.keys()))
            
            submitted = st.form_submit_button("➕ Create Transaction", type="primary", width='stretch')
            
            if submitted:
                if not name or not name.strip():
                    st.error("❌ Transaction name is required")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                elif not selected_account:
                    st.error("❌ Please select an account")
                elif not selected_category:
                    st.error("❌ Please select a category")
                else:
                    account_uid = account_options[selected_account]
                    category_uid = category_options[selected_category]
                    date_str = transaction_date.strftime('%Y-%m-%d')
                    
                    success, data = api_client.create_transaction(
                        name.strip(), amount, date_str, account_uid, category_uid
                    )
                    if success:
                        st.success(f"✅ Transaction created: {data['name']}")
                        load_transactions()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create transaction: {data}")

with tab3:
    st.subheader("Update Transaction")
    
    # Load accounts and categories
    accounts = load_accounts()
    categories = load_categories()
    
    if not accounts:
        st.warning("⚠️ No accounts found. Please create an account first!")
    elif not categories:
        st.warning("⚠️ No categories found. Please create a category first!")
    else:
        with st.form("update_transaction_form"):
            uid = st.text_input("Transaction UID *", placeholder="Enter UID to update")
            name = st.text_input("New Name *", placeholder="Enter new name")
            amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=0.01, format="%.2f")
            transaction_date = st.date_input("Transaction Date *", value=datetime.now())
            
            account_options = {f"{account[0]} ({account[1]})": account[1] for account in accounts}
            selected_account = st.selectbox("Account *", options=list(account_options.keys()))
            
            category_options = {f"{cat[0]} ({cat[1]})": cat[1] for cat in categories}
            selected_category = st.selectbox("Category *", options=list(category_options.keys()))
            
            submitted = st.form_submit_button("✏️ Update Transaction", type="secondary", width='stretch')
            
            if submitted:
                if not uid or not uid.strip():
                    st.error("❌ Transaction UID is required")
                elif not name or not name.strip():
                    st.error("❌ Name is required")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                elif not selected_account:
                    st.error("❌ Please select an account")
                elif not selected_category:
                    st.error("❌ Please select a category")
                else:
                    account_uid = account_options[selected_account]
                    category_uid = category_options[selected_category]
                    date_str = transaction_date.strftime('%Y-%m-%d')
                    
                    success, data = api_client.update_transaction(
                        uid.strip(), name.strip(), amount, date_str, account_uid, category_uid
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
        
        submitted = st.form_submit_button("🗑️ Delete Transaction", type="primary", width='stretch')
        
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

with tab5:
    st.subheader("Import/Export CSV")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Export")
        st.markdown("Download all transactions as CSV file")
        
        if st.button("📥 Download CSV", type="primary", use_container_width=True):
            success, data = api_client.export_transactions_csv()
            if success:
                st.download_button(
                    label="💾 Save File",
                    data=data,
                    file_name="transactions.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success("✅ CSV ready for download")
            else:
                st.error(f"❌ Export failed: {data}")
    
    with col2:
        st.markdown("### 📥 Import")
        st.markdown("Upload CSV file to import transactions")
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], key="import_transactions")
        
        if uploaded_file is not None:
            try:
                csv_content = uploaded_file.read().decode('utf-8')
                
                if st.button("📤 Import CSV", type="primary", use_container_width=True):
                    success, data = api_client.import_transactions_csv(csv_content)
                    if success:
                        st.success(f"✅ Import completed!")
                        st.json(data)
                        if data.get('errors'):
                            st.warning("⚠️ Some rows had errors:")
                            for error in data['errors']:
                                st.text(f"- {error}")
                        load_transactions()
                    else:
                        st.error(f"❌ Import failed: {data}")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
        
        with st.expander("📋 CSV Format Guide"):
            st.markdown("""
            **Required columns:**
            - `name`: Transaction name
            - `amount`: Amount (positive number)
            - `date`: Date in DD/MM/YYYY format (mandatory)
            - `account`: Account name (must exist)
            - `category`: Category name (must exist)
            
            **Example:**
            ```
            name,amount,date,account,category
            Salary,50000,15/01/2024,Checking Account,Income
            Groceries,2500,16/01/2024,Credit Card,Food
            ```
            """)

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Track all transactions for better financial insights
    - Use descriptive names for easy identification
    - Assign appropriate accounts and categories
    
    **CSV Import/Export:**
    - Use Export to backup your transactions
    - Import CSV to bulk add transactions
    - Date format must be DD/MM/YYYY
    - Ensure account and category names exist before importing
    - Account and category names are case-sensitive
    """)
