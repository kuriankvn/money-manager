import unittest
import os
import tempfile
from money_manager.database import init_user_tables, init_category_tables, init_subscription_tables
from money_manager.models import User, Category, Subscription, Interval
from money_manager.repositories import UserRepository, CategoryRepository, SubscriptionRepository


class TestSubscriptionRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_user_tables()
        init_category_tables()
        init_subscription_tables()
        
        self.user_repo = UserRepository()
        self.category_repo = CategoryRepository()
        self.repo = SubscriptionRepository()
        
        # Create test user and category
        self.user = User(uid='user-1', name='Test User')
        self.category = Category(uid='cat-1', name='Entertainment', user=self.user)
        self.user_repo.create(self.user)
        self.category_repo.create(self.category)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create_subscription(self) -> None:
        subscription = Subscription(
            uid='sub-1',
            name='Netflix',
            amount=15.99,
            interval=Interval.MONTHLY,
            multiplier=1,
            user=self.user,
            category=self.category,
            active=True
        )
        uid = self.repo.create(subscription)
        self.assertEqual(uid, 'sub-1')
    
    def test_get_subscription_by_id(self) -> None:
        subscription = Subscription(
            uid='sub-2',
            name='Spotify',
            amount=9.99,
            interval=Interval.MONTHLY,
            multiplier=1,
            user=self.user,
            category=self.category
        )
        self.repo.create(subscription)
        retrieved = self.repo.get_by_id('sub-2')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, 'Spotify')
        self.assertEqual(retrieved.amount, 9.99)
    
    def test_get_all_subscriptions(self) -> None:
        sub1 = Subscription(uid='sub-3', name='Service 1', amount=10.0, interval=Interval.MONTHLY,
                           multiplier=1, user=self.user, category=self.category)
        sub2 = Subscription(uid='sub-4', name='Service 2', amount=20.0, interval=Interval.YEARLY,
                           multiplier=1, user=self.user, category=self.category)
        self.repo.create(sub1)
        self.repo.create(sub2)
        subscriptions = self.repo.get_all()
        self.assertEqual(len(subscriptions), 2)
    
    def test_update_subscription(self) -> None:
        subscription = Subscription(
            uid='sub-5',
            name='Original',
            amount=100.0,
            interval=Interval.MONTHLY,
            multiplier=1,
            user=self.user,
            category=self.category
        )
        self.repo.create(subscription)
        subscription.name = 'Updated'
        subscription.amount = 150.0
        result = self.repo.update(subscription)
        self.assertTrue(result)
        updated = self.repo.get_by_id('sub-5')
        self.assertEqual(updated.name, 'Updated')
        self.assertEqual(updated.amount, 150.0)
    
    def test_delete_subscription(self) -> None:
        subscription = Subscription(
            uid='sub-6',
            name='Delete Me',
            amount=99.99,
            interval=Interval.MONTHLY,
            multiplier=1,
            user=self.user,
            category=self.category
        )
        self.repo.create(subscription)
        result = self.repo.delete('sub-6')
        self.assertTrue(result)
        deleted = self.repo.get_by_id('sub-6')
        self.assertIsNone(deleted)


if __name__ == '__main__':
    unittest.main()

# Made with Bob
