"""Main Gradio application for Money Manager UI"""
import gradio as gr
from money_manager_gradio_ui.components import users, categories, transactions, subscriptions


def create_app():
    """Create and configure the Gradio application"""
    with gr.Blocks(
        title="Money Manager",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        """
    ) as app:
        gr.Markdown(
            """
            # 💰 Money Manager Dashboard
            
            Manage your personal finances with ease. This UI provides full CRUD operations for:
            - **Users**: Create and manage user accounts
            - **Categories**: Organize transactions by category
            - **Transactions**: Track income and expenses
            - **Subscriptions**: Manage recurring payments
            
            ---
            """
        )
        
        with gr.Tabs():
            with gr.Tab("👤 Users"):
                users.create_interface()
            
            with gr.Tab("📁 Categories"):
                categories.create_interface()
            
            with gr.Tab("💳 Transactions"):
                transactions.create_interface()
            
            with gr.Tab("🔄 Subscriptions"):
                subscriptions.create_interface()
        
        gr.Markdown(
            """
            ---
            
            ### 📝 Instructions
            
            1. **Start the backend**: Run `money-manager` in a separate terminal
            2. **Backend URL**: http://localhost:8000
            3. **API Docs**: http://localhost:8000/docs
            
            ### 💡 Tips
            
            - Create users first before adding categories, transactions, or subscriptions
            - Use the UID from the table to update or delete items
            - Click refresh buttons to update dropdowns with latest data
            - All timestamps are automatically set to current time
            
            ---
            *Made with Bob*
            """
        )
    
    return app


def main():
    """Main entry point for the UI application"""
    app = create_app()
    
    print("\n" + "="*60)
    print("🚀 Money Manager UI Starting...")
    print("="*60)
    print("\n📋 Prerequisites:")
    print("   1. Backend must be running: money-manager")
    print("   2. Backend URL: http://localhost:8000")
    print("\n🌐 UI will be available at:")
    print("   - Local: http://localhost:7860")
    print("   - Network: Check terminal output below")
    print("\n" + "="*60 + "\n")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()


# Made with Bob