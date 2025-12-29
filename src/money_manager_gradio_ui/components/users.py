"""Users CRUD interface"""
import gradio as gr
import pandas as pd
from money_manager_gradio_ui import api_client


def refresh_users_table():
    """Fetch and display all users"""
    success, data = api_client.get_users()
    if success and data:
        df = pd.DataFrame(data)
        return df
    elif success:
        return pd.DataFrame(columns=["uid", "name"])
    else:
        gr.Warning(f"Failed to fetch users: {data}")
        return pd.DataFrame(columns=["uid", "name"])


def handle_create_user(name: str):
    """Create a new user"""
    if not name or not name.strip():
        gr.Warning("Name is required")
        return refresh_users_table(), ""
    
    success, data = api_client.create_user(name.strip())
    if success:
        gr.Info(f"User created: {data['name']}")
        return refresh_users_table(), ""
    else:
        gr.Warning(f"Failed to create user: {data}")
        return refresh_users_table(), name


def handle_update_user(uid: str, name: str):
    """Update an existing user"""
    if not uid or not uid.strip():
        gr.Warning("Please enter User UID")
        return refresh_users_table(), uid, name
    
    if not name or not name.strip():
        gr.Warning("Name is required")
        return refresh_users_table(), uid, name
    
    success, data = api_client.update_user(uid.strip(), name.strip())
    if success:
        gr.Info(f"User updated: {data['name']}")
        return refresh_users_table(), "", ""
    else:
        gr.Warning(f"Failed to update user: {data}")
        return refresh_users_table(), uid, name


def handle_delete_user(uid: str):
    """Delete a user"""
    if not uid or not uid.strip():
        gr.Warning("Please enter User UID")
        return refresh_users_table(), uid
    
    success, data = api_client.delete_user(uid.strip())
    if success:
        gr.Info("User deleted successfully")
        return refresh_users_table(), ""
    else:
        gr.Warning(f"Failed to delete user: {data}")
        return refresh_users_table(), uid


def create_interface():
    """Create the Users CRUD interface"""
    with gr.Column():
        gr.Markdown("## Users Management")
        
        # Display users table
        users_table = gr.Dataframe(
            value=refresh_users_table(),
            label="All Users",
            interactive=False,
            wrap=True
        )
        
        refresh_btn = gr.Button("🔄 Refresh", size="sm")
        
        gr.Markdown("---")
        
        # Create user section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Create User")
                create_name = gr.Textbox(label="Name", placeholder="Enter user name")
                create_btn = gr.Button("➕ Create User", variant="primary")
        
        gr.Markdown("---")
        
        # Update user section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Update User")
                update_uid = gr.Textbox(label="User UID", placeholder="Enter UID to update")
                update_name = gr.Textbox(label="New Name", placeholder="Enter new name")
                update_btn = gr.Button("✏️ Update User", variant="secondary")
        
        gr.Markdown("---")
        
        # Delete user section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Delete User")
                delete_uid = gr.Textbox(label="User UID", placeholder="Enter UID to delete")
                delete_btn = gr.Button("🗑️ Delete User", variant="stop")
        
        # Event handlers
        refresh_btn.click(
            fn=refresh_users_table,
            outputs=users_table
        )
        
        create_btn.click(
            fn=handle_create_user,
            inputs=[create_name],
            outputs=[users_table, create_name]
        )
        
        update_btn.click(
            fn=handle_update_user,
            inputs=[update_uid, update_name],
            outputs=[users_table, update_uid, update_name]
        )
        
        delete_btn.click(
            fn=handle_delete_user,
            inputs=[delete_uid],
            outputs=[users_table, delete_uid]
        )


# Made with Bob