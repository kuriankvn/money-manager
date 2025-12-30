from .transactions import categories_router, accounts_router, transactions_router
from .subscriptions import subscriptions_router, subscription_instances_router
from .investments import (
    investments_router,
    investment_snapshots_router,
    investment_plans_router,
    investment_plan_instances_router
)

__all__ = [
    "categories_router",
    "accounts_router",
    "transactions_router",
    "subscriptions_router",
    "subscription_instances_router",
    "investments_router",
    "investment_snapshots_router",
    "investment_plans_router",
    "investment_plan_instances_router",
]

# Made with Bob