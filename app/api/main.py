"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import accounts, subscriptions, investments


app = FastAPI(
    title="Personal Finance Manager API",
    description="REST API for managing personal finances",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router)
app.include_router(subscriptions.router)
app.include_router(investments.router)


@app.get("/")
def root():
    return {
        "message": "Personal Finance Manager API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob


def run_server():
    """Entry point for money-manager-api script"""
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
