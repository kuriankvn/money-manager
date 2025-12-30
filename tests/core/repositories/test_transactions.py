import unittest
import os
import tempfile
from datetime import date
from core.storage.init_db import init_database
from core.domain import Category, Account, Transaction
from core.repositories import CategoryRepository, AccountRepository, TransactionRepository


class TestCategoryRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.repo = CategoryRepository()
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        category = Category(uid='cat-1', name='Groceries')
        uid = self.repo.create(category)
        self.assertEqual(uid, 'cat-1')
    
    def test_get_by_id(self) -> None:
        category = Category(uid='cat-2', name='Food')
        self.repo.create(category)
        retrieved = self.repo.get_by_id('cat-2')
        self.assertIsNotNone(retrieved)
        if retrieved:
            self.assertEqual(retrieved.name, 'Food')
    
    def test_get_all(self) -> None:
        cat1 = Category(uid='cat-3', name='Salary')
        cat2 = Category(uid='cat-4', name='Entertainment')
        self.repo.create(cat1)
        self.repo.create(cat2)
        categories = self.repo.get_all()
        self.assertEqual(len(categories), 2)
    
    def test_update(self) -> None:
        category = Category(uid='cat-5', name='Original')
        self.repo.create(category)
        category.name = 'Updated'
        result = self.repo.update(category)
        self.assertTrue(result)
    
    def test_delete(self) -> None:
        category = Category(uid='cat-6', name='Delete Me')
        self.repo.create(category)
        result = self.repo.delete('cat-6')
        self.assertTrue(result)


class TestAccountRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.repo = AccountRepository()
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        account = Account(uid='acc-1', name='Checking')
        uid = self.repo.create(account)
        self.assertEqual(uid, 'acc-1')
    
    def test_get_by_id(self) -> None:
        account = Account(uid='acc-2', name='Savings')
        self.repo.create(account)
        retrieved = self.repo.get_by_id('acc-2')
        self.assertIsNotNone(retrieved)
    
    def test_get_all(self) -> None:
        acc1 = Account(uid='acc-3', name='Checking')
        acc2 = Account(uid='acc-4', name='Savings')
        self.repo.create(acc1)
        self.repo.create(acc2)
        accounts = self.repo.get_all()
        self.assertEqual(len(accounts), 2)
    
    def test_update(self) -> None:
        account = Account(uid='acc-5', name='Original')
        self.repo.create(account)
        account.name = 'Updated'
        result = self.repo.update(account)
        self.assertTrue(result)
    
    def test_delete(self) -> None:
        account = Account(uid='acc-6', name='Delete Me')
        self.repo.create(account)
        result = self.repo.delete('acc-6')
        self.assertTrue(result)


class TestTransactionRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        
        self.category_repo = CategoryRepository()
        self.account_repo = AccountRepository()
        self.repo = TransactionRepository()
        
        self.category = Category(uid='cat-1', name='Groceries')
        self.account = Account(uid='acc-1', name='Checking')
        self.category_repo.create(self.category)
        self.account_repo.create(self.account)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        transaction = Transaction(
            uid='txn-1',
            name='Grocery Shopping',
            amount=50.75,
            date=date(2024, 1, 15),
            account_id=self.account.uid,
            category_id=self.category.uid
        )
        uid = self.repo.create(transaction)
        self.assertEqual(uid, 'txn-1')
    
    def test_get_by_id(self) -> None:
        transaction = Transaction(
            uid='txn-2',
            name='Coffee',
            amount=5.50,
            date=date(2024, 1, 16),
            account_id=self.account.uid,
            category_id=self.category.uid
        )
        self.repo.create(transaction)
        retrieved = self.repo.get_by_id('txn-2')
        self.assertIsNotNone(retrieved)
    
    def test_get_all(self) -> None:
        txn1 = Transaction(uid='txn-3', name='Item 1', amount=10.0, 
                          date=date(2024, 1, 1), account_id=self.account.uid, 
                          category_id=self.category.uid)
        txn2 = Transaction(uid='txn-4', name='Item 2', amount=20.0, 
                          date=date(2024, 1, 2), account_id=self.account.uid, 
                          category_id=self.category.uid)
        self.repo.create(txn1)
        self.repo.create(txn2)
        transactions = self.repo.get_all()
        self.assertEqual(len(transactions), 2)
    
    def test_update(self) -> None:
        transaction = Transaction(
            uid='txn-5',
            name='Original',
            amount=100.0,
            date=date(2024, 1, 1),
            account_id=self.account.uid,
            category_id=self.category.uid
        )
        self.repo.create(transaction)
        transaction.name = 'Updated'
        result = self.repo.update(transaction)
        self.assertTrue(result)
    
    def test_delete(self) -> None:
        transaction = Transaction(
            uid='txn-6',
            name='Delete Me',
            amount=99.99,
            date=date(2024, 1, 1),
            account_id=self.account.uid,
            category_id=self.category.uid
        )
        self.repo.create(transaction)
        result = self.repo.delete('txn-6')
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()

# Made with Bob
