import pandas as pd
import io
from typing import Any, Optional
from core.models import Subscription, Interval, User, Category
from core.repositories import SubscriptionRepository, UserRepository, CategoryRepository
from core.utils import generate_uid
from core.services.csv_validators import CSVValidator


class SubscriptionService:
    def __init__(self) -> None:
        self.subscription_repo = SubscriptionRepository()
    
    def export_to_csv(self) -> str:
        subscriptions: list[Subscription] = self.subscription_repo.get_all()
        data: list[dict[str, Any]] = [{
            'name': sub.name,
            'amount': sub.amount,
            'interval': sub.interval.value,
            'multiplier': sub.multiplier,
            'user': sub.user.name,
            'category': sub.category.name,
            'active': sub.active
        } for sub in subscriptions]
        
        df: pd.DataFrame = pd.DataFrame(data)
        return df.to_csv(index=False)
    
    def import_from_csv(self, csv_content: str) -> dict[str, Any]:
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
                    interval=Interval(value=row_data['interval']),
                    multiplier=row_data['multiplier'],
                    user=row_data['user'],
                    category=row_data['category'],
                    active=row_data['active']
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
        errors: list[str] = []
        valid_rows: list[dict[str, Any]] = []
        validator: CSVValidator = CSVValidator()

        try:
            df: pd.DataFrame = pd.read_csv(io.StringIO(initial_value=csv_content))
        except Exception as e:
            return [], [f"CSV parsing error: {str(e)}"]

        required_cols: list[str] = ['name', 'amount', 'interval', 'user', 'category']
        if not CSVValidator.validate_required_fields(df, required_cols, errors):
            return [], errors

        for idx, row in df.iterrows():
            row_num: int = int(idx) + 2

            name: Optional[str] = CSVValidator.validate_string(value=row.get(key='name'))
            if name is None:
                errors.append(f"Row {row_num}: Name must be a non-empty string")
                continue

            amount: Optional[float] = CSVValidator.validate_float(value=row.get(key='amount'))
            if amount is None:
                errors.append(f"Row {row_num}: Amount must be a positive number")
                continue

            interval: Optional[str] = CSVValidator.validate_enum(
                value=row.get(key='interval'), allowed=['daily', 'weekly', 'monthly', 'yearly'])
            if interval is None:
                errors.append(f"Row {row_num}: Interval must be daily, weekly, monthly or yearly")
                continue

            multiplier: Optional[int] = 1
            if 'multiplier' in df.columns:
                multiplier = CSVValidator.validate_int(value=row.get(key='multiplier'))
                if multiplier is None:
                    errors.append(f"Row {row_num}: Multiplier must be a positive integer")
                    continue

            user: Optional[User] = validator.validate_user(value=row.get(key='user'))
            if user is None:
                errors.append(f"Row {row_num}: User must exist")
                continue

            category: Optional[Category] = validator.validate_category(value=row.get(key='category'))
            if category is None:
                errors.append(f"Row {row_num}: Category must exist")
                continue

            active: Optional[bool] = True
            if 'active' in df.columns:
                active = CSVValidator.validate_boolean(value=row.get(key='active'))
                if active is None:
                    errors.append(f"Row {row_num}: Active must be a boolean")
                    continue

            valid_rows.append({
                'name': name,
                'amount': amount,
                'interval': interval,
                'multiplier': multiplier,
                'user': user,
                'category': category,
                'active': active,
            })

        return valid_rows, errors
