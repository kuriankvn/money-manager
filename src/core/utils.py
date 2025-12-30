from datetime import datetime, timezone
import uuid


def epoch_to_datetime(epoch: float) -> str:
    """Convert epoch timestamp to formatted datetime string"""
    dt: datetime = datetime.fromtimestamp(epoch, tz=timezone.utc)
    return dt.strftime(format="%Y-%m-%d %H:%M:%S UTC")


def generate_uid() -> str:
    """Generate a unique identifier"""
    return str(uuid.uuid4())
