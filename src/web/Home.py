"""Main Streamlit application for Money Manager UI"""
import streamlit as st

st.set_page_config(
    page_title="Money Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

    
st.title("💰 Money Manager Dashboard")

st.markdown("""
Welcome to the **Money Manager** Streamlit UI! This application provides a modern interface
for managing your personal finances.

---

## 📋 Features

Use the sidebar to navigate between different sections:

### 💳 Transactions
- **🏦 Accounts**: Manage your financial accounts
- **📁 Categories**: Organize transactions by category
- **💰 Transactions**: Track income and expenses

### 🔄 Subscriptions
- **📋 Subscriptions**: Manage recurring subscriptions
- **📅 Subscription Instances**: Track individual subscription payments

### 📈 Investments
- **💼 Investments**: Manage your investment portfolios
- **📊 Investment Snapshots**: Track investment values over time
- **📝 Investment Plans**: Set up recurring investment plans
- **🎯 Investment Plan Instances**: Track individual investment contributions

---

## 🚀 Getting Started

### Prerequisites

1. **Backend must be running**:
   ```bash
   money-manager
   ```
   Backend URL: http://localhost:8000

2. **API Documentation**: http://localhost:8000/docs

### Usage Tips

- 📝 Create accounts and categories first
- 🔑 Use the UID from tables to update or delete items
- 🔄 Tables auto-refresh after operations
- ⏰ All timestamps are automatically set to current time
- 💾 Use forms to batch multiple inputs before submitting
- 📥 Export/Import CSV for bulk operations

---

## 🎨 About This UI

This Streamlit interface provides:
- ✅ Full CRUD operations for all entities
- 📊 Clean, responsive data tables
- 🎯 Form-based input validation
- 🔔 Real-time success/error notifications
- 📁 CSV Export/Import capabilities
- 🎨 Modern, customizable theme

---

## 📚 Navigation

Select a page from the sidebar to get started! 👈

---

""")

# Sidebar information
with st.sidebar:
    st.markdown("### 🔗 Quick Links")
    st.markdown("- [Backend API](http://localhost:8000)")
    st.markdown("- [API Docs](http://localhost:8000/docs)")
    st.markdown("- [Health Check](http://localhost:8000/health)")
    
    st.markdown("---")
    st.markdown("### ℹ️ System Info")
    st.info("Backend: http://localhost:8000")
    st.info("Streamlit UI: http://localhost:8501")
