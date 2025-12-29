from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from money_manager.api.users import router as users_router
from money_manager.api.categories import router as categories_router
from money_manager.api.transactions import router as transactions_router
from money_manager.api.subscriptions import router as subscriptions_router

app = FastAPI(
    title="Money Manager API",
    description="REST API for managing personal finances",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(transactions_router)
app.include_router(subscriptions_router)


@app.get("/")
def root():
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


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Made with Bob