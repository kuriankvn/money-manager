"""Money and decimal handling utilities."""
from decimal import Decimal, ROUND_HALF_UP


def to_decimal(value: float | int | str | Decimal) -> Decimal:
    """Convert value to Decimal with 2 decimal places."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_money(value: Decimal) -> str:
    """Format decimal as money string."""
    return f"{value:,.2f}"


def parse_money(value: str) -> Decimal:
    """Parse money string to Decimal."""
    # Remove commas and convert
    cleaned = value.replace(",", "")
    return to_decimal(cleaned)

