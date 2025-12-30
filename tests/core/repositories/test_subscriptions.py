import unittest
import os
import tempfile
from datetime import date
from core.storage.init_db import init_database
from core.domain import Subscription, SubscriptionInstance
from core.domain.base import Frequency, SubscriptionStatus, SubscriptionInstanceStatus
from core.repositories import SubscriptionRepository, SubscriptionInstanceRepository


class TestSubscriptionRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.repo = SubscriptionRepository()
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        subscription = Subscription(
            uid='sub-1',
            name='Netflix',
            amount=15.99,
            frequency=Frequency.MONTHLY,
            interval=1,
            due_day=15,
            due_month=None,
            status=SubscriptionStatus.ACTIVE
        )
        uid = self.repo.create(subscription)
        self.assertEqual(uid, 'sub-1')
    
    def test_get_by_id(self) -> None:
        subscription = Subscription(
            uid='sub-2',
            name='Spotify',
            amount=9.99,
            frequency=Frequency.MONTHLY,
            interval=1,
            due_day=1,
            due_month=None,
            status=SubscriptionStatus.ACTIVE
        )
        self.repo.create(subscription)
        retrieved = self.repo.get_by_id('sub-2')
        self.assertIsNotNone(retrieved)
    
    def test_get_all(self) -> None:
        sub1 = Subscription(uid='sub-3', name='Service 1', amount=10.0,
                           frequency=Frequency.MONTHLY, interval=1,
                           due_day=1, due_month=None,
                           status=SubscriptionStatus.ACTIVE)
        sub2 = Subscription(uid='sub-4', name='Service 2', amount=20.0,
                           frequency=Frequency.YEARLY, interval=1,
                           due_day=15, due_month=6,
                           status=SubscriptionStatus.ACTIVE)
        self.repo.create(sub1)
        self.repo.create(sub2)
        subscriptions = self.repo.get_all()
        self.assertEqual(len(subscriptions), 2)
    
    def test_update(self) -> None:
        subscription = Subscription(
            uid='sub-5',
            name='Original',
            amount=100.0,
            frequency=Frequency.MONTHLY,
            interval=1,
            due_day=1,
            due_month=None,
            status=SubscriptionStatus.ACTIVE
        )
        self.repo.create(subscription)
        subscription.name = 'Updated'
        result = self.repo.update(subscription)
        self.assertTrue(result)
    
    def test_delete(self) -> None:
        subscription = Subscription(
            uid='sub-6',
            name='Delete Me',
            amount=99.99,
            frequency=Frequency.MONTHLY,
            interval=1,
            due_day=1,
            due_month=None,
            status=SubscriptionStatus.ACTIVE
        )
        self.repo.create(subscription)
        result = self.repo.delete('sub-6')
        self.assertTrue(result)


class TestSubscriptionInstanceRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        
        self.sub_repo = SubscriptionRepository()
        self.repo = SubscriptionInstanceRepository()
        
        self.subscription = Subscription(
            uid='sub-1',
            name='Netflix',
            amount=15.99,
            frequency=Frequency.MONTHLY,
            interval=1,
            due_day=15,
            due_month=None,
            status=SubscriptionStatus.ACTIVE
        )
        self.sub_repo.create(self.subscription)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        instance = SubscriptionInstance(
            uid='inst-1',
            subscription_id=self.subscription.uid,
            amount=15.99,
            due_date=date(2024, 1, 15),
            transaction_id=None,
            status=SubscriptionInstanceStatus.DUE
        )
        uid = self.repo.create(instance)
        self.assertEqual(uid, 'inst-1')
    
    def test_get_by_id(self) -> None:
        instance = SubscriptionInstance(
            uid='inst-2',
            subscription_id=self.subscription.uid,
            amount=15.99,
            due_date=date(2024, 1, 15),
            transaction_id=None,
            status=SubscriptionInstanceStatus.DUE
        )
        self.repo.create(instance)
        retrieved = self.repo.get_by_id('inst-2')
        self.assertIsNotNone(retrieved)
    
    def test_get_all(self) -> None:
        inst1 = SubscriptionInstance(uid='inst-3', subscription_id=self.subscription.uid,
                                     amount=15.99, due_date=date(2024, 1, 15),
                                     transaction_id=None, status=SubscriptionInstanceStatus.DUE)
        inst2 = SubscriptionInstance(uid='inst-4', subscription_id=self.subscription.uid,
                                     amount=15.99, due_date=date(2024, 2, 15),
                                     transaction_id=None, status=SubscriptionInstanceStatus.DUE)
        self.repo.create(inst1)
        self.repo.create(inst2)
        instances = self.repo.get_all()
        self.assertEqual(len(instances), 2)
    
    def test_update(self) -> None:
        instance = SubscriptionInstance(
            uid='inst-5',
            subscription_id=self.subscription.uid,
            amount=15.99,
            due_date=date(2024, 1, 15),
            transaction_id=None,
            status=SubscriptionInstanceStatus.DUE
        )
        self.repo.create(instance)
        instance.status = SubscriptionInstanceStatus.PAID
        result = self.repo.update(instance)
        self.assertTrue(result)
    
    def test_delete(self) -> None:
        instance = SubscriptionInstance(
            uid='inst-6',
            subscription_id=self.subscription.uid,
            amount=15.99,
            due_date=date(2024, 1, 15),
            transaction_id=None,
            status=SubscriptionInstanceStatus.DUE
        )
        self.repo.create(instance)
        result = self.repo.delete('inst-6')
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()

# Made with Bob
