import uuid


def generate_uid() -> str:
    """Generate a unique identifier"""
    return str(uuid.uuid4())

# Made with Bob