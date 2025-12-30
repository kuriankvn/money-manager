import unittest
import os
import tempfile
from datetime import date
from fastapi.testclient import TestClient
from core.main import app
from core.storage.init_db import init_database


class TestSubscriptionAPI(unittest.TestCase):
    
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
        response = self.client.post('/subscriptions/', json={
            'name': 'Netflix',
            'amount': 15.99,
            'frequency': 'monthly',
            'interval': 1,
            'due_day': 15,
            'due_month': None,
            'status': 'active'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'Netflix')
        self.assertEqual(data['amount'], 15.99)
    
    def test_get_by_id(self) -> None:
        create_response = self.client.post('/subscriptions/', json={
            'name': 'Spotify',
            'amount': 9.99,
            'frequency': 'monthly',
            'interval': 1,
            'due_day': 1,
            'due_month': None,
            'status': 'active'
        })
        uid = create_response.json()['uid']
        
        response = self.client.get(f'/subscriptions/{uid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Spotify')
    
    def test_get_all(self) -> None:
        self.client.post('/subscriptions/', json={
            'name': 'Service 1', 'amount': 10.0, 'frequency': 'monthly',
            'interval': 1, 'due_day': 1, 'due_month': None, 'status': 'active'
        })
        self.client.post('/subscriptions/', json={
            'name': 'Service 2', 'amount': 20.0, 'frequency': 'yearly',
            'interval': 1, 'due_day': 15, 'due_month': 6, 'status': 'active'
        })
        
        response = self.client.get('/subscriptions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
    
    def test_update(self) -> None:
        create_response = self.client.post('/subscriptions/', json={
            'name': 'Original', 'amount': 100.0, 'frequency': 'monthly',
            'interval': 1, 'due_day': 1, 'due_month': None, 'status': 'active'
        })
        uid = create_response.json()['uid']
        
        response = self.client.put(f'/subscriptions/{uid}', json={
            'name': 'Updated', 'amount': 100.0, 'frequency': 'monthly',
            'interval': 1, 'due_day': 1, 'due_month': None, 'status': 'active'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Updated')
    
    def test_delete(self) -> None:
        create_response = self.client.post('/subscriptions/', json={
            'name': 'Delete Me', 'amount': 99.99, 'frequency': 'monthly',
            'interval': 1, 'due_day': 1, 'due_month': None, 'status': 'active'
        })
        uid = create_response.json()['uid']
        
        response = self.client.delete(f'/subscriptions/{uid}')
        self.assertEqual(response.status_code, 204)


class TestSubscriptionInstanceAPI(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.client = TestClient(app)
        
        # Create subscription dependency
        sub_response = self.client.post('/subscriptions/', json={
            'name': 'Netflix',
            'amount': 15.99,
            'frequency': 'monthly',
            'interval': 1,
            'due_day': 15,
            'due_month': None,
            'status': 'active'
        })
        self.subscription_uid = sub_response.json()['uid']
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        response = self.client.post('/subscription-instances/', json={
            'subscription_id': self.subscription_uid,
            'amount': 15.99,
            'due_date': '2024-01-15',
            'transaction_id': None,
            'status': 'due'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['amount'], 15.99)
        self.assertEqual(data['status'], 'due')
    
    def test_get_by_id(self) -> None:
        create_response = self.client.post('/subscription-instances/', json={
            'subscription_id': self.subscription_uid,
            'amount': 15.99,
            'due_date': '2024-01-15',
            'transaction_id': None,
            'status': 'due'
        })
        uid = create_response.json()['uid']
        
        response = self.client.get(f'/subscription-instances/{uid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['amount'], 15.99)
    
    def test_get_all(self) -> None:
        self.client.post('/subscription-instances/', json={
            'subscription_id': self.subscription_uid, 'amount': 15.99,
            'due_date': '2024-01-15', 'transaction_id': None, 'status': 'due'
        })
        self.client.post('/subscription-instances/', json={
            'subscription_id': self.subscription_uid, 'amount': 15.99,
            'due_date': '2024-02-15', 'transaction_id': None, 'status': 'due'
        })
        
        response = self.client.get('/subscription-instances/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
    
    def test_update(self) -> None:
        create_response = self.client.post('/subscription-instances/', json={
            'subscription_id': self.subscription_uid, 'amount': 15.99,
            'due_date': '2024-01-15', 'transaction_id': None, 'status': 'due'
        })
        uid = create_response.json()['uid']
        
        response = self.client.put(f'/subscription-instances/{uid}', json={
            'subscription_id': self.subscription_uid, 'amount': 15.99,
            'due_date': '2024-01-15', 'transaction_id': None, 'status': 'paid'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'paid')
    
    def test_delete(self) -> None:
        create_response = self.client.post('/subscription-instances/', json={
            'subscription_id': self.subscription_uid, 'amount': 15.99,
            'due_date': '2024-01-15', 'transaction_id': None, 'status': 'due'
        })
        uid = create_response.json()['uid']
        
        response = self.client.delete(f'/subscription-instances/{uid}')
        self.assertEqual(response.status_code, 204)


if __name__ == '__main__':
    unittest.main()

# Made with Bob