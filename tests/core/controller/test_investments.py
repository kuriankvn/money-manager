import unittest
import os
import tempfile
from datetime import date
from fastapi.testclient import TestClient
from core.main import app
from core.storage.init_db import init_database


class TestInvestmentAPI(unittest.TestCase):
    
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
        response = self.client.post('/investments/', json={
            'name': 'Stock Portfolio',
            'start_date': '2024-01-01',
            'status': 'active'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'Stock Portfolio')
        self.assertEqual(data['status'], 'active')
    
    def test_get_by_id(self) -> None:
        create_response = self.client.post('/investments/', json={
            'name': 'Mutual Fund',
            'start_date': '2024-01-01',
            'status': 'active'
        })
        uid = create_response.json()['uid']
        
        response = self.client.get(f'/investments/{uid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Mutual Fund')
    
    def test_get_all(self) -> None:
        self.client.post('/investments/', json={
            'name': 'Investment 1', 'start_date': '2024-01-01', 'status': 'active'
        })
        self.client.post('/investments/', json={
            'name': 'Investment 2', 'start_date': '2024-01-01', 'status': 'active'
        })
        
        response = self.client.get('/investments/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
    
    def test_update(self) -> None:
        create_response = self.client.post('/investments/', json={
            'name': 'Original', 'start_date': '2024-01-01', 'status': 'active'
        })
        uid = create_response.json()['uid']
        
        response = self.client.put(f'/investments/{uid}', json={
            'name': 'Original', 'start_date': '2024-01-01', 'status': 'closed'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'closed')
    
    def test_delete(self) -> None:
        create_response = self.client.post('/investments/', json={
            'name': 'Delete Me', 'start_date': '2024-01-01', 'status': 'active'
        })
        uid = create_response.json()['uid']
        
        response = self.client.delete(f'/investments/{uid}')
        self.assertEqual(response.status_code, 204)


class TestInvestmentSnapshotAPI(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.client = TestClient(app)
        
        # Create investment dependency
        inv_response = self.client.post('/investments/', json={
            'name': 'Stock Portfolio',
            'start_date': '2024-01-01',
            'status': 'active'
        })
        self.investment_uid = inv_response.json()['uid']
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        response = self.client.post('/investment-snapshots/', json={
            'investment_id': self.investment_uid,
            'date': '2024-01-15',
            'current_value': 10000.50
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['current_value'], 10000.50)
    
    def test_get_by_id(self) -> None:
        create_response = self.client.post('/investment-snapshots/', json={
            'investment_id': self.investment_uid,
            'date': '2024-01-15',
            'current_value': 10000.50
        })
        uid = create_response.json()['uid']
        
        response = self.client.get(f'/investment-snapshots/{uid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['current_value'], 10000.50)
    
    def test_get_all(self) -> None:
        self.client.post('/investment-snapshots/', json={
            'investment_id': self.investment_uid, 'date': '2024-01-15', 'current_value': 10000.0
        })
        self.client.post('/investment-snapshots/', json={
            'investment_id': self.investment_uid, 'date': '2024-02-15', 'current_value': 11000.0
        })
        
        response = self.client.get('/investment-snapshots/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
    
    def test_update(self) -> None:
        create_response = self.client.post('/investment-snapshots/', json={
            'investment_id': self.investment_uid, 'date': '2024-01-15', 'current_value': 10000.0
        })
        uid = create_response.json()['uid']
        
        response = self.client.put(f'/investment-snapshots/{uid}', json={
            'investment_id': self.investment_uid, 'date': '2024-01-15', 'current_value': 12000.0
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['current_value'], 12000.0)
    
    def test_delete(self) -> None:
        create_response = self.client.post('/investment-snapshots/', json={
            'investment_id': self.investment_uid, 'date': '2024-01-15', 'current_value': 10000.0
        })
        uid = create_response.json()['uid']
        
        response = self.client.delete(f'/investment-snapshots/{uid}')
        self.assertEqual(response.status_code, 204)


class TestInvestmentPlanAPI(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.client = TestClient(app)
        
        # Create investment dependency
        inv_response = self.client.post('/investments/', json={
            'name': 'Stock Portfolio',
            'start_date': '2024-01-01',
            'status': 'active'
        })
        self.investment_uid = inv_response.json()['uid']
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        response = self.client.post('/investment-plans/', json={
            'investment_id': self.investment_uid,
            'amount': 500.0,
            'frequency': 'monthly',
            'interval': 1,
            'due_day': 15,
            'due_month': None,
            'status': 'active'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['amount'], 500.0)
        self.assertEqual(data['frequency'], 'monthly')
    
    def test_get_by_id(self) -> None:
        create_response = self.client.post('/investment-plans/', json={
            'investment_id': self.investment_uid,
            'amount': 500.0,
            'frequency': 'monthly',
            'interval': 1,
            'due_day': 15,
            'due_month': None,
            'status': 'active'
        })
        uid = create_response.json()['uid']
        
        response = self.client.get(f'/investment-plans/{uid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['amount'], 500.0)
    
    def test_get_all(self) -> None:
        self.client.post('/investment-plans/', json={
            'investment_id': self.investment_uid, 'amount': 500.0,
            'frequency': 'monthly', 'interval': 1, 'due_day': 15,
            'due_month': None, 'status': 'active'
        })
        self.client.post('/investment-plans/', json={
            'investment_id': self.investment_uid, 'amount': 1000.0,
            'frequency': 'yearly', 'interval': 1, 'due_day': 1,
            'due_month': 1, 'status': 'active'
        })
        
        response = self.client.get('/investment-plans/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
    
    def test_update(self) -> None:
        create_response = self.client.post('/investment-plans/', json={
            'investment_id': self.investment_uid, 'amount': 500.0,
            'frequency': 'monthly', 'interval': 1, 'due_day': 15,
            'due_month': None, 'status': 'active'
        })
        uid = create_response.json()['uid']
        
        response = self.client.put(f'/investment-plans/{uid}', json={
            'investment_id': self.investment_uid, 'amount': 500.0,
            'frequency': 'monthly', 'interval': 1, 'due_day': 15,
            'due_month': None, 'status': 'closed'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'closed')
    
    def test_delete(self) -> None:
        create_response = self.client.post('/investment-plans/', json={
            'investment_id': self.investment_uid, 'amount': 500.0,
            'frequency': 'monthly', 'interval': 1, 'due_day': 15,
            'due_month': None, 'status': 'active'
        })
        uid = create_response.json()['uid']
        
        response = self.client.delete(f'/investment-plans/{uid}')
        self.assertEqual(response.status_code, 204)


class TestInvestmentPlanInstanceAPI(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.client = TestClient(app)
        
        # Create investment and plan dependencies
        inv_response = self.client.post('/investments/', json={
            'name': 'Stock Portfolio',
            'start_date': '2024-01-01',
            'status': 'active'
        })
        investment_uid = inv_response.json()['uid']
        
        plan_response = self.client.post('/investment-plans/', json={
            'investment_id': investment_uid,
            'amount': 500.0,
            'frequency': 'monthly',
            'interval': 1,
            'due_day': 15,
            'due_month': None,
            'status': 'active'
        })
        self.plan_uid = plan_response.json()['uid']
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        response = self.client.post('/investment-plan-instances/', json={
            'investment_plan_id': self.plan_uid,
            'amount': 500.0,
            'due_date': '2024-01-15',
            'transaction_id': None,
            'status': 'planned'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['amount'], 500.0)
        self.assertEqual(data['status'], 'planned')
    
    def test_get_by_id(self) -> None:
        create_response = self.client.post('/investment-plan-instances/', json={
            'investment_plan_id': self.plan_uid,
            'amount': 500.0,
            'due_date': '2024-01-15',
            'transaction_id': None,
            'status': 'planned'
        })
        uid = create_response.json()['uid']
        
        response = self.client.get(f'/investment-plan-instances/{uid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['amount'], 500.0)
    
    def test_get_all(self) -> None:
        self.client.post('/investment-plan-instances/', json={
            'investment_plan_id': self.plan_uid, 'amount': 500.0,
            'due_date': '2024-01-15', 'transaction_id': None, 'status': 'planned'
        })
        self.client.post('/investment-plan-instances/', json={
            'investment_plan_id': self.plan_uid, 'amount': 500.0,
            'due_date': '2024-02-15', 'transaction_id': None, 'status': 'planned'
        })
        
        response = self.client.get('/investment-plan-instances/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
    
    def test_update(self) -> None:
        create_response = self.client.post('/investment-plan-instances/', json={
            'investment_plan_id': self.plan_uid, 'amount': 500.0,
            'due_date': '2024-01-15', 'transaction_id': None, 'status': 'planned'
        })
        uid = create_response.json()['uid']
        
        response = self.client.put(f'/investment-plan-instances/{uid}', json={
            'investment_plan_id': self.plan_uid, 'amount': 500.0,
            'due_date': '2024-01-15', 'transaction_id': None, 'status': 'executed'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'executed')
    
    def test_delete(self) -> None:
        create_response = self.client.post('/investment-plan-instances/', json={
            'investment_plan_id': self.plan_uid, 'amount': 500.0,
            'due_date': '2024-01-15', 'transaction_id': None, 'status': 'planned'
        })
        uid = create_response.json()['uid']
        
        response = self.client.delete(f'/investment-plan-instances/{uid}')
        self.assertEqual(response.status_code, 204)


if __name__ == '__main__':
    unittest.main()

# Made with Bob