from typing import Any
from fastapi import FastAPI
from core.apis.users import router as users_router
from core.apis.categories import router as categories_router
from core.apis.transactions import router as transactions_router
from core.apis.subscriptions import router as subscriptions_router
from core.database import init_database

app: FastAPI = FastAPI(
    title="Money Manager API",
    description="REST API for managing personal finances",
    version="0.1.0"
)

app.include_router(router=users_router)
app.include_router(router=categories_router)
app.include_router(router=transactions_router)
app.include_router(router=subscriptions_router)


@app.get(path="/")
def root() -> dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "Money Manager API",
        "version": "0.1.0",
        "endpoints": {
            "users": "/users",
            "categories": "/categories",
            "transactions": "/transactions",
            "subscriptions": "/subscriptions",
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
