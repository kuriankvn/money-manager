"""CSV validation utilities for import operations"""
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

import pandas as pd


class CSVValidator:
    """Validator for CSV import operations"""
    
    @staticmethod
    def validate_required_fields(df: pd.DataFrame, required_cols: list[str], errors: list[str]) -> bool:
        """Validate that all required columns are present"""
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return False
        return True
    
    @staticmethod
    def validate_string(value: Any) -> Optional[str]:
        """Validate and convert to string"""
        try:
            if pd.isna(value):
                return None
            sv = str(value).strip()
            return sv if sv else None
        except (TypeError, ValueError):
            return None
    
    @staticmethod
    def validate_int(value: Any) -> Optional[int]:
        """Validate and convert to integer"""
        if isinstance(value, bool):
            return None
        try:
            if pd.isna(value):
                return None
            iv = int(value)
            return iv if iv > 0 else None
        except (TypeError, ValueError, OverflowError):
            return None
    
    @staticmethod
    def validate_float(value: Any) -> Optional[float]:
        """Validate and convert to float"""
        if isinstance(value, bool):
            return None
        try:
            if pd.isna(value):
                return None
            fv = float(value)
            return fv if fv > 0.0 else None
        except (TypeError, ValueError, OverflowError):
            return None
    
    @staticmethod
    def validate_decimal(value: Any) -> Optional[Decimal]:
        """Validate and convert to Decimal"""
        if isinstance(value, bool):
            return None
        try:
            if pd.isna(value):
                return None
            dv = Decimal(str(value))
            return dv if dv > 0 else None
        except (TypeError, ValueError):
            return None
    
    @staticmethod
    def validate_boolean(value: Any) -> Optional[bool]:
        """Validate and convert to boolean"""
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            bv = value.strip().lower()
            if bv == "true":
                return True
            if bv == "false":
                return False
        return None
    
    @staticmethod
    def validate_enum(value: Any, allowed: list[str]) -> Optional[str]:
        """Validate that value is in allowed list"""
        try:
            if pd.isna(value):
                return None
            sv = str(value).strip().upper()
        except (TypeError, ValueError):
            return None
        return sv if sv in {v.upper() for v in allowed} else None
    
    @staticmethod
    def validate_date(value: Any, date_format: str = "%Y-%m-%d") -> Optional[date]:
        """Validate and convert to date"""
        if isinstance(value, bool):
            return None
        try:
            if pd.isna(value):
                return None
            if isinstance(value, date):
                return value
            return datetime.strptime(str(value).strip(), date_format).date()
        except (TypeError, ValueError):
            return None
    
    @staticmethod
    def validate_iso_date(value: Any) -> Optional[date]:
        """Validate ISO format date (YYYY-MM-DD)"""
        try:
            if pd.isna(value):
                return None
            if isinstance(value, date):
                return value
            return datetime.fromisoformat(str(value).strip()).date()
        except (TypeError, ValueError):
            return None

# Made with Bob
