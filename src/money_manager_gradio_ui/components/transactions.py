"""Transactions CRUD interface"""
import gradio as gr
import pandas as pd
from datetime import datetime
from money_manager_gradio_ui import api_client


def refresh_transactions_table():
    """Fetch and display all transactions"""
    success, data = api_client.get_transactions()
    if success and data:
        df = pd.DataFrame(data)
        # Convert timestamp to readable format
        if 'datetime' in df.columns:
            df['datetime'] = df['datetime'].apply(
                lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
            )
        return df
    elif success:
        return pd.DataFrame(columns=[
            "uid", "name", "amount", "datetime", "type",
            "user_uid", "user_name", "category_uid", "category_name"
        ])
    else:
        gr.Warning(f"Failed to fetch transactions: {data}")
        return pd.DataFrame(columns=[
            "uid", "name", "amount", "datetime", "type",
            "user_uid", "user_name", "category_uid", "category_name"
        ])


def get_user_choices():
    """Get list of users for dropdown"""
    success, data = api_client.get_users()
    if success and data:
        return [(f"{user['name']} ({user['uid']})", user['uid']) for user in data]
    return []


def get_category_choices():
    """Get list of categories for dropdown"""
    success, data = api_client.get_categories()
    if success and data:
        return [(f"{cat['name']} ({cat['uid']})", cat['uid']) for cat in data]
    return []


def handle_create_transaction(
    name: str,
    amount: float,
    transaction_type: str,
    user_uid: str,
    category_uid: str
):
    """Create a new transaction"""
    if not name or not name.strip():
        gr.Warning("Name is required")
        return refresh_transactions_table(), "", amount, transaction_type, user_uid, category_uid
    
    if amount <= 0:
        gr.Warning("Amount must be greater than 0")
        return refresh_transactions_table(), name, amount, transaction_type, user_uid, category_uid
    
    if not user_uid:
        gr.Warning("Please select a user")
        return refresh_transactions_table(), name, amount, transaction_type, user_uid, category_uid
    
    if not category_uid:
        gr.Warning("Please select a category")
        return refresh_transactions_table(), name, amount, transaction_type, user_uid, category_uid
    
    # Use current timestamp
    timestamp = datetime.now().timestamp()
    
    success, data = api_client.create_transaction(
        name.strip(),
        amount,
        timestamp,
        transaction_type,
        user_uid,
        category_uid
    )
    
    if success:
        gr.Info(f"Transaction created: {data['name']}")
        return refresh_transactions_table(), "", 0.0, "expense", None, None
    else:
        gr.Warning(f"Failed to create transaction: {data}")
        return refresh_transactions_table(), name, amount, transaction_type, user_uid, category_uid


def handle_update_transaction(
    uid: str,
    name: str,
    amount: float,
    transaction_type: str,
    user_uid: str,
    category_uid: str
):
    """Update an existing transaction"""
    if not uid or not uid.strip():
        gr.Warning("Please enter Transaction UID")
        return refresh_transactions_table(), uid, name, amount, transaction_type, user_uid, category_uid
    
    if not name or not name.strip():
        gr.Warning("Name is required")
        return refresh_transactions_table(), uid, name, amount, transaction_type, user_uid, category_uid
    
    if amount <= 0:
        gr.Warning("Amount must be greater than 0")
        return refresh_transactions_table(), uid, name, amount, transaction_type, user_uid, category_uid
    
    if not user_uid:
        gr.Warning("Please select a user")
        return refresh_transactions_table(), uid, name, amount, transaction_type, user_uid, category_uid
    
    if not category_uid:
        gr.Warning("Please select a category")
        return refresh_transactions_table(), uid, name, amount, transaction_type, user_uid, category_uid
    
    # Use current timestamp
    timestamp = datetime.now().timestamp()
    
    success, data = api_client.update_transaction(
        uid.strip(),
        name.strip(),
        amount,
        timestamp,
        transaction_type,
        user_uid,
        category_uid
    )
    
    if success:
        gr.Info(f"Transaction updated: {data['name']}")
        return refresh_transactions_table(), "", "", 0.0, "expense", None, None
    else:
        gr.Warning(f"Failed to update transaction: {data}")
        return refresh_transactions_table(), uid, name, amount, transaction_type, user_uid, category_uid


