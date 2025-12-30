import pandas as pd
import io
from typing import Any, Optional
from core.domain import Subscription
from core.domain.base import Frequency, SubscriptionStatus
from core.repositories import SubscriptionRepository
from core.utils import generate_uid


class SubscriptionService:
    def __init__(self) -> None:
        self.subscription_repo = SubscriptionRepository()
    
    def export_to_csv(self) -> str:
        """Export all subscriptions to CSV format"""
        subscriptions: list[Subscription] = self.subscription_repo.get_all()
        data: list[dict[str, Any]] = [{
            'name': sub.name,
            'amount': sub.amount,
            'frequency': sub.frequency.value,
            'interval': sub.interval,
            'due_day': sub.due_day,
            'due_month': sub.due_month if sub.due_month else '',
            'status': sub.status.value
        } for sub in subscriptions]
        
        df: pd.DataFrame = pd.DataFrame(data)
        return df.to_csv(index=False)
    
    def import_from_csv(self, csv_content: str) -> dict[str, Any]:
        """Import subscriptions from CSV content"""
        valid_rows, errors = self._validate_csv(csv_content)
        
        created_count = 0
        failed_count: int = len(errors)
        
        for row_data in valid_rows:
            try:
                uid: str = generate_uid()
                subscription: Subscription = Subscription(
                    uid=uid,
                    name=row_data['name'],
                    amount=row_data['amount'],
                    frequency=Frequency(row_data['frequency']),
                    interval=row_data['interval'],
                    due_day=row_data['due_day'],
                    due_month=row_data['due_month'],
                    status=SubscriptionStatus(row_data['status'])
                )
                self.subscription_repo.create(entity=subscription)
                created_count += 1
            except Exception as e:
                errors.append(f"Failed to create subscription '{row_data['name']}': {str(e)}")
                failed_count += 1
        
        return {
            "created": created_count,
            "failed": failed_count,
            "errors": errors
        }
    
    def _validate_csv(self, csv_content: str) -> tuple[list[dict[str, Any]], list[str]]:
        """Validate CSV content and return valid rows with errors"""
        errors: list[str] = []
        valid_rows: list[dict[str, Any]] = []

        try:
            df: pd.DataFrame = pd.read_csv(io.StringIO(csv_content))
        except Exception as e:
            return [], [f"CSV parsing error: {str(e)}"]

        required_cols: list[str] = ['name', 'amount', 'frequency', 'interval', 'due_day', 'status']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return [], errors

        for idx, row in df.iterrows():
            row_num = idx + 2  # type: ignore

            # Validate name
            name = str(row.get('name', '')).strip()
            if not name:
                errors.append(f"Row {row_num}: Name is required")
                continue

            # Validate amount
            try:
                amount = float(row.get('amount', 0))  # type: ignore
                if amount <= 0:
                    errors.append(f"Row {row_num}: Amount must be positive")
                    continue
            except (TypeError, ValueError):
                errors.append(f"Row {row_num}: Invalid amount")
                continue

            # Validate frequency
            frequency = str(row.get('frequency', '')).strip().lower()
            if frequency not in ['monthly', 'yearly']:
                errors.append(f"Row {row_num}: Frequency must be 'monthly' or 'yearly'")
                continue

            # Validate interval
            try:
                interval = int(row.get('interval', 0))  # type: ignore
                if interval <= 0:
                    errors.append(f"Row {row_num}: Interval must be positive")
                    continue
            except (TypeError, ValueError):
                errors.append(f"Row {row_num}: Invalid interval")
                continue

            # Validate due_day
            try:
                due_day = int(row.get('due_day', 0))  # type: ignore
                if due_day < 1 or due_day > 31:
                    errors.append(f"Row {row_num}: Due day must be between 1 and 31")
                    continue
            except (TypeError, ValueError):
                errors.append(f"Row {row_num}: Invalid due day")
                continue

            # Validate due_month (optional for monthly, required for yearly)
            due_month: Optional[int] = None
            if 'due_month' in df.columns and pd.notna(row.get('due_month')):
                try:
                    due_month = int(row.get('due_month'))  # type: ignore
                    if due_month < 1 or due_month > 12:
                        errors.append(f"Row {row_num}: Due month must be between 1 and 12")
                        continue
                except (TypeError, ValueError):
                    errors.append(f"Row {row_num}: Invalid due month")
                    continue

            # Validate frequency-specific rules
            if frequency == 'monthly' and due_month is not None:
                errors.append(f"Row {row_num}: Monthly subscriptions cannot have due_month")
                continue
            if frequency == 'yearly' and due_month is None:
                errors.append(f"Row {row_num}: Yearly subscriptions require due_month")
                continue

            # Validate status
            status = str(row.get('status', '')).strip().lower()
            if status not in ['active', 'cancelled']:
                errors.append(f"Row {row_num}: Status must be 'active' or 'cancelled'")
                continue

            valid_rows.append({
                'name': name,
                'amount': amount,
                'frequency': frequency,
                'interval': interval,
                'due_day': due_day,
                'due_month': due_month,
                'status': status,
            })

        return valid_rows, errors

# Made with Bob
