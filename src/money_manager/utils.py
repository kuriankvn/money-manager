import os
import re
import time
from typing import Optional
from uuid import UUID


def clear_screen() -> None:
    os.system(command='clear' if os.name == 'posix' else 'cls')


def pause() -> None:
    input("\nPress Enter to continue...")


def print_header(title: str) -> None:
    clear_screen()
    print("=" * 50)
    print(f" {title}")
    print("=" * 50)
    print()


def validate_uuid(uid: str) -> bool:
    try:
        UUID(hex=uid)
        return True
    except ValueError:
        return False


def validate_positive_float(value: str) -> Optional[float]:
    try:
        num: float = float(value)
        if num > 0:
            return num
        return None
    except ValueError:
        return None


def validate_non_empty(value: str) -> bool:
    return bool(value.strip())


def datetime_to_epoch(datetime_str: str) -> Optional[float]:
    if not datetime_str.strip():
        return time.time()
    
    try:
        datetime: time.struct_time = time.strptime(datetime_str.strip(), '%Y-%m-%d %H:%M')
        return time.mktime(datetime)
    except ValueError:
        print("Invalid date format. Expected: YYYY-MM-DD HH:MM")
        return None


def epoch_to_datetime(epoch: float) -> str:
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
