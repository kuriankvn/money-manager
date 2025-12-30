"""Investments CRUD interface with import/export"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.web import api_client


st.set_page_config(page_title="Investments", page_icon="📈", layout="wide")

st.title("📈 Investments Management")

if 'investments_data' not in st.session_state:
    st.session_state.investments_data = None
if 'selected_investment' not in st.session_state:
    st.session_state.selected_investment = None


def load_investments():
    """Load investments from API"""
    success, data = api_client.get_investments()
    if success and data:
        st.session_state.investments_data = pd.DataFrame(data)
        return st.session_state.investments_data
    elif success:
        st.session_state.investments_data = pd.DataFrame()
        return st.session_state.investments_data
    else:
        st.error(f"Failed to fetch investments: {data}")
        return pd.DataFrame()


def load_portfolio_summary():
    """Load portfolio summary"""
    success, data = api_client.get_portfolio_summary()
    if success:
        return data
    else:
        return {
            "total_invested": 0,
            "total_current_value": None,
            "total_gain_loss": None,
            "total_gain_loss_percentage": None
        }


tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Portfolio", "➕ Create", "💰 Contributions", "📊 Snapshots", "📁 Import/Export"])

with tab1:
    st.subheader("Investment Portfolio")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_portfolio"):
            load_investments()
            st.rerun()
    
    summary = load_portfolio_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Invested", f"₹{summary['total_invested']:,.2f}")
    with col2:
        current_val = summary.get('total_current_value')
        st.metric("Current Value", f"₹{current_val:,.2f}" if current_val else "N/A")
    with col3:
        gain_loss = summary.get('total_gain_loss')
        st.metric("Gain/Loss", f"₹{gain_loss:,.2f}" if gain_loss else "N/A")
    with col4:
        gain_pct = summary.get('total_gain_loss_percentage')
        st.metric("Return %", f"{gain_pct:.2f}%" if gain_pct else "N/A")
    
    st.markdown("---")
    
    df = load_investments()
    
    if not df.empty:
        st.dataframe(
            df,
            width='stretch',
            hide_index=True,
            column_config={
                "id": st.column_config.TextColumn("ID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "provider": st.column_config.TextColumn("Provider", width="medium"),
                "type": st.column_config.TextColumn("Type", width="small"),
                "notes": st.column_config.TextColumn("Notes", width="large"),
            }
        )
        
        st.markdown("---")
        st.subheader("Investment Details")
        
        investment_ids = df['id'].tolist()
        selected_id = st.selectbox("Select Investment", options=investment_ids, 
                                   format_func=lambda x: next((inv['name'] for inv in df.to_dict('records') if inv['id'] == x), x))
        
        if selected_id and st.button("📊 View Summary", type="primary"):
            success, inv_summary = api_client.get_investment_summary(selected_id)
            if success:
                st.json(inv_summary)
            else:
                st.error(f"Failed to load summary: {inv_summary}")
    else:
        st.info("No investments found. Create your first investment!")

with tab2:
    st.subheader("Create New Investment")
    
    with st.form("create_investment_form", clear_on_submit=True):
        name = st.text_input("Investment Name *", placeholder="e.g., Mutual Fund XYZ")
        provider = st.text_input("Provider *", placeholder="e.g., HDFC, SBI")
        inv_type = st.selectbox("Type *", options=["MUTUAL_FUND", "STOCK", "BOND", "FD", "PPF", "NPS", "OTHER"])
        notes = st.text_area("Notes", height=100)
        
        submitted = st.form_submit_button("➕ Create Investment", type="primary", use_container_width=True)
        
        if submitted:
            if not name or not name.strip():
                st.error("❌ Investment name is required")
            elif not provider or not provider.strip():
                st.error("❌ Provider is required")
            else:
                success, data = api_client.create_investment(
                    name=name.strip(),
                    provider=provider.strip(),
                    inv_type=inv_type,
                    notes=notes.strip() if notes else None
                )
                if success:
                    st.success(f"✅ Investment created: {data['name']}")
                    load_investments()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create investment: {data}")

with tab3:
    st.subheader("Add Contribution")
    
    df = load_investments()
    
    if df.empty:
        st.warning("⚠️ No investments found. Please create an investment first!")
    else:
        with st.form("add_contribution_form", clear_on_submit=True):
            investment_ids = df['id'].tolist()
            investment_id = st.selectbox(
                "Investment *",
                options=investment_ids,
                format_func=lambda x: next((inv['name'] for inv in df.to_dict('records') if inv['id'] == x), x)
            )
            
            col1, col2 = st.columns(2)
            with col1:
                contrib_date = st.date_input("Contribution Date *", value=date.today())
            with col2:
                amount = st.number_input("Amount *", min_value=0.01, value=0.01, step=100.0, format="%.2f")
            
            notes = st.text_area("Notes", height=100)
            
            submitted = st.form_submit_button("➕ Add Contribution", type="primary", use_container_width=True)
            
            if submitted:
                if amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                else:
                    success, data = api_client.add_contribution(
                        investment_id=investment_id,
                        date=contrib_date.isoformat(),
                        amount=float(amount),
                        notes=notes.strip() if notes else None
                    )
                    if success:
                        st.success(f"✅ Contribution added: ₹{amount:,.2f}")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to add contribution: {data}")
        
        st.markdown("---")
        st.subheader("View Contributions")
        
        selected_inv = st.selectbox(
            "Select Investment to View",
            options=investment_ids,
            format_func=lambda x: next((inv['name'] for inv in df.to_dict('records') if inv['id'] == x), x),
            key="view_contributions"
        )
        
        if st.button("📋 Load Contributions", type="secondary"):
            success, contrib_data = api_client.get_contributions(selected_inv)
            if success and contrib_data:
                contrib_df = pd.DataFrame(contrib_data)
                st.dataframe(
                    contrib_df,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "id": st.column_config.TextColumn("ID", width="small"),
                        "investment_id": st.column_config.TextColumn("Investment", width="medium"),
                        "date": st.column_config.TextColumn("Date", width="medium"),
                        "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                        "notes": st.column_config.TextColumn("Notes", width="large"),
                    }
                )
            elif success:
                st.info("No contributions found for this investment")
            else:
                st.error(f"Failed to load contributions: {contrib_data}")

with tab4:
    st.subheader("Add Value Snapshot")
    
    df = load_investments()
    
    if df.empty:
        st.warning("⚠️ No investments found. Please create an investment first!")
    else:
        with st.form("add_snapshot_form", clear_on_submit=True):
            investment_ids = df['id'].tolist()
            investment_id = st.selectbox(
                "Investment *",
                options=investment_ids,
                format_func=lambda x: next((inv['name'] for inv in df.to_dict('records') if inv['id'] == x), x)
            )
            
            col1, col2 = st.columns(2)
            with col1:
                snapshot_date = st.date_input("Snapshot Date *", value=date.today())
            with col2:
                current_value = st.number_input("Current Value *", min_value=0.01, value=0.01, step=100.0, format="%.2f")
            
            submitted = st.form_submit_button("➕ Add Snapshot", type="primary", use_container_width=True)
            
            if submitted:
                if current_value <= 0:
                    st.error("❌ Current value must be greater than 0")
                else:
                    success, data = api_client.add_snapshot(
                        investment_id=investment_id,
                        date=snapshot_date.isoformat(),
                        current_value=float(current_value)
                    )
                    if success:
                        st.success(f"✅ Snapshot added: ₹{current_value:,.2f}")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to add snapshot: {data}")

with tab5:
    st.subheader("Import/Export CSV")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Export Investments")
        
        if st.button("📥 Download Investments CSV", type="primary", use_container_width=True):
            success, data = api_client.export_investments_csv()
            if success:
                st.download_button(
                    label="💾 Save Investments File",
                    data=data,
                    file_name="investments.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success("✅ CSV ready for download")
            else:
                st.error(f"❌ Export failed: {data}")
        
        st.markdown("---")
        st.markdown("### 📤 Export Contributions")
        
        df = load_investments()
        if not df.empty:
            investment_ids = ["All"] + df['id'].tolist()
            selected_inv_export = st.selectbox(
                "Select Investment",
                options=investment_ids,
                format_func=lambda x: "All Investments" if x == "All" else next((inv['name'] for inv in df.to_dict('records') if inv['id'] == x), x),
                key="export_contributions"
            )
            
            if st.button("📥 Download Contributions CSV", type="primary", use_container_width=True):
                inv_id = None if selected_inv_export == "All" else selected_inv_export
                success, data = api_client.export_contributions_csv(inv_id)
                if success:
                    st.download_button(
                        label="💾 Save Contributions File",
                        data=data,
                        file_name="contributions.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    st.success("✅ CSV ready for download")
                else:
                    st.error(f"❌ Export failed: {data}")
    
    with col2:
        st.markdown("### 📥 Import Investments")
        
        uploaded_inv_file = st.file_uploader("Choose CSV file", type=['csv'], key="import_investments")
        
        if uploaded_inv_file is not None:
            try:
                csv_content = uploaded_inv_file.read().decode('utf-8')
                
                if st.button("📤 Import Investments CSV", type="primary", use_container_width=True):
                    success, data = api_client.import_investments_csv(csv_content)
                    if success:
                        st.success(f"✅ Import completed!")
                        st.json(data)
                        if data.get('errors'):
                            st.warning("⚠️ Some rows had errors:")
                            for error in data['errors']:
                                st.text(f"- {error}")
                        load_investments()
                    else:
                        st.error(f"❌ Import failed: {data}")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
        
        with st.expander("📋 Investments CSV Format"):
            st.markdown("""
            **Required columns:**
            - `name`: Investment name
            - `provider`: Provider name
            - `type`: Investment type (MUTUAL_FUND, STOCK, etc.)
            - `notes`: Additional notes (optional)
            
            **Example:**
            ```
            name,provider,type,notes
            HDFC Equity Fund,HDFC,MUTUAL_FUND,Growth fund
            Reliance Stock,Zerodha,STOCK,Long term hold
            ```
            """)
        
        st.markdown("---")
        st.markdown("### 📥 Import Contributions")
        
        uploaded_contrib_file = st.file_uploader("Choose CSV file", type=['csv'], key="import_contributions")
        
        if uploaded_contrib_file is not None:
            try:
                csv_content = uploaded_contrib_file.read().decode('utf-8')
                
                if st.button("📤 Import Contributions CSV", type="primary", use_container_width=True):
                    success, data = api_client.import_contributions_csv(csv_content)
                    if success:
                        st.success(f"✅ Import completed!")
                        st.json(data)
                        if data.get('errors'):
                            st.warning("⚠️ Some rows had errors:")
                            for error in data['errors']:
                                st.text(f"- {error}")
                    else:
                        st.error(f"❌ Import failed: {data}")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
        
        with st.expander("📋 Contributions CSV Format"):
            st.markdown("""
            **Required columns:**
            - `investment_id`: Investment ID (must exist)
            - `date`: Date in YYYY-MM-DD format
            - `amount`: Amount (positive number)
            - `notes`: Additional notes (optional)
            
            **Example:**
            ```
            investment_id,date,amount,notes
            inv_123,2024-01-15,10000,Monthly SIP
            inv_456,2024-01-20,5000,Lump sum
            ```
            """)

with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **General:**
    - Track multiple investment types
    - Add contributions as you invest
    - Record value snapshots to track performance
    - View portfolio summary for overall performance
    
    **CSV Import/Export:**
    - Export investments and contributions separately
    - Use Export to backup your data
    - Import CSV to bulk add data
    - Date format must be YYYY-MM-DD
    - Investment ID must exist for contributions
    """)

# Made with Bob
