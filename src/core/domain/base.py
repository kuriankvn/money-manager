from enum import StrEnum


class Frequency(StrEnum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class SubscriptionInstanceStatus(StrEnum):
    DUE = "due"
    PAID = "paid"
    OVERDUE = "overdue"


class InvestmentStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"


class InvestmentPlanStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"


class InvestmentPlanInstanceStatus(StrEnum):
    PLANNED = "planned"
    EXECUTED = "executed"
    SKIPPED = "skipped"

# Made with Bob
