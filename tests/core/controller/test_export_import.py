import unittest
import os
import tempfile
from fastapi.testclient import TestClient
from core.main import app
from core.storage.init_db import init_database


class TestTransactionExportImport(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.client = TestClient(app)
        
        # Create test data
        self.category = self.client.post('/categories/', json={'name': 'Food'}).json()
        self.account = self.client.post('/accounts/', json={'name': 'Checking'}).json()
        
        # Create test transactions
        self.client.post('/transactions/', json={
            'name': 'Grocery',
            'amount': 50.0,
            'date': '2024-01-15',
            'account_id': self.account['uid'],
            'category_id': self.category['uid']
        })
        self.client.post('/transactions/', json={
            'name': 'Restaurant',
            'amount': 30.0,
            'date': '2024-01-16',
            'account_id': self.account['uid'],
            'category_id': self.category['uid']
        })
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_export_transactions_csv(self) -> None:
        """Test exporting transactions to CSV"""
        response = self.client.get('/transactions/export/csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'text/csv; charset=utf-8')
        
        # Check CSV content
        csv_content = response.text
        self.assertIn('name,amount,date,account,category', csv_content)
        self.assertIn('Grocery', csv_content)
        self.assertIn('Restaurant', csv_content)
        self.assertIn('50.0', csv_content)
        self.assertIn('30.0', csv_content)
    
    def test_import_transactions_csv(self) -> None:
        """Test importing transactions from CSV"""
        csv_content = f"""name,amount,date,account,category
Coffee,5.50,2024-01-17,{self.account['name']},{self.category['name']}
Lunch,12.00,2024-01-18,{self.account['name']},{self.category['name']}"""
        
        response = self.client.post('/transactions/export/csv', json={'file_content': csv_content})
        self.assertEqual(response.status_code, 201)
        
        result = response.json()
        self.assertEqual(result['created'], 2)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(len(result['errors']), 0)
        
        # Verify transactions were created
        all_txns = self.client.get('/transactions/').json()
        self.assertEqual(len(all_txns), 4)  # 2 original + 2 imported
    
    def test_import_transactions_csv_with_errors(self) -> None:
        """Test importing transactions with validation errors"""
        csv_content = """name,amount,date,account,category
Valid,10.0,2024-01-17,Checking,Food
Invalid Amount,-5.0,2024-01-18,Checking,Food
Missing Account,10.0,2024-01-19,NonExistent,Food"""
        
        response = self.client.post('/transactions/export/csv', json={'file_content': csv_content})
        self.assertEqual(response.status_code, 201)
        
        result = response.json()
        self.assertGreater(result['failed'], 0)
        self.assertGreater(len(result['errors']), 0)


class TestSubscriptionExportImport(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.client = TestClient(app)
        
        # Create test subscriptions
        self.client.post('/subscriptions/', json={
            'name': 'Netflix',
            'amount': 15.99,
            'frequency': 'monthly',
            'interval': 1,
            'due_day': 15,
            'due_month': None,
            'status': 'active'
        })
        self.client.post('/subscriptions/', json={
            'name': 'Amazon Prime',
            'amount': 139.0,
            'frequency': 'yearly',
            'interval': 1,
            'due_day': 1,
            'due_month': 6,
            'status': 'active'
        })
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_export_subscriptions_csv(self) -> None:
        """Test exporting subscriptions to CSV"""
        response = self.client.get('/subscriptions/export/csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'text/csv; charset=utf-8')
        
        # Check CSV content
        csv_content = response.text
        self.assertIn('name,amount,frequency,interval,due_day,due_month,status', csv_content)
        self.assertIn('Netflix', csv_content)
        self.assertIn('Amazon Prime', csv_content)
        self.assertIn('15.99', csv_content)
        self.assertIn('139.0', csv_content)
    
    def test_import_subscriptions_csv(self) -> None:
        """Test importing subscriptions from CSV"""
        csv_content = """name,amount,frequency,interval,due_day,due_month,status
Spotify,9.99,monthly,1,1,,active
Disney+,79.99,yearly,1,15,3,active"""
        
        response = self.client.post('/subscriptions/export/csv', json={'file_content': csv_content})
        self.assertEqual(response.status_code, 201)
        
        result = response.json()
        self.assertEqual(result['created'], 2)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(len(result['errors']), 0)
        
        # Verify subscriptions were created
        all_subs = self.client.get('/subscriptions/').json()
        self.assertEqual(len(all_subs), 4)  # 2 original + 2 imported
    
    def test_import_subscriptions_csv_with_errors(self) -> None:
        """Test importing subscriptions with validation errors"""
        csv_content = """name,amount,frequency,interval,due_day,due_month,status
Valid,10.0,monthly,1,15,,active
Invalid Amount,-5.0,monthly,1,15,,active
Invalid Frequency,10.0,weekly,1,15,,active
Monthly With Month,10.0,monthly,1,15,6,active
Yearly Without Month,10.0,yearly,1,15,,active"""
        
        response = self.client.post('/subscriptions/export/csv', json={'file_content': csv_content})
        self.assertEqual(response.status_code, 201)
        
        result = response.json()
        self.assertGreater(result['failed'], 0)
        self.assertGreater(len(result['errors']), 0)


if __name__ == '__main__':
    unittest.main()

# Made with Bob