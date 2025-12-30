import pandas as pd
import io
from datetime import date
from typing import Any, Optional
from core.domain import Transaction, Account, Category
from core.repositories import TransactionRepository, AccountRepository, CategoryRepository
from core.utils import generate_uid


class TransactionService:
    def __init__(self) -> None:
        self.transaction_repo = TransactionRepository()
        self.account_repo = AccountRepository()
        self.category_repo = CategoryRepository()
    
    def export_to_csv(self) -> str:
        """Export all transactions to CSV format"""
        transactions: list[Transaction] = self.transaction_repo.get_all()
        
        # Get account and category names
        accounts = {acc.uid: acc.name for acc in self.account_repo.get_all()}
        categories = {cat.uid: cat.name for cat in self.category_repo.get_all()}
        
        data: list[dict[str, Any]] = [{
            'name': txn.name,
            'amount': txn.amount,
            'date': txn.date.isoformat() if isinstance(txn.date, date) else str(txn.date),
            'account': accounts.get(txn.account_id, ''),
            'category': categories.get(txn.category_id, '')
        } for txn in transactions]
        
        df: pd.DataFrame = pd.DataFrame(data)
        return df.to_csv(index=False)
    
    def import_from_csv(self, csv_content: str) -> dict[str, Any]:
        """Import transactions from CSV content"""
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
                    account_id=row_data['account_id'],
                    category_id=row_data['category_id']
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
        """Validate CSV content and return valid rows with errors"""
        errors: list[str] = []
        valid_rows: list[dict[str, Any]] = []

        try:
            df: pd.DataFrame = pd.read_csv(io.StringIO(csv_content))
        except Exception as e:
            return [], [f"CSV parsing error: {str(e)}"]

        required_cols: list[str] = ['name', 'amount', 'date', 'account', 'category']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return [], errors

        # Build lookup maps
        accounts = {acc.name: acc.uid for acc in self.account_repo.get_all()}
        categories = {cat.name: cat.uid for cat in self.category_repo.get_all()}

        for idx, row in df.iterrows():
            row_num: int = int(idx) + 2

            # Validate name
            name = str(row.get('name', '')).strip()
            if not name:
                errors.append(f"Row {row_num}: Name is required")
                continue

            # Validate amount
            try:
                amount = float(row.get('amount', 0))
                if amount <= 0:
                    errors.append(f"Row {row_num}: Amount must be positive")
                    continue
            except (TypeError, ValueError):
                errors.append(f"Row {row_num}: Invalid amount")
                continue

            # Validate date
            try:
                date_val = pd.to_datetime(row.get('date')).date()
            except Exception:
                errors.append(f"Row {row_num}: Invalid date format (use YYYY-MM-DD)")
                continue

            # Validate account
            account_name = str(row.get('account', '')).strip()
            account_id = accounts.get(account_name)
            if not account_id:
                errors.append(f"Row {row_num}: Account '{account_name}' not found")
                continue

            # Validate category
            category_name = str(row.get('category', '')).strip()
            category_id = categories.get(category_name)
            if not category_id:
                errors.append(f"Row {row_num}: Category '{category_name}' not found")
                continue

            valid_rows.append({
                'name': name,
                'amount': amount,
                'date': date_val,
                'account_id': account_id,
                'category_id': category_id,
            })

        return valid_rows, errors

# Made with Bob
