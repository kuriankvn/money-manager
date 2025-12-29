"""Money Manager Package - Main Package"""
from money_manager.database import init_database, get_connection
from money_manager.repositories import (
    IRepository,
    UserRepository,
    CategoryRepository,
    TransactionRepository,
    SubscriptionRepository,
)
from money_manager.models import (
    User,
    Category,
    Transaction,
    Subscription,
    Interval,
)

__version__ = "0.1.0"
__all__ = [
    "__version__",
    "init_database",
    "get_connection",
    "IRepository",
    "User",
    "UserRepository",
    "Category",
    "CategoryRepository",
    "Transaction",
    "TransactionRepository",
    "Subscription",
    "Interval",
    "SubscriptionRepository",
]

# Made with Bob
