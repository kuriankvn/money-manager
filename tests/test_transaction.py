import unittest
import os
import tempfile
from core.database import init_user_tables, init_category_tables, init_transaction_tables
from core.models import User, Category, Transaction, TransactionType
from core.repositories import UserRepository, CategoryRepository, TransactionRepository
from fastapi.testclient import TestClient
from core.main import app


class TestTransaction(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_user_tables()
        init_category_tables()
        init_transaction_tables()
        
        self.user_repo = UserRepository()
        self.category_repo = CategoryRepository()
        self.repo = TransactionRepository()
        self.client = TestClient(app)
        
        self.user = User(uid='user-1', name='Test User')
        self.category = Category(uid='cat-1', name='Groceries', user=self.user)
        self.user_repo.create(self.user)
        self.category_repo.create(self.category)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create_transaction_repository(self) -> None:
        transaction = Transaction(
            uid='txn-1',
            name='Grocery Shopping',
            amount=50.75,
            datetime=1700000000.0,
            type=TransactionType.EXPENSE,
            user=self.user,
            category=self.category
        )
        uid = self.repo.create(transaction)
        self.assertEqual(uid, 'txn-1')
    
    def test_create_transaction_api(self) -> None:
        response = self.client.post("/transactions/", json={
            "name": "Grocery Shopping",
            "amount": 50.75,
            "datetime": 1700000000.0,
            "type": "expense",
            "user_uid": self.user.uid,
            "category_uid": self.category.uid
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Grocery Shopping")
        self.assertEqual(data["amount"], 50.75)
    
    def test_get_transaction_by_id_repository(self) -> None:
        transaction = Transaction(
            uid='txn-2',
            name='Coffee',
            amount=5.50,
            datetime=1700000000.0,
            type=TransactionType.EXPENSE,
            user=self.user,
            category=self.category
        )
        self.repo.create(transaction)
        retrieved = self.repo.get_by_id('txn-2')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, 'Coffee')
        self.assertEqual(retrieved.amount, 5.50)
    
    def test_get_transaction_by_id_api(self) -> None:
        create_response = self.client.post("/transactions/", json={
            "name": "Coffee",
            "amount": 5.50,
            "datetime": 1700000000.0,
            "type": "expense",
            "user_uid": self.user.uid,
            "category_uid": self.category.uid
        })
        uid = create_response.json()["uid"]
        response = self.client.get(f"/transactions/{uid}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Coffee")
        self.assertEqual(data["amount"], 5.50)
    
    def test_get_all_transactions_repository(self) -> None:
        txn1 = Transaction(uid='txn-3', name='Item 1', amount=10.0, datetime=1700000000.0, type=TransactionType.EXPENSE, user=self.user, category=self.category)
        txn2 = Transaction(uid='txn-4', name='Item 2', amount=20.0, datetime=1700000000.0, type=TransactionType.INCOME, user=self.user, category=self.category)
        self.repo.create(txn1)
        self.repo.create(txn2)
        transactions = self.repo.get_all()
        self.assertEqual(len(transactions), 2)
    
    def test_get_all_transactions_api(self) -> None:
        self.client.post("/transactions/", json={
            "name": "Item 1", "amount": 10.0, "datetime": 1700000000.0,
            "type": "expense", "user_uid": self.user.uid, "category_uid": self.category.uid
        })
        self.client.post("/transactions/", json={
            "name": "Item 2", "amount": 20.0, "datetime": 1700000000.0,
            "type": "income", "user_uid": self.user.uid, "category_uid": self.category.uid
        })
        response = self.client.get("/transactions/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
    
    def test_update_transaction_repository(self) -> None:
        transaction = Transaction(
            uid='txn-5',
            name='Original',
            amount=100.0,
            datetime=1700000000.0,
            type=TransactionType.EXPENSE,
            user=self.user,
            category=self.category
        )
        self.repo.create(transaction)
        transaction.name = 'Updated'
        transaction.amount = 150.0
        result = self.repo.update(transaction)
        self.assertTrue(result)
        updated = self.repo.get_by_id('txn-5')
        self.assertEqual(updated.name, 'Updated')
        self.assertEqual(updated.amount, 150.0)
    
    def test_update_transaction_api(self) -> None:
        create_response = self.client.post("/transactions/", json={
            "name": "Original", "amount": 100.0, "datetime": 1700000000.0,
            "type": "expense", "user_uid": self.user.uid, "category_uid": self.category.uid
        })
        uid = create_response.json()["uid"]
        response = self.client.put(f"/transactions/{uid}", json={
            "name": "Updated", "amount": 150.0, "datetime": 1700000000.0,
            "type": "expense", "user_uid": self.user.uid, "category_uid": self.category.uid
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated")
        self.assertEqual(data["amount"], 150.0)
    
    def test_delete_transaction_repository(self) -> None:
        transaction = Transaction(
            uid='txn-6',
            name='Delete Me',
            amount=99.99,
            datetime=1700000000.0,
            type=TransactionType.EXPENSE,
            user=self.user,
            category=self.category
        )
        self.repo.create(transaction)
        result = self.repo.delete('txn-6')
        self.assertTrue(result)
        deleted = self.repo.get_by_id('txn-6')
        self.assertIsNone(deleted)
    
    def test_delete_transaction_api(self) -> None:
        create_response = self.client.post("/transactions/", json={
            "name": "Delete Me", "amount": 99.99, "datetime": 1700000000.0,
            "type": "expense", "user_uid": self.user.uid, "category_uid": self.category.uid
        })
        uid = create_response.json()["uid"]
        response = self.client.delete(f"/transactions/{uid}")
        self.assertEqual(response.status_code, 204)
        deleted = self.client.get(f"/transactions/{uid}")
        self.assertEqual(deleted.status_code, 404)


if __name__ == '__main__':
    unittest.main()
