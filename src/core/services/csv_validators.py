from datetime import datetime
import pandas as pd
from typing import Any, Optional

from core.domain import User, Category
from core.repositories.category import CategoryRepository
from core.repositories.user import UserRepository


class CSVValidator:
    def __init__(self) -> None:
        self.user_repo = UserRepository()
        self.category_repo = CategoryRepository()

    @staticmethod
    def validate_required_fields(df: pd.DataFrame, required_cols: list[str], errors: list[str]) -> bool:
        missing_cols: list[str] = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return False
        return True

    @staticmethod
    def validate_string(value: Any) -> Optional[str]:
        try:
            if pd.isna(value):
                return None
            sv: str = str(value).strip()
            return sv if sv else None
        except (TypeError, ValueError):
            return None
    
    @staticmethod
    def validate_int(value: Any) -> Optional[int]:
        if isinstance(value, bool):
            return None
        try:
            if pd.isna(value):
                return None
            iv: int = int(value)
            return iv if iv > 0 else None
        except (TypeError, ValueError, OverflowError):
            return None
    
    @staticmethod
    def validate_float(value: Any) -> Optional[float]:
        if isinstance(value, bool):
            return None
        try:
            if pd.isna(value):
                return None
            fv: float = float(value)
            return fv if fv > 0.0 else None
        except (TypeError, ValueError, OverflowError):
            return None
    
    @staticmethod
    def validate_boolean(value: Any) -> Optional[bool]:
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            bv: str = value.strip().lower()
            if bv == "true":
                return True
            if bv == "false":
                return False
        return None
    
    @staticmethod
    def validate_enum(value: Any, allowed: list[str]) -> Optional[str]:
        try:
            if pd.isna(value):
                return None
            sv: str = str(value).strip().lower()
        except (TypeError, ValueError):
            return None
        return sv if sv in {v.lower() for v in allowed} else None

    @staticmethod
    def validate_date(value: Any, date_format: str = "%d/%m/%Y") -> Optional[datetime]:
        if isinstance(value, bool):
            return None
        try:
            if pd.isna(value):
                return None
            return pd.to_datetime(value, format=date_format, errors="raise").to_pydatetime()
        except (TypeError, ValueError):
            return None
    
    def validate_user(self, value: Any) -> Optional[User]:
        name: Optional[str] = self.validate_string(value)
        if not name:
            return None
        return next((u for u in self.user_repo.get_all() if u.name == name), None)

    def validate_category(self, value: Any) -> Optional[Category]:
        name: Optional[str] = self.validate_string(value)
        if not name:
            return None
        return next((c for c in self.category_repo.get_all() if c.name == name), None)
