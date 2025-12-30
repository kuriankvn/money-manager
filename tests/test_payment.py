import unittest
import os
import tempfile
from datetime import datetime
from core.database import init_user_tables, init_category_tables, init_subscription_tables, init_subscription_payment_tables
from core.models import User, Category, Subscription, Interval, Payment
from core.repositories import UserRepository, CategoryRepository, SubscriptionRepository, PaymentRepository
from core.services import PaymentService
from fastapi.testclient import TestClient
from core.main import app


class TestPayment(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_user_tables()
        init_category_tables()
        init_subscription_tables()
        init_subscription_payment_tables()
        
        self.user_repo = UserRepository()
        self.category_repo = CategoryRepository()
        self.subscription_repo = SubscriptionRepository()
        self.repo = PaymentRepository()
        self.service = PaymentService()
        self.client = TestClient(app)
        
        self.user = User(uid='user-1', name='Test User')
        self.category = Category(uid='cat-1', name='Entertainment', user=self.user)
        self.subscription = Subscription(
            uid='sub-1',
            name='Netflix',
            amount=999.0,
            interval=Interval.MONTHLY,
            multiplier=1,
            user=self.user,
            category=self.category,
            active=True
        )
        self.user_repo.create(self.user)
        self.category_repo.create(self.category)
        self.subscription_repo.create(self.subscription)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create_payment_repository(self) -> None:
        payment = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        uid = self.repo.create(payment)
        self.assertEqual(uid, 'pay-1')
    
    def test_get_payment_by_id(self) -> None:
        payment = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment)
        
        retrieved = self.repo.get_by_id('pay-1')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.uid, 'pay-1')
        self.assertEqual(retrieved.amount, 999.0)
        self.assertFalse(retrieved.paid)
    
    def test_get_all_payments(self) -> None:
        payment1 = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        payment2 = Payment(
            uid='pay-2',
            amount=999.0,
            due_date=datetime(2025, 2, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment1)
        self.repo.create(payment2)
        
        payments = self.repo.get_all()
        self.assertEqual(len(payments), 2)
    
    def test_update_payment(self) -> None:
        payment = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment)
        
        payment.paid = True
        payment.paid_date = datetime(2025, 1, 5)
        success = self.repo.update(payment)
        self.assertTrue(success)
        
        updated = self.repo.get_by_id('pay-1')
        self.assertTrue(updated.paid)
        self.assertIsNotNone(updated.paid_date)
    
    def test_delete_payment(self) -> None:
        payment = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment)
        
        success = self.repo.delete('pay-1')
        self.assertTrue(success)
        
        retrieved = self.repo.get_by_id('pay-1')
        self.assertIsNone(retrieved)
    
    def test_get_payments_by_month_year(self) -> None:
        payment1 = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        payment2 = Payment(
            uid='pay-2',
            amount=999.0,
            due_date=datetime(2025, 2, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment1)
        self.repo.create(payment2)
        
        january_payments = self.repo.get_by_month_year(1, 2025)
        self.assertEqual(len(january_payments), 1)
        self.assertEqual(january_payments[0].uid, 'pay-1')
    
    def test_generate_payments_for_month(self) -> None:
        result = self.service.generate_payments_for_month(1, 2025)
        self.assertEqual(result['created'], 1)
        self.assertEqual(result['skipped'], 0)
        
        payments = self.repo.get_by_month_year(1, 2025)
        self.assertEqual(len(payments), 1)
    
    def test_generate_payments_skips_existing(self) -> None:
        # Generate once
        self.service.generate_payments_for_month(1, 2025)
        
        # Try to generate again
        result = self.service.generate_payments_for_month(1, 2025)
        self.assertEqual(result['created'], 0)
        self.assertEqual(result['skipped'], 1)
    
    def test_generate_payments_yearly_subscription(self) -> None:
        yearly_sub = Subscription(
            uid='sub-2',
            name='Amazon Prime',
            amount=1499.0,
            interval=Interval.YEARLY,
            multiplier=1,
            user=self.user,
            category=self.category,
            active=True
        )
        self.subscription_repo.create(yearly_sub)
        
        # Generate for January - should include yearly
        result_jan = self.service.generate_payments_for_month(1, 2025)
        self.assertEqual(result_jan['created'], 2)  # Monthly + Yearly
        
        # Generate for February - should skip yearly
        result_feb = self.service.generate_payments_for_month(2, 2025)
        self.assertEqual(result_feb['created'], 1)  # Only monthly
        self.assertEqual(result_feb['skipped_interval'], 1)  # Yearly skipped
    
    def test_mark_payment_as_paid(self) -> None:
        payment = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment)
        
        success = self.service.mark_as_paid('pay-1')
        self.assertTrue(success)
        
        updated = self.repo.get_by_id('pay-1')
        self.assertTrue(updated.paid)
        self.assertIsNotNone(updated.paid_date)
    
    def test_get_payment_statistics(self) -> None:
        payment1 = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=datetime(2025, 1, 5),
            paid=True
        )
        payment2 = Payment(
            uid='pay-2',
            amount=500.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment1)
        self.repo.create(payment2)
        
        stats = self.service.get_payment_statistics(1, 2025)
        self.assertEqual(stats['total_due'], 1499.0)
        self.assertEqual(stats['total_paid'], 999.0)
        self.assertEqual(stats['total_pending'], 500.0)
        self.assertEqual(stats['paid_count'], 1)
        self.assertEqual(stats['pending_count'], 1)
        self.assertEqual(stats['total_count'], 2)
    
    def test_create_payment_api(self) -> None:
        response = self.client.post(
            "/payments/generate",
            json={"month": 1, "year": 2025}
        )
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertEqual(result['created'], 1)
    
    def test_get_payment_api(self) -> None:
        payment = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment)
        
        response = self.client.get("/payments/pay-1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['uid'], 'pay-1')
        self.assertEqual(data['amount'], 999.0)
    
    def test_get_all_payments_api(self) -> None:
        payment = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment)
        
        response = self.client.get("/payments")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
    
    def test_mark_payment_as_paid_api(self) -> None:
        payment = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment)
        
        response = self.client.put(
            "/payments/pay-1/mark-paid",
            json={}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['paid'])
    
    def test_get_payment_statistics_api(self) -> None:
        payment = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment)
        
        response = self.client.get("/payments/statistics/1/2025")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_count'], 1)
    
    def test_delete_payment_api(self) -> None:
        payment = Payment(
            uid='pay-1',
            amount=999.0,
            due_date=datetime(2025, 1, 1),
            user=self.user,
            subscription=self.subscription,
            paid_date=None,
            paid=False
        )
        self.repo.create(payment)
        
        response = self.client.delete("/payments/pay-1")
        self.assertEqual(response.status_code, 204)
        
        retrieved = self.repo.get_by_id('pay-1')
        self.assertIsNone(retrieved)


if __name__ == '__main__':
    unittest.main()

# Made with Bob
