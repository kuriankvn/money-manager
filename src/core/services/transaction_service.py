"""Transaction service with business logic including CSV import/export"""
from pandas.core.series import Series
from pandas.core.indexes.datetimes import DatetimeIndex
import pandas as pd
import io
from datetime import datetime
from typing import Any
from core.models.transaction import Transaction, TransactionType
from core.models.user import User
from core.models.category import Category
from core.repositories.transaction import TransactionRepository
from core.repositories.user import UserRepository
from core.repositories.category import CategoryRepository
from core.utils import generate_uid


class TransactionService:
    """Service for transaction business logic"""
    
    def __init__(self) -> None:
        self.transaction_repo = TransactionRepository()
        self.user_repo = UserRepository()
        self.category_repo = CategoryRepository()
    
    def export_to_csv(self) -> str:
        """Export all transactions to CSV format"""
        transactions: list[Transaction] = self.transaction_repo.get_all()
        data: list[dict[str, Any]] = [{
            'name': txn.name,
            'amount': txn.amount,
            'date': datetime.fromtimestamp(timestamp=txn.datetime).strftime(format='%d/%m/%Y'),
            'type': txn.type.value,
            'user': txn.user.name,
            'category': txn.category.name
        } for txn in transactions]
        
        df: pd.DataFrame = pd.DataFrame(data)
        return df.to_csv(index=False)
    
    def import_from_csv(self, csv_content: str) -> dict[str, Any]:
        """Import transactions from CSV content"""
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
                
                # Create transaction
                uid: str = generate_uid()
                transaction: Transaction = Transaction(
                    uid=uid,
                    name=row_data['name'],
                    amount=row_data['amount'],
                    datetime=row_data['datetime'],
                    type=TransactionType(value=row_data['type']),
                    user=user,
                    category=category
                )
                self.transaction_repo.create(entity=transaction)
                created_count += 1
            except Exception as e:
                import_errors.append(f"Failed to create transaction '{row_data['name']}': {str(e)}")
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
            df: pd.DataFrame = pd.read_csv(io.StringIO(initial_value=csv_content))
            
            required_cols: list[str] = ['name', 'amount', 'date', 'type', 'user', 'category']
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
                    
                    # Parse date (mandatory, DD/MM/YYYY format)
                    if pd.isna(row['date']):
                        errors.append(f"Row {row_num}: Date is required")
                        continue
                    
                    try:
                        dt = pd.to_datetime(row['date'], format='%d/%m/%Y')
                        datetime_val = dt.to_pydatetime().timestamp()
                    except Exception as e:
                        errors.append(f"Row {row_num}: Invalid date format (use DD/MM/YYYY) - {str(e)}")
                        continue
                    
                    # Validate type
                    txn_type: str = str(row['type']).lower()
                    if txn_type not in ['income', 'expense']:
                        errors.append(f"Row {row_num}: Invalid type '{txn_type}' (must be 'income' or 'expense')")
                        continue
                    
                    # Validate user
                    if pd.isna(row['user']):
                        errors.append(f"Row {row_num}: User is required")
                        continue
                    
                    # Validate category
                    if pd.isna(row['category']):
                        errors.append(f"Row {row_num}: Category is required")
                        continue
                    
                    valid_rows.append({
                        'name': str(row['name']).strip(),
                        'amount': amount,
                        'datetime': datetime_val,
                        'type': txn_type,
                        'user': str(row['user']).strip(),
                        'category': str(row['category']).strip()
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
