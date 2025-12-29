import unittest
import os
import tempfile
from money_manager.database import init_user_tables, get_connection
from money_manager.models import User
from money_manager.repositories import UserRepository
from fastapi.testclient import TestClient
from money_manager.main import app


class TestUser(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_user_tables()
        self.repo = UserRepository()
        self.client = TestClient(app)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create_user_repository(self) -> None:
        user = User(uid='test-uid-1', name='John Doe')
        uid = self.repo.create(user)
        self.assertEqual(uid, 'test-uid-1')
    
    def test_create_user_api(self) -> None:
        response = self.client.post("/users/", json={"name": "John Doe"})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "John Doe")
        self.assertIn("uid", data)
    
    def test_get_user_by_id_repository(self) -> None:
        user = User(uid='test-uid-2', name='Jane Doe')
        self.repo.create(user)
        retrieved = self.repo.get_by_id('test-uid-2')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, 'Jane Doe')
    
    def test_get_user_by_id_api(self) -> None:
        create_response = self.client.post("/users/", json={"name": "Jane Doe"})
        uid = create_response.json()["uid"]
        response = self.client.get(f"/users/{uid}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Jane Doe")
    
    def test_get_all_users_repository(self) -> None:
        user1 = User(uid='uid-1', name='Alice')
        user2 = User(uid='uid-2', name='Bob')
        self.repo.create(user1)
        self.repo.create(user2)
        users = self.repo.get_all()
        self.assertEqual(len(users), 2)
    
    def test_get_all_users_api(self) -> None:
        self.client.post("/users/", json={"name": "Alice"})
        self.client.post("/users/", json={"name": "Bob"})
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
    
    def test_update_user_repository(self) -> None:
        user = User(uid='uid-3', name='Original')
        self.repo.create(user)
        user.name = 'Updated'
        result = self.repo.update(user)
        self.assertTrue(result)
        updated = self.repo.get_by_id('uid-3')
        self.assertEqual(updated.name, 'Updated')
    
    def test_update_user_api(self) -> None:
        create_response = self.client.post("/users/", json={"name": "Original"})
        uid = create_response.json()["uid"]
        response = self.client.put(f"/users/{uid}", json={"name": "Updated"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated")
    
    def test_delete_user_repository(self) -> None:
        user = User(uid='uid-4', name='Delete Me')
        self.repo.create(user)
        result = self.repo.delete('uid-4')
        self.assertTrue(result)
        deleted = self.repo.get_by_id('uid-4')
        self.assertIsNone(deleted)
    
    def test_delete_user_api(self) -> None:
        create_response = self.client.post("/users/", json={"name": "Delete Me"})
        uid = create_response.json()["uid"]
        response = self.client.delete(f"/users/{uid}")
        self.assertEqual(response.status_code, 204)
        deleted = self.client.get(f"/users/{uid}")
        self.assertEqual(deleted.status_code, 404)


if __name__ == '__main__':
    unittest.main()

# Made with Bob
