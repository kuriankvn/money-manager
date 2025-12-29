"""Categories CRUD interface"""
import gradio as gr
import pandas as pd
from money_manager_gradio_ui import api_client


def refresh_categories_table():
    """Fetch and display all categories"""
    success, data = api_client.get_categories()
    if success and data:
        df = pd.DataFrame(data)
        return df
    elif success:
        return pd.DataFrame(columns=["uid", "name", "user_uid", "user_name"])
    else:
        gr.Warning(f"Failed to fetch categories: {data}")
        return pd.DataFrame(columns=["uid", "name", "user_uid", "user_name"])


def get_user_choices():
    """Get list of users for dropdown"""
    success, data = api_client.get_users()
    if success and data:
        return [(f"{user['name']} ({user['uid']})", user['uid']) for user in data]
    return []


def handle_create_category(name: str, user_uid: str):
    """Create a new category"""
    if not name or not name.strip():
        gr.Warning("Name is required")
        return refresh_categories_table(), "", user_uid
    
    if not user_uid:
        gr.Warning("Please select a user")
        return refresh_categories_table(), name, user_uid
    
    success, data = api_client.create_category(name.strip(), user_uid)
    if success:
        gr.Info(f"Category created: {data['name']}")
        return refresh_categories_table(), "", None
    else:
        gr.Warning(f"Failed to create category: {data}")
        return refresh_categories_table(), name, user_uid


def handle_update_category(uid: str, name: str, user_uid: str):
    """Update an existing category"""
    if not uid or not uid.strip():
        gr.Warning("Please enter Category UID")
        return refresh_categories_table(), uid, name, user_uid
    
    if not name or not name.strip():
        gr.Warning("Name is required")
        return refresh_categories_table(), uid, name, user_uid
    
    if not user_uid:
        gr.Warning("Please select a user")
        return refresh_categories_table(), uid, name, user_uid
    
    success, data = api_client.update_category(uid.strip(), name.strip(), user_uid)
    if success:
        gr.Info(f"Category updated: {data['name']}")
        return refresh_categories_table(), "", "", None
    else:
        gr.Warning(f"Failed to update category: {data}")
        return refresh_categories_table(), uid, name, user_uid


def handle_delete_category(uid: str):
    """Delete a category"""
    if not uid or not uid.strip():
        gr.Warning("Please enter Category UID")
        return refresh_categories_table(), uid
    
    success, data = api_client.delete_category(uid.strip())
    if success:
        gr.Info("Category deleted successfully")
        return refresh_categories_table(), ""
    else:
        gr.Warning(f"Failed to delete category: {data}")
        return refresh_categories_table(), uid


def create_interface():
    """Create the Categories CRUD interface"""
    with gr.Column():
        gr.Markdown("## Categories Management")
        
        # Display categories table
        categories_table = gr.Dataframe(
            value=refresh_categories_table(),
            label="All Categories",
            interactive=False,
            wrap=True
        )
        
        refresh_btn = gr.Button("🔄 Refresh", size="sm")
        
        gr.Markdown("---")
        
        # Create category section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Create Category")
                create_name = gr.Textbox(label="Name", placeholder="Enter category name")
                create_user = gr.Dropdown(
                    label="User",
                    choices=[],
                    interactive=True,
                    allow_custom_value=False
                )
                create_btn = gr.Button("➕ Create Category", variant="primary")
        
        gr.Markdown("---")
        
        # Update category section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Update Category")
                update_uid = gr.Textbox(label="Category UID", placeholder="Enter UID to update")
                update_name = gr.Textbox(label="New Name", placeholder="Enter new name")
                update_user = gr.Dropdown(
                    label="User",
                    choices=[],
                    interactive=True
                )
                update_btn = gr.Button("✏️ Update Category", variant="secondary")
        
        gr.Markdown("---")
        
        # Delete category section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Delete Category")
                delete_uid = gr.Textbox(label="Category UID", placeholder="Enter UID to delete")
                delete_btn = gr.Button("🗑️ Delete Category", variant="stop")
        
        # Event handlers
        def refresh_all():
            choices = get_user_choices()
            return refresh_categories_table(), gr.Dropdown(choices=choices), gr.Dropdown(choices=choices)
        
        refresh_btn.click(
            fn=refresh_all,
            outputs=[categories_table, create_user, update_user]
        )
        
        create_btn.click(
            fn=handle_create_category,
            inputs=[create_name, create_user],
            outputs=[categories_table, create_name, create_user]
        ).then(
            fn=lambda: gr.Dropdown(choices=get_user_choices()),
            outputs=create_user
        )
        
        update_btn.click(
            fn=handle_update_category,
            inputs=[update_uid, update_name, update_user],
            outputs=[categories_table, update_uid, update_name, update_user]
        )
        
        delete_btn.click(
            fn=handle_delete_category,
            inputs=[delete_uid],
            outputs=[categories_table, delete_uid]
        )


# Made with Bob