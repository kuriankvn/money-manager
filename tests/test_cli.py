import unittest
from unittest.mock import patch, MagicMock
from typing import Any
import os
import tempfile
from money_manager.cli import MoneyManagerCLI
from money_manager.database import init_database
from money_manager.models import TransactionType, User, Category, Transaction


class TestUserManagement(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.cli = MoneyManagerCLI()
    
    def tearDown(self) -> None:
        if os.path.exists(path=self.test_db.name):
            os.unlink(path=self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    @patch(target='builtins.input', side_effect=['John Doe'])
    @patch(target='money_manager.cli.pause')
    def test_create_user_success(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_user()
        users: list[User] = self.cli.user_repo.get_all()
        self.assertEqual(first=len(users), second=1)
        self.assertEqual(first=users[0].name, second='John Doe')
    
    @patch(target='builtins.input', side_effect=['Alice', 'Bob', 'Charlie'])
    @patch(target='money_manager.cli.pause')
    def test_list_users_with_data(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_user()
        self.cli.create_user()
        self.cli.create_user()
        
        users: list[User] = self.cli.user_repo.get_all()
        self.assertEqual(first=len(users), second=3)
        self.assertIn(member='Alice', container=[u.name for u in users])
        self.assertIn(member='Bob', container=[u.name for u in users])
        self.assertIn(member='Charlie', container=[u.name for u in users])
    
    @patch(target='builtins.input', side_effect=['Original Name', '1', 'Updated Name'])
    @patch(target='money_manager.cli.pause')
    def test_update_user_success(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_user()
        self.cli.update_user()
        
        users: list[User] = self.cli.user_repo.get_all()
        self.assertEqual(first=len(users), second=1)
        self.assertEqual(first=users[0].name, second='Updated Name')
    
    @patch(target='builtins.input', side_effect=['Delete Me', '1', 'yes'])
    @patch(target='money_manager.cli.pause')
    def test_delete_user_success(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_user()
        users_before: list[User] = self.cli.user_repo.get_all()
        self.assertEqual(first=len(users_before), second=1)
        
        self.cli.delete_user()
        users_after: list[User] = self.cli.user_repo.get_all()
        self.assertEqual(first=len(users_after), second=0)


class TestCategoryManagement(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db: Any = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.cli: MoneyManagerCLI = MoneyManagerCLI()
    
    def tearDown(self) -> None:
        if os.path.exists(path=self.test_db.name):
            os.unlink(path=self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    @patch(target='builtins.input', side_effect=['Salary', '1'])
    @patch(target='money_manager.cli.pause')
    def test_create_category_success(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_category()
        categories: list[Category] = self.cli.category_repo.get_all()
        self.assertEqual(first=len(categories), second=1)
        self.assertEqual(first=categories[0].name, second='Salary')
        self.assertEqual(first=categories[0].type, second=TransactionType.INCOME)
    
    @patch(target='builtins.input', side_effect=['Salary', '1', 'Food', '2', 'Transport', '2'])
    @patch(target='money_manager.cli.pause')
    def test_list_categories_with_data(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_category()
        self.cli.create_category()
        self.cli.create_category()
        
        categories: list[Category] = self.cli.category_repo.get_all()
        self.assertEqual(first=len(categories), second=3)
        
        salary_category: Category = next(c for c in categories if c.name == 'Salary')
        food_category: Category = next(c for c in categories if c.name == 'Food')
        transport_category: Category = next(c for c in categories if c.name == 'Transport')
        
        self.assertEqual(first=salary_category.name, second='Salary')
        self.assertEqual(first=food_category.name, second='Food')
        self.assertEqual(first=transport_category.name, second='Transport')
        
        self.assertEqual(first=salary_category.type, second=TransactionType.INCOME)
        self.assertEqual(first=food_category.type, second=TransactionType.EXPENSE)
        self.assertEqual(first=transport_category.type, second=TransactionType.EXPENSE)
    
    @patch(target='builtins.input', side_effect=['Old Category', '1', '1', 'Updated Category', '2'])
    @patch(target='money_manager.cli.pause')
    def test_update_category_success(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_category()
        self.cli.update_category()
        
        categories: list[Category] = self.cli.category_repo.get_all()
        self.assertEqual(first=len(categories), second=1)
        self.assertEqual(first=categories[0].name, second='Updated Category')
        self.assertEqual(first=categories[0].type, second=TransactionType.EXPENSE)
    
    @patch(target='builtins.input', side_effect=['Delete Me', '2', '1', 'yes'])
    @patch(target='money_manager.cli.pause')
    def test_delete_category_success(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_category()
        categories_before: list[Category] = self.cli.category_repo.get_all()
        self.assertEqual(first=len(categories_before), second=1)
        
        self.cli.delete_category()
        categories_after: list[Category] = self.cli.category_repo.get_all()
        self.assertEqual(first=len(categories_after), second=0)


class TestTransactionManagement(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db: Any = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.cli: MoneyManagerCLI = MoneyManagerCLI()
        with patch(target='builtins.input', side_effect=['Test User', 'Groceries', '2']):
            with patch(target='money_manager.cli.pause'):
                self.cli.create_user()
                self.cli.create_category()
    
    def tearDown(self) -> None:
        if os.path.exists(path=self.test_db.name):
            os.unlink(path=self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    @patch(target='builtins.input', side_effect=['1', '1', 'Grocery Shopping', '50.75', '2023-11-15 10:30'])
    @patch(target='money_manager.cli.pause')
    def test_create_transaction_success(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_transaction()
        transactions: list[Transaction] = self.cli.transaction_repo.get_all()
        self.assertEqual(first=len(transactions), second=1)
        self.assertEqual(first=transactions[0].name, second='Grocery Shopping')
        self.assertEqual(first=transactions[0].amount, second=50.75)
    
    @patch(target='builtins.input', side_effect=[
        '1', '1', 'Transaction 1', '100.00', '2023-11-15 10:00',
        '1', '1', 'Transaction 2', '200.00', '2023-11-16 11:00',
        '1', '1', 'Transaction 3', '300.00', '2023-11-17 12:00'
    ])
    @patch(target='money_manager.cli.pause')
    def test_list_transactions_with_data(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_transaction()
        self.cli.create_transaction()
        self.cli.create_transaction()
        
        transactions: list[Transaction] = self.cli.transaction_repo.get_all()
        self.assertEqual(first=len(transactions), second=3)
        
        transaction_1: Transaction = next(t for t in transactions if t.name == 'Transaction 1')
        transaction_2: Transaction = next(t for t in transactions if t.name == 'Transaction 2')
        transaction_3: Transaction = next(t for t in transactions if t.name == 'Transaction 3')
        
        self.assertEqual(first=transaction_1.name, second='Transaction 1')
        self.assertEqual(first=transaction_2.name, second='Transaction 2')
        self.assertEqual(first=transaction_3.name, second='Transaction 3')
        
        self.assertEqual(first=transaction_1.amount, second=100.00)
        self.assertEqual(first=transaction_2.amount, second=200.00)
        self.assertEqual(first=transaction_3.amount, second=300.00)
        
        from money_manager.utils import epoch_to_datetime
        self.assertEqual(first=epoch_to_datetime(epoch=transaction_1.datetime), second='2023-11-15 10:00:00')
        self.assertEqual(first=epoch_to_datetime(epoch=transaction_2.datetime), second='2023-11-16 11:00:00')
        self.assertEqual(first=epoch_to_datetime(epoch=transaction_3.datetime), second='2023-11-17 12:00:00')
        
        self.assertEqual(first=transaction_1.user.name, second='Test User')
        self.assertEqual(first=transaction_1.category.name, second='Groceries')
    
    @patch(target='builtins.input', side_effect=[
        '1', '1', 'Original Transaction', '100.00', '2023-11-15 10:00',
        '1', '1', '1', 'Updated Transaction', '150.25', '2023-11-16 12:00'
    ])
    @patch(target='money_manager.cli.pause')
    def test_update_transaction_success(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_transaction()
        self.cli.update_transaction()
        
        transactions: list[Transaction] = self.cli.transaction_repo.get_all()
        self.assertEqual(first=len(transactions), second=1)
        self.assertEqual(first=transactions[0].name, second='Updated Transaction')
        self.assertEqual(first=transactions[0].amount, second=150.25)
        self.assertEqual(first=transactions[0].user.name, second='Test User')
        self.assertEqual(first=transactions[0].category.name, second='Groceries')
    
    @patch(target='builtins.input', side_effect=[
        '1', '1', 'Delete Me', '99.99', '2023-11-15 10:00',
        '1', 'yes'
    ])
    @patch(target='money_manager.cli.pause')
    def test_delete_transaction_success(self, mock_pause: MagicMock, mock_input: MagicMock) -> None:
        self.cli.create_transaction()
        transactions_before: list[Transaction] = self.cli.transaction_repo.get_all()
        self.assertEqual(first=len(transactions_before), second=1)
        
        self.cli.delete_transaction()
        transactions_after: list[Transaction] = self.cli.transaction_repo.get_all()
        self.assertEqual(first=len(transactions_after), second=0)


if __name__ == '__main__':
    unittest.main()
