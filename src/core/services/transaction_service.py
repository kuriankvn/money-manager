
import pandas as pd
import io
from datetime import datetime
from typing import Any, Optional
from core.models import Transaction, TransactionType, User, Category
from core.repositories import TransactionRepository, UserRepository, CategoryRepository
from core.utils import generate_uid
from core.services.csv_validators import CSVValidator


class TransactionService:
    def __init__(self) -> None:
        self.transaction_repo = TransactionRepository()
    
    def export_to_csv(self) -> str:
        transactions: list[Transaction] = self.transaction_repo.get_all()
        data: list[dict[str, Any]] = [{
            'name': txn.name,
            'amount': txn.amount,
            'date': datetime.fromtimestamp(timestamp=txn.date).strftime(format='%d/%m/%Y'),
            'type': txn.type.value,
            'user': txn.user.name,
            'category': txn.category.name
        } for txn in transactions]
        
        df: pd.DataFrame = pd.DataFrame(data)
        return df.to_csv(index=False)
    
    def import_from_csv(self, csv_content: str) -> dict[str, Any]:
        valid_rows, errors = self._validate_csv(csv_content)
        
        created_count = 0
        failed_count: int = len(errors)
        
        for row_data in valid_rows:
            try:
                uid: str = generate_uid()
                transaction: Transaction = Transaction(
                    uid=uid,
                    name=row_data['name'],
                    amount=row_data['amount'],
                    date=row_data['date'],
                    type=TransactionType(value=row_data['type']),
                    user=row_data['user'],
                    category=row_data['category']
                )
                self.transaction_repo.create(entity=transaction)
                created_count += 1
            except Exception as e:
                errors.append(f"Failed to create transaction '{row_data['name']}': {str(e)}")
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

        required_cols: list[str] = ['name', 'amount', 'date', 'type', 'user', 'category']
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

            date: Optional[datetime] = CSVValidator.validate_date(value=row.get(key='date'))
            if date is None:
                errors.append(f"Row {row_num}: Date must be in DD/MM/YYYY format")
                continue

            txn_type: Optional[str] = CSVValidator.validate_enum(
                value=row.get(key='type'), allowed=['income', 'expense'])
            if txn_type is None:
                errors.append(f"Row {row_num}: Type must be 'income' or 'expense'")
                continue

            user: Optional[User] = validator.validate_user(value=row.get(key='user'))
            if user is None:
                errors.append(f"Row {row_num}: User must exist")
                continue

            category: Optional[Category] = validator.validate_category(value=row.get(key='category'))
            if category is None:
                errors.append(f"Row {row_num}: Category must exist")
                continue

            valid_rows.append({
                'name': name,
                'amount': amount,
                'date': date.timestamp(),
                'type': txn_type,
                'user': user,
                'category': category,
            })

        return valid_rows, errors
