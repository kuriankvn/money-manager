"""Accounts management page."""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import date
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.web import api_client

from app.storage.db import get_connection
from app.accounts.repository import AccountRepository, TransactionRepository
from app.accounts.service import AccountService, TransactionService


st.set_page_config(page_title="Accounts", page_icon="🏦", layout="wide")
st.title("🏦 Accounts & Transactions")


def get_services():
    """Get fresh service instances with new connection."""
    conn = get_connection()
    acc_repo = AccountRepository(conn=conn)
    txn_repo = TransactionRepository(conn=conn)
    return AccountService(repository=acc_repo), TransactionService(repository=txn_repo)


acc_service, txn_service = get_services()

tab1, tab2, tab3 = st.tabs(["Accounts", "Transactions", "Import/Export"])

with tab1:
    st.subheader("Create New Account")
    with st.form("create_account"):
        name = st.text_input("Account Name")
        acc_type = st.selectbox("Type", ["BANK", "CARD"])
        institution = st.text_input("Institution")
        notes = st.text_area("Notes", height=100)
        
        if st.form_submit_button("Create Account"):
            try:
                account = acc_service.create_account(
                    name=name,
                    account_type=acc_type,
                    institution=institution,
                    notes=notes if notes else None
                )
                st.success(f"Account '{account.name}' created successfully!")
                st.cache_resource.clear()
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.subheader("Existing Accounts")
    accounts = acc_service.list_accounts()
    
    if accounts:
        for account in accounts:
            with st.expander(f"{account.name} ({account.type})"):
                st.write(f"**Institution:** {account.institution}")
                if account.notes:
                    st.write(f"**Notes:** {account.notes}")
    else:
        st.info("No accounts found. Create one above!")

with tab2:
    st.subheader("Add Transaction")
    accounts = acc_service.list_accounts()
    
    if not accounts:
        st.warning("Please create an account first!")
    else:
        with st.form("create_transaction"):
            account_id = st.selectbox(
                "Account",
                options=[acc.id for acc in accounts],
                format_func=lambda x: next(acc.name for acc in accounts if acc.id == x)
            )
            txn_date = st.date_input("Date", value=date.today())
            amount = st.number_input("Amount (negative for expense)", value=0.0, step=100.0)
            description = st.text_input("Description")
            category = st.text_input("Category")
            notes = st.text_area("Notes", height=100)
            
            if st.form_submit_button("Add Transaction"):
                try:
                    transaction = txn_service.create_transaction(
                        account_id=account_id,
                        transaction_date=txn_date,
                        amount=Decimal(str(amount)),
                        description=description,
                        category=category,
                        notes=notes if notes else None
                    )
                    st.success("Transaction added successfully!")
                    st.cache_resource.clear()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        st.subheader("Recent Transactions")
        transactions = txn_service.list_all_transactions()
        
        if transactions:
            for txn in transactions[:20]:
                acc_name = next((acc.name for acc in accounts if acc.id == txn.account_id), "Unknown")
                color = "green" if txn.is_income else "red"
                st.markdown(
                    f"**{txn.date}** | {acc_name} | "
                    f":{color}[₹{abs(txn.amount):,.2f}] | "
                    f"{txn.description} ({txn.category})"
                )
        else:
            st.info("No transactions found.")

with tab3:
    st.subheader("Import/Export Transactions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Export")
        st.markdown("Download transactions as CSV file")
        
        accounts = acc_service.list_accounts()
        if accounts:
            account_ids = ["All"] + [acc.id for acc in accounts]
            selected_acc_export = st.selectbox(
                "Select Account",
                options=account_ids,
                format_func=lambda x: "All Accounts" if x == "All" else next((acc.name for acc in accounts if acc.id == x), x),
                key="export_transactions"
            )
            
            if st.button("📥 Download CSV", type="primary", use_container_width=True):
                acc_id = None if selected_acc_export == "All" else selected_acc_export
                success, data = api_client.export_transactions_csv(acc_id)
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
        else:
            st.info("No accounts found. Create an account first!")
    
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
                        st.cache_resource.clear()
                    else:
                        st.error(f"❌ Import failed: {data}")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
        
        with st.expander("📋 CSV Format Guide"):
            st.markdown("""
            **Required columns:**
            - `account_id`: Account ID (must exist)
            - `date`: Date in YYYY-MM-DD format
            - `amount`: Amount (positive for income, negative for expense)
            - `description`: Transaction description
            - `category`: Transaction category
            - `notes`: Additional notes (optional)
            
            **Example:**
            ```
            account_id,date,amount,description,category,notes
            acc_123,2024-01-15,50000,Salary,Income,Monthly salary
            acc_123,2024-01-16,-2500,Groceries,Food,Weekly shopping
            ```
            """)

with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Create accounts for banks and credit cards
    - Track all income and expenses
    - Use descriptive categories
    - Positive amounts = income, Negative = expenses
    
    **CSV Import/Export:**
    - Export to backup your transactions
    - Import CSV to bulk add transactions
    - Date format must be YYYY-MM-DD
    - Account ID must exist before importing
    - Amount can be positive or negative
    """)
