from datetime import datetime, timezone


def epoch_to_datetime(epoch: float) -> str:
    """Convert epoch timestamp to formatted datetime string"""
    dt: datetime = datetime.fromtimestamp(epoch, tz=timezone.utc)
    return dt.strftime(format="%Y-%m-%d %H:%M:%S UTC")


# Made with Bob