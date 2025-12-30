"""Date and time utilities."""
from datetime import date, datetime, timedelta


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def format_date(dt: date) -> str:
    """Format date as YYYY-MM-DD."""
    return dt.strftime("%Y-%m-%d")


def today() -> date:
    """Get today's date."""
    return date.today()


def get_month_start(dt: date) -> date:
    """Get first day of the month for given date."""
    return date(dt.year, dt.month, 1)


def get_month_end(dt: date) -> date:
    """Get last day of the month for given date."""
    if dt.month == 12:
        return date(dt.year, 12, 31)
    return date(dt.year, dt.month + 1, 1).replace(day=1) - timedelta(days=1)


def get_year_start(dt: date) -> date:
    """Get first day of the year for given date."""
    return date(dt.year, 1, 1)


def get_year_end(dt: date) -> date:
    """Get last day of the year for given date."""
    return date(dt.year, 12, 31)