def handle_delete_transaction(uid: str):
    """Delete a transaction"""
    if not uid or not uid.strip():
        gr.Warning("Please enter Transaction UID")
        return refresh_transactions_table(), uid
    
    success, data = api_client.delete_transaction(uid.strip())
    if success:
        gr.Info("Transaction deleted successfully")
        return refresh_transactions_table(), ""
    else:
        gr.Warning(f"Failed to delete transaction: {data}")
        return refresh_transactions_table(), uid


def create_interface():
    """Create the Transactions CRUD interface"""
    with gr.Column():
        gr.Markdown("## Transactions Management")
        
        # Display transactions table
        transactions_table = gr.Dataframe(
            value=refresh_transactions_table(),
            label="All Transactions",
            interactive=False,
            wrap=True
        )
        
        refresh_btn = gr.Button("🔄 Refresh", size="sm")
        
        gr.Markdown("---")
        
        # Create transaction section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Create Transaction")
                create_name = gr.Textbox(label="Name", placeholder="Enter transaction name")
                create_amount = gr.Number(label="Amount", value=0.0, minimum=0.01)
                create_type = gr.Radio(
                    label="Type",
                    choices=["income", "expense"],
                    value="expense"
                )
                create_user = gr.Dropdown(
                    label="User",
                    choices=[],
                    interactive=True
                )
                create_category = gr.Dropdown(
                    label="Category",
                    choices=[],
                    interactive=True
                )
                create_btn = gr.Button("➕ Create Transaction", variant="primary")
        
        gr.Markdown("---")
        
        # Update transaction section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Update Transaction")
                update_uid = gr.Textbox(label="Transaction UID", placeholder="Enter UID to update")
                update_name = gr.Textbox(label="New Name", placeholder="Enter new name")
                update_amount = gr.Number(label="Amount", value=0.0, minimum=0.01)
                update_type = gr.Radio(
                    label="Type",
                    choices=["income", "expense"],
                    value="expense"
                )
                update_user = gr.Dropdown(
                    label="User",
                    choices=[],
                    interactive=True
                )
                update_category = gr.Dropdown(
                    label="Category",
                    choices=[],
                    interactive=True
                )
                update_btn = gr.Button("✏️ Update Transaction", variant="secondary")
        
        gr.Markdown("---")
        
        # Delete transaction section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Delete Transaction")
                delete_uid = gr.Textbox(label="Transaction UID", placeholder="Enter UID to delete")
                delete_btn = gr.Button("🗑️ Delete Transaction", variant="stop")
        
        # Event handlers
        def refresh_all():
            user_choices = get_user_choices()
            category_choices = get_category_choices()
            return (
                refresh_transactions_table(),
                gr.Dropdown(choices=user_choices),
                gr.Dropdown(choices=category_choices),
                gr.Dropdown(choices=user_choices),
                gr.Dropdown(choices=category_choices)
            )
        
        refresh_btn.click(
            fn=refresh_all,
            outputs=[
                transactions_table,
                create_user,
                create_category,
                update_user,
                update_category
            ]
        )
        
        create_btn.click(
            fn=handle_create_transaction,
            inputs=[create_name, create_amount, create_type, create_user, create_category],
            outputs=[transactions_table, create_name, create_amount, create_type, create_user, create_category]
        )
        
        update_btn.click(
            fn=handle_update_transaction,
            inputs=[update_uid, update_name, update_amount, update_type, update_user, update_category],
            outputs=[transactions_table, update_uid, update_name, update_amount, update_type, update_user, update_category]
        )
        
        delete_btn.click(
            fn=handle_delete_transaction,
            inputs=[delete_uid],
            outputs=[transactions_table, delete_uid]
        )


# Made with Bob