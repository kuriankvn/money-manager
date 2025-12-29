"""Subscriptions CRUD interface"""
import gradio as gr
import pandas as pd
from money_manager_gradio_ui import api_client


def refresh_subscriptions_table():
    """Fetch and display all subscriptions"""
    success, data = api_client.get_subscriptions()
    if success and data:
        df = pd.DataFrame(data)
        return df
    elif success:
        return pd.DataFrame(columns=[
            "uid", "name", "amount", "interval", "multiplier",
            "user_uid", "user_name", "category_uid", "category_name", "active"
        ])
    else:
        gr.Warning(f"Failed to fetch subscriptions: {data}")
        return pd.DataFrame(columns=[
            "uid", "name", "amount", "interval", "multiplier",
            "user_uid", "user_name", "category_uid", "category_name", "active"
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


def handle_create_subscription(
    name: str,
    amount: float,
    interval: str,
    multiplier: int,
    user_uid: str,
    category_uid: str,
    active: bool
):
    """Create a new subscription"""
    if not name or not name.strip():
        gr.Warning("Name is required")
        return refresh_subscriptions_table(), "", amount, interval, multiplier, user_uid, category_uid, active
    
    if amount <= 0:
        gr.Warning("Amount must be greater than 0")
        return refresh_subscriptions_table(), name, amount, interval, multiplier, user_uid, category_uid, active
    
    if multiplier < 1:
        gr.Warning("Multiplier must be at least 1")
        return refresh_subscriptions_table(), name, amount, interval, multiplier, user_uid, category_uid, active
    
    if not user_uid:
        gr.Warning("Please select a user")
        return refresh_subscriptions_table(), name, amount, interval, multiplier, user_uid, category_uid, active
    
    if not category_uid:
        gr.Warning("Please select a category")
        return refresh_subscriptions_table(), name, amount, interval, multiplier, user_uid, category_uid, active
    
    success, data = api_client.create_subscription(
        name.strip(),
        amount,
        interval,
        multiplier,
        user_uid,
        category_uid,
        active
    )
    
    if success:
        gr.Info(f"Subscription created: {data['name']}")
        return refresh_subscriptions_table(), "", 0.0, "monthly", 1, None, None, True
    else:
        gr.Warning(f"Failed to create subscription: {data}")
        return refresh_subscriptions_table(), name, amount, interval, multiplier, user_uid, category_uid, active


def handle_update_subscription(
    uid: str,
    name: str,
    amount: float,
    interval: str,
    multiplier: int,
    user_uid: str,
    category_uid: str,
    active: bool
):
    """Update an existing subscription"""
    if not uid or not uid.strip():
        gr.Warning("Please enter Subscription UID")
        return refresh_subscriptions_table(), uid, name, amount, interval, multiplier, user_uid, category_uid, active
    
    if not name or not name.strip():
        gr.Warning("Name is required")
        return refresh_subscriptions_table(), uid, name, amount, interval, multiplier, user_uid, category_uid, active
    
    if amount <= 0:
        gr.Warning("Amount must be greater than 0")
        return refresh_subscriptions_table(), uid, name, amount, interval, multiplier, user_uid, category_uid, active
    
    if multiplier < 1:
        gr.Warning("Multiplier must be at least 1")
        return refresh_subscriptions_table(), uid, name, amount, interval, multiplier, user_uid, category_uid, active
    
    if not user_uid:
        gr.Warning("Please select a user")
        return refresh_subscriptions_table(), uid, name, amount, interval, multiplier, user_uid, category_uid, active
    
    if not category_uid:
        gr.Warning("Please select a category")
        return refresh_subscriptions_table(), uid, name, amount, interval, multiplier, user_uid, category_uid, active
    
    success, data = api_client.update_subscription(
        uid.strip(),
        name.strip(),
        amount,
        interval,
        multiplier,
        user_uid,
        category_uid,
        active
    )
    
    if success:
        gr.Info(f"Subscription updated: {data['name']}")
        return refresh_subscriptions_table(), "", "", 0.0, "monthly", 1, None, None, True
    else:
        gr.Warning(f"Failed to update subscription: {data}")
        return refresh_subscriptions_table(), uid, name, amount, interval, multiplier, user_uid, category_uid, active


def handle_delete_subscription(uid: str):
    """Delete a subscription"""
    if not uid or not uid.strip():
        gr.Warning("Please enter Subscription UID")
        return refresh_subscriptions_table(), uid
    
    success, data = api_client.delete_subscription(uid.strip())
    if success:
        gr.Info("Subscription deleted successfully")
        return refresh_subscriptions_table(), ""
    else:
        gr.Warning(f"Failed to delete subscription: {data}")
        return refresh_subscriptions_table(), uid


def create_interface():
    """Create the Subscriptions CRUD interface"""
    with gr.Column():
        gr.Markdown("## Subscriptions Management")
        
        # Display subscriptions table
        subscriptions_table = gr.Dataframe(
            value=refresh_subscriptions_table(),
            label="All Subscriptions",
            interactive=False,
            wrap=True
        )
        
        refresh_btn = gr.Button("🔄 Refresh", size="sm")
        
        gr.Markdown("---")
        
        # Create subscription section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Create Subscription")
                create_name = gr.Textbox(label="Name", placeholder="Enter subscription name")
                create_amount = gr.Number(label="Amount", value=0.0, minimum=0.01)
                create_interval = gr.Radio(
                    label="Interval",
                    choices=["daily", "weekly", "monthly", "yearly"],
                    value="monthly"
                )
                create_multiplier = gr.Number(
                    label="Multiplier",
                    value=1,
                    minimum=1,
                    step=1,
                    precision=0
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
                create_active = gr.Checkbox(label="Active", value=True)
                create_btn = gr.Button("➕ Create Subscription", variant="primary")
        
        gr.Markdown("---")
        
        # Update subscription section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Update Subscription")
                update_uid = gr.Textbox(label="Subscription UID", placeholder="Enter UID to update")
                update_name = gr.Textbox(label="New Name", placeholder="Enter new name")
                update_amount = gr.Number(label="Amount", value=0.0, minimum=0.01)
                update_interval = gr.Radio(
                    label="Interval",
                    choices=["daily", "weekly", "monthly", "yearly"],
                    value="monthly"
                )
                update_multiplier = gr.Number(
                    label="Multiplier",
                    value=1,
                    minimum=1,
                    step=1,
                    precision=0
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
                update_active = gr.Checkbox(label="Active", value=True)
                update_btn = gr.Button("✏️ Update Subscription", variant="secondary")
        
        gr.Markdown("---")
        
        # Delete subscription section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Delete Subscription")
                delete_uid = gr.Textbox(label="Subscription UID", placeholder="Enter UID to delete")
                delete_btn = gr.Button("🗑️ Delete Subscription", variant="stop")
        
        # Event handlers
        def refresh_all():
            user_choices = get_user_choices()
            category_choices = get_category_choices()
            return (
                refresh_subscriptions_table(),
                gr.Dropdown(choices=user_choices),
                gr.Dropdown(choices=category_choices),
                gr.Dropdown(choices=user_choices),
                gr.Dropdown(choices=category_choices)
            )
        
        refresh_btn.click(
            fn=refresh_all,
            outputs=[
                subscriptions_table,
                create_user,
                create_category,
                update_user,
                update_category
            ]
        )
        
        create_btn.click(
            fn=handle_create_subscription,
            inputs=[
                create_name,
                create_amount,
                create_interval,
                create_multiplier,
                create_user,
                create_category,
                create_active
            ],
            outputs=[
                subscriptions_table,
                create_name,
                create_amount,
                create_interval,
                create_multiplier,
                create_user,
                create_category,
                create_active
            ]
        )
        
        update_btn.click(
            fn=handle_update_subscription,
            inputs=[
                update_uid,
                update_name,
                update_amount,
                update_interval,
                update_multiplier,
                update_user,
                update_category,
                update_active
            ],
            outputs=[
                subscriptions_table,
                update_uid,
                update_name,
                update_amount,
                update_interval,
                update_multiplier,
                update_user,
                update_category,
                update_active
            ]
        )
        
        delete_btn.click(
            fn=handle_delete_subscription,
            inputs=[delete_uid],
            outputs=[subscriptions_table, delete_uid]
        )


# Made with Bob