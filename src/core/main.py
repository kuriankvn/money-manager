from typing import Any
from fastapi import FastAPI
from core.controller import (
    categories_router,
    accounts_router,
    transactions_router,
    subscriptions_router,
    subscription_instances_router,
    investments_router,
    investment_snapshots_router,
    investment_plans_router,
    investment_plan_instances_router,
    transactions_export_router,
    subscriptions_export_router
)
from core.storage import init_database

app: FastAPI = FastAPI(
    title="Money Manager API",
    description="REST API for managing personal finances",
    version="0.1.0"
)

app.include_router(router=categories_router)
app.include_router(router=accounts_router)
app.include_router(router=transactions_router)
app.include_router(router=subscriptions_router)
app.include_router(router=subscription_instances_router)
app.include_router(router=investments_router)
app.include_router(router=investment_snapshots_router)
app.include_router(router=investment_plans_router)
app.include_router(router=investment_plan_instances_router)
app.include_router(router=transactions_export_router)
app.include_router(router=subscriptions_export_router)


@app.get(path="/")
def root() -> dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "Money Manager API",
        "version": "0.1.0",
        "endpoints": {
            "categories": "/categories",
            "accounts": "/accounts",
            "transactions": "/transactions",
            "subscriptions": "/subscriptions",
            "subscription_instances": "/subscription-instances",
            "investments": "/investments",
            "investment_snapshots": "/investment-snapshots",
            "investment_plans": "/investment-plans",
            "investment_plan_instances": "/investment-plan-instances",
            "docs": "/docs"
        }
    }


@app.get(path="/health")
def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}



def main() -> None:
    """Entry point for money-manager command"""
    print("Initializing database...")
    try:
        init_database()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return
    
    import uvicorn
    uvicorn.run(app="core.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
