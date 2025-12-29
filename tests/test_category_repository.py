import unittest
import os
import tempfile
from money_manager.database import init_user_tables, init_category_tables
from money_manager.models import User, Category
from money_manager.repositories import UserRepository, CategoryRepository


class TestCategoryRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_user_tables()
        init_category_tables()
        
        self.user_repo = UserRepository()
        self.repo = CategoryRepository()
        
        # Create test user
        self.user = User(uid='user-1', name='Test User')
        self.user_repo.create(self.user)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create_category(self) -> None:
        category = Category(uid='cat-1', name='Salary', user=self.user)
        uid = self.repo.create(category)
        self.assertEqual(uid, 'cat-1')
    
    def test_get_category_by_id(self) -> None:
        category = Category(uid='cat-2', name='Food', user=self.user)
        self.repo.create(category)
        retrieved = self.repo.get_by_id('cat-2')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, 'Food')
    
    def test_get_all_categories(self) -> None:
        cat1 = Category(uid='cat-3', name='Salary', user=self.user)
        cat2 = Category(uid='cat-4', name='Groceries', user=self.user)
        self.repo.create(cat1)
        self.repo.create(cat2)
        categories = self.repo.get_all()
        self.assertEqual(len(categories), 2)
    
    def test_update_category(self) -> None:
        category = Category(uid='cat-5', name='Original', user=self.user)
        self.repo.create(category)
        category.name = 'Updated'
        result = self.repo.update(category)
        self.assertTrue(result)
        updated = self.repo.get_by_id('cat-5')
        self.assertEqual(updated.name, 'Updated')
    
    def test_delete_category(self) -> None:
        category = Category(uid='cat-6', name='Delete Me', user=self.user)
        self.repo.create(category)
        result = self.repo.delete('cat-6')
        self.assertTrue(result)
        deleted = self.repo.get_by_id('cat-6')
        self.assertIsNone(deleted)


if __name__ == '__main__':
    unittest.main()

# Made with Bob
