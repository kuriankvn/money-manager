import unittest
import os
import tempfile
from datetime import date
from fastapi.testclient import TestClient
from core.main import app
from core.storage.init_db import init_database


class TestCategoryAPI(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.client = TestClient(app)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        response = self.client.post('/categories/', json={'name': 'Groceries'})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'Groceries')
        self.assertIn('uid', data)
    
    def test_get_by_id(self) -> None:
        create_response = self.client.post('/categories/', json={'name': 'Food'})
        uid = create_response.json()['uid']
        
        response = self.client.get(f'/categories/{uid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Food')
    
    def test_get_all(self) -> None:
        self.client.post('/categories/', json={'name': 'Salary'})
        self.client.post('/categories/', json={'name': 'Entertainment'})
        
        response = self.client.get('/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
    
    def test_update(self) -> None:
        create_response = self.client.post('/categories/', json={'name': 'Original'})
        uid = create_response.json()['uid']
        
        response = self.client.put(f'/categories/{uid}', json={'name': 'Updated'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Updated')
    
    def test_delete(self) -> None:
        create_response = self.client.post('/categories/', json={'name': 'Delete Me'})
        uid = create_response.json()['uid']
        
        response = self.client.delete(f'/categories/{uid}')
        self.assertEqual(response.status_code, 204)


class TestAccountAPI(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.client = TestClient(app)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        response = self.client.post('/accounts/', json={'name': 'Checking'})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'Checking')
        self.assertIn('uid', data)
    
    def test_get_by_id(self) -> None:
        create_response = self.client.post('/accounts/', json={'name': 'Savings'})
        uid = create_response.json()['uid']
        
        response = self.client.get(f'/accounts/{uid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Savings')
    
    def test_get_all(self) -> None:
        self.client.post('/accounts/', json={'name': 'Checking'})
        self.client.post('/accounts/', json={'name': 'Savings'})
        
        response = self.client.get('/accounts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
    
    def test_update(self) -> None:
        create_response = self.client.post('/accounts/', json={'name': 'Original'})
        uid = create_response.json()['uid']
        
        response = self.client.put(f'/accounts/{uid}', json={'name': 'Updated'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Updated')
    
    def test_delete(self) -> None:
        create_response = self.client.post('/accounts/', json={'name': 'Delete Me'})
        uid = create_response.json()['uid']
        
        response = self.client.delete(f'/accounts/{uid}')
        self.assertEqual(response.status_code, 204)


class TestTransactionAPI(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.client = TestClient(app)
        
        # Create dependencies
        category_response = self.client.post('/categories/', json={'name': 'Groceries'})
        self.category_uid = category_response.json()['uid']
        
        account_response = self.client.post('/accounts/', json={'name': 'Checking'})
        self.account_uid = account_response.json()['uid']
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        response = self.client.post('/transactions/', json={
            'name': 'Grocery Shopping',
            'amount': 50.75,
            'date': '2024-01-15',
            'account_id': self.account_uid,
            'category_id': self.category_uid
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'Grocery Shopping')
        self.assertEqual(data['amount'], 50.75)
    
    def test_get_by_id(self) -> None:
        create_response = self.client.post('/transactions/', json={
            'name': 'Coffee',
            'amount': 5.50,
            'date': '2024-01-16',
            'account_id': self.account_uid,
            'category_id': self.category_uid
        })
        uid = create_response.json()['uid']
        
        response = self.client.get(f'/transactions/{uid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Coffee')
    
    def test_get_all(self) -> None:
        self.client.post('/transactions/', json={
            'name': 'Item 1', 'amount': 10.0, 'date': '2024-01-01',
            'account_id': self.account_uid, 'category_id': self.category_uid
        })
        self.client.post('/transactions/', json={
            'name': 'Item 2', 'amount': 20.0, 'date': '2024-01-02',
            'account_id': self.account_uid, 'category_id': self.category_uid
        })
        
        response = self.client.get('/transactions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
    
    def test_update(self) -> None:
        create_response = self.client.post('/transactions/', json={
            'name': 'Original', 'amount': 100.0, 'date': '2024-01-01',
            'account_id': self.account_uid, 'category_id': self.category_uid
        })
        uid = create_response.json()['uid']
        
        response = self.client.put(f'/transactions/{uid}', json={
            'name': 'Updated', 'amount': 100.0, 'date': '2024-01-01',
            'account_id': self.account_uid, 'category_id': self.category_uid
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Updated')
    
    def test_delete(self) -> None:
        create_response = self.client.post('/transactions/', json={
            'name': 'Delete Me', 'amount': 99.99, 'date': '2024-01-01',
            'account_id': self.account_uid, 'category_id': self.category_uid
        })
        uid = create_response.json()['uid']
        
        response = self.client.delete(f'/transactions/{uid}')
        self.assertEqual(response.status_code, 204)


if __name__ == '__main__':
    unittest.main()

# Made with Bob