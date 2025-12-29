"""Subscription service with business logic including CSV import/export"""
import pandas as pd
import io
from typing import Any
from core.models.subscription import Subscription, Interval
from core.models.user import User
from core.models.category import Category
from core.repositories.subscription import SubscriptionRepository
from core.repositories.user import UserRepository
from core.repositories.category import CategoryRepository
from core.utils import generate_uid


class SubscriptionService:
    """Service for subscription business logic"""
    
    def __init__(self) -> None:
        self.subscription_repo = SubscriptionRepository()
        self.user_repo = UserRepository()
        self.category_repo = CategoryRepository()
    
    def export_to_csv(self) -> str:
        """Export all subscriptions to CSV format"""
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
        """Import subscriptions from CSV content"""
        valid_rows, errors = self._parse_csv(csv_content)
        
        created_count = 0
        failed_count = len(errors)  # Count parsing errors as failures
        import_errors: list[str] = errors.copy()
        
        for row_data in valid_rows:
            try:
                # Find user by name
                user: User | None = self._find_user_by_name(name=row_data['user'])
                if not user:
                    import_errors.append(f"User not found: {row_data['user']}")
                    failed_count += 1
                    continue
                
                # Find category by name
                category: Category | None = self._find_category_by_name(name=row_data['category'])
                if not category:
                    import_errors.append(f"Category not found: {row_data['category']}")
                    failed_count += 1
                    continue
                
                # Create subscription
                uid: str = generate_uid()
                subscription: Subscription = Subscription(
                    uid=uid,
                    name=row_data['name'],
                    amount=row_data['amount'],
                    interval=Interval(value=row_data['interval']),
                    multiplier=row_data['multiplier'],
                    user=user,
                    category=category,
                    active=row_data['active']
                )
                self.subscription_repo.create(entity=subscription)
                created_count += 1
            except Exception as e:
                import_errors.append(f"Failed to create subscription '{row_data['name']}': {str(e)}")
                failed_count += 1
        
        return {
            "created": created_count,
            "failed": failed_count,
            "errors": import_errors
        }
    
    def _parse_csv(self, csv_content: str) -> tuple[list[dict[str, Any]], list[str]]:
        """Parse CSV content and validate data"""
        valid_rows: list[Any] = []
        errors: list[Any] = []
        
        try:
            df: pd.DataFrame = pd.read_csv(io.StringIO(csv_content))
            
            required_cols: list[str] = ['name', 'amount', 'interval', 'user', 'category']
            missing_cols: list[str] = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                errors.append(f"Missing required columns: {', '.join(missing_cols)}")
                return valid_rows, errors
            
            for idx, row in df.iterrows():
                row_num: int = int(idx) + 2
                try:
                    # Validate name
                    if pd.isna(row['name']) or not str(row['name']).strip():
                        errors.append(f"Row {row_num}: Name is required")
                        continue
                    
                    # Validate amount
                    if pd.isna(row['amount']):
                        errors.append(f"Row {row_num}: Amount is required")
                        continue
                    
                    amount: float = float(row['amount'])
                    if amount <= 0:
                        errors.append(f"Row {row_num}: Amount must be positive")
                        continue
                    
                    # Validate interval
                    interval: str = str(row['interval']).lower()
                    if interval not in ['daily', 'weekly', 'monthly', 'yearly']:
                        errors.append(f"Row {row_num}: Invalid interval '{interval}'")
                        continue
                    
                    # Validate multiplier
                    multiplier: int = int(row['multiplier']) if 'multiplier' in df.columns and not pd.isna(row['multiplier']) else 1
                    if multiplier < 1:
                        errors.append(f"Row {row_num}: Multiplier must be at least 1")
                        continue
                    
                    # Validate user
                    if pd.isna(row['user']):
                        errors.append(f"Row {row_num}: User is required")
                        continue
                    
                    # Validate category
                    if pd.isna(row['category']):
                        errors.append(f"Row {row_num}: Category is required")
                        continue
                    
                    # Parse active
                    active: bool = bool(row['active']) if 'active' in df.columns and not pd.isna(row['active']) else True
                    
                    valid_rows.append({
                        'name': str(row['name']).strip(),
                        'amount': amount,
                        'interval': interval,
                        'multiplier': multiplier,
                        'user': str(row['user']).strip(),
                        'category': str(row['category']).strip(),
                        'active': active
                    })
                    
                except (ValueError, TypeError) as e:
                    errors.append(f"Row {row_num}: Invalid data format - {str(e)}")
                except Exception as e:
                    errors.append(f"Row {row_num}: Error - {str(e)}")
        
        except Exception as e:
            errors.append(f"CSV parsing error: {str(e)}")
        
        return valid_rows, errors
    
    def _find_user_by_name(self, name: str) -> User | None:
        """Find user by name"""
        for user in self.user_repo.get_all():
            if user.name == name:
                return user
        return None
    
    def _find_category_by_name(self, name: str) -> Category | None:
        """Find category by name"""
        for category in self.category_repo.get_all():
            if category.name == name:
                return category
        return None

# Made with Bob
