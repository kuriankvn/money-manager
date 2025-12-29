import unittest
import os
import tempfile
from money_manager.database import init_user_tables, init_category_tables, init_subscription_tables
from money_manager.models import User, Category, Subscription, Interval
from money_manager.repositories import UserRepository, CategoryRepository, SubscriptionRepository
from fastapi.testclient import TestClient
from money_manager.main import app


class TestSubscription(unittest.TestCase):
    
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
        self.client = TestClient(app)
        
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
    
    def test_create_subscription_repository(self) -> None:
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
    
    def test_create_subscription_api(self) -> None:
        response = self.client.post("/subscriptions/", json={
            "name": "Netflix",
            "amount": 15.99,
            "interval": "monthly",
            "multiplier": 1,
            "user_uid": self.user.uid,
            "category_uid": self.category.uid,
            "active": True
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Netflix")
        self.assertEqual(data["amount"], 15.99)
    
    def test_get_subscription_by_id_repository(self) -> None:
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
    
    def test_get_subscription_by_id_api(self) -> None:
        create_response = self.client.post("/subscriptions/", json={
            "name": "Spotify",
            "amount": 9.99,
            "interval": "monthly",
            "multiplier": 1,
            "user_uid": self.user.uid,
            "category_uid": self.category.uid,
            "active": True
        })
        uid = create_response.json()["uid"]
        response = self.client.get(f"/subscriptions/{uid}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Spotify")
        self.assertEqual(data["amount"], 9.99)
    
    def test_get_all_subscriptions_repository(self) -> None:
        sub1 = Subscription(uid='sub-3', name='Service 1', amount=10.0, interval=Interval.MONTHLY,
                           multiplier=1, user=self.user, category=self.category)
        sub2 = Subscription(uid='sub-4', name='Service 2', amount=20.0, interval=Interval.YEARLY,
                           multiplier=1, user=self.user, category=self.category)
        self.repo.create(sub1)
        self.repo.create(sub2)
        subscriptions = self.repo.get_all()
        self.assertEqual(len(subscriptions), 2)
    
    def test_get_all_subscriptions_api(self) -> None:
        self.client.post("/subscriptions/", json={
            "name": "Service 1", "amount": 10.0, "interval": "monthly",
            "multiplier": 1, "user_uid": self.user.uid, "category_uid": self.category.uid, "active": True
        })
        self.client.post("/subscriptions/", json={
            "name": "Service 2", "amount": 20.0, "interval": "yearly",
            "multiplier": 1, "user_uid": self.user.uid, "category_uid": self.category.uid, "active": True
        })
        response = self.client.get("/subscriptions/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
    
    def test_update_subscription_repository(self) -> None:
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
    
    def test_update_subscription_api(self) -> None:
        create_response = self.client.post("/subscriptions/", json={
            "name": "Original", "amount": 100.0, "interval": "monthly",
            "multiplier": 1, "user_uid": self.user.uid, "category_uid": self.category.uid, "active": True
        })
        uid = create_response.json()["uid"]
        response = self.client.put(f"/subscriptions/{uid}", json={
            "name": "Updated", "amount": 150.0, "interval": "monthly",
            "multiplier": 1, "user_uid": self.user.uid, "category_uid": self.category.uid, "active": True
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated")
        self.assertEqual(data["amount"], 150.0)
    
    def test_delete_subscription_repository(self) -> None:
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
    
    def test_delete_subscription_api(self) -> None:
        create_response = self.client.post("/subscriptions/", json={
            "name": "Delete Me", "amount": 99.99, "interval": "monthly",
            "multiplier": 1, "user_uid": self.user.uid, "category_uid": self.category.uid, "active": True
        })
        uid = create_response.json()["uid"]
        response = self.client.delete(f"/subscriptions/{uid}")
        self.assertEqual(response.status_code, 204)
        deleted = self.client.get(f"/subscriptions/{uid}")
        self.assertEqual(deleted.status_code, 404)


if __name__ == '__main__':
    unittest.main()

# Made with Bob
