import uuid
from collections.abc import Callable
from typing import Any, Optional, List

from money_manager.database import init_database
from money_manager.models import Category, Transaction, TransactionType, User
from money_manager.repositories import (
    CategoryRepository,
    TransactionRepository,
    UserRepository,)
from money_manager.utils import (
    pause,
    print_header,
    validate_non_empty,
    validate_positive_float,
    datetime_to_epoch,
    epoch_to_datetime,)


class MoneyManagerCLI:
    def __init__(self) -> None:
        self.user_repo: UserRepository = UserRepository()
        self.category_repo: CategoryRepository = CategoryRepository()
        self.transaction_repo: TransactionRepository = TransactionRepository()
    
    def _display_menu(self, title: str, options: List[str]) -> str:
        print_header(title=title)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        return input("\nEnter your choice: ").strip()
    
    def _select_item_from_list(self, items: List[Any], prompt: str) -> Optional[Any]:
        print("\nAvailable items:")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item.__str__()}")
        
        choice: str = input(f"\n{prompt}: ").strip()
        if not choice.isdigit():
            print("\n✗ Invalid input. Please enter a number.")
            pause()
            return None
        
        index: int = int(choice) - 1
        if 0 <= index < len(items):
            return items[index]
        else:
            print("\n✗ Invalid selection.")
            pause()
            return None
    
    def _get_transaction_type(self) -> Optional[TransactionType]:
        print("\nTransaction type:")
        print("1. Income")
        print("2. Expense")
        type_choice: str = input("Select type: ").strip()
        
        if type_choice == "1":
            return TransactionType.INCOME
        elif type_choice == "2":
            return TransactionType.EXPENSE
        else:
            print("\n✗ Invalid type selection.")
            pause()
            return None
    
    def _get_validated_name(self, prompt: str) -> Optional[str]:
        name: str = input(prompt).strip()
        if not validate_non_empty(value=name):
            print("\n✗ Name cannot be empty.")
            pause()
            return None
        return name
    
    def _get_validated_amount(self, prompt: str) -> Optional[float]:
        amount_str: str = input(prompt).strip()
        amount: Optional[float] = validate_positive_float(value=amount_str)
        if amount is None:
            print("\n✗ Invalid amount. Must be a positive number.")
            pause()
            return None
        return amount
    
    def run(self) -> None:
        init_database()
        self.main_menu()

    def main_menu(self) -> None:
        menu_actions: dict[str, Callable[[], None]] = {
            "1": self.user_management_menu,
            "2": self.category_management_menu,
            "3": self.transaction_management_menu,}
        
        while True:
            choice: str = self._display_menu(
                title="Money Manager - Main Menu",
                options=["User Management", "Category Management", "Transaction Management", "Exit"])
            
            if choice in menu_actions:
                menu_actions[choice]()
            elif choice == "4":
                print("\nGoodbye!")
                break
            else:
                print("\n✗ Invalid choice. Please try again.")
                pause()
    
    def user_management_menu(self) -> None:
        menu_actions: dict[str, Callable[[], None]] = {
            "1": self.create_user,
            "2": self.list_users,
            "3": self.update_user,
            "4": self.delete_user,}
        
        while True:
            choice: str = self._display_menu(
                title="User Management",
                options=["Create User", "List Users", "Update User", "Delete User", "Back to Main Menu"])
            
            if choice in menu_actions:
                menu_actions[choice]()
            elif choice == "5":
                break
            else:
                print("\n✗ Invalid choice. Please try again.")
                pause()
    
    def create_user(self) -> None:
        print_header(title="Create User")
        name: Optional[str] = self._get_validated_name(prompt="Enter user name: ")
        if not name:
            return
        user: User = User(uid=str(uuid.uuid4()), name=name)

        try:
            self.user_repo.create(user=user)
            print(f"\n✓ User created successfully with ID: {user.uid}")
        except Exception as e:
            print(f"\n✗ Error creating user: {e}")
        pause()
    
    def _get_users(self) -> list[User]:
        users: List[User] = self.user_repo.get_all()
        if not users:
            print("\n✗ No users found.")
            pause()
        return users
    
    def list_users(self) -> None:
        print_header(title="List Users")
        users: List[User] = self._get_users()
        if not users:
            return
        
        for i, user in enumerate(users, 1):
            print(f"{i}. {user.__str__()}")
        pause()
    
    def update_user(self) -> None:
        print_header(title="Update User")
        users: List[User] = self._get_users()
        if not users:
            return
        item: Optional[Any] = self._select_item_from_list(items=users, prompt="Select user number")
        if item is None:
            return
        selected_user: User = item

        updated_name: Optional[str] = self._get_validated_name(prompt=f"Enter updated user name (current: {selected_user.name}): ")
        if not updated_name:
            return
        updated_user: User = User(uid=selected_user.uid, name=updated_name)
        
        try:
            if self.user_repo.update(user=updated_user):
                print("\n✓ User updated successfully.")
            else:
                print("\n✗ Failed to update user.")
        except Exception as e:
            print(f"\n✗ Error updating user: {e}")
        pause()
    
    def delete_user(self) -> None:
        print_header(title="Delete User")
        users: List[User] = self._get_users()
        if not users:
            return
        item: Optional[Any] = self._select_item_from_list(items=users, prompt="Select user number")
        if item is None:
            return
        selected_user: User = item

        confirm: str = input(f"Delete user '{selected_user.name}'? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("\n✗ Deletion cancelled.")
            pause()
            return
        
        try:
            if self.user_repo.delete(uid=selected_user.uid):
                print("\n✓ User deleted successfully.")
            else:
                print("\n✗ Failed to delete user.")
        except Exception as e:
            print(f"\n✗ Error deleting user: {e}")
        pause()
    
    def category_management_menu(self) -> None:
        menu_actions: dict[str, Callable[[], None]] = {
            "1": self.create_category,
            "2": self.list_categories,
            "3": self.update_category,
            "4": self.delete_category,}
        
        while True:
            choice: str = self._display_menu(
                title="Category Management",
                options=["Create Category", "List Categories", "Update Category", "Delete Category", "Back to Main Menu"])
            
            if choice in menu_actions:
                menu_actions[choice]()
            elif choice == "5":
                break
            else:
                print("\n✗ Invalid choice. Please try again.")
                pause()
    
    def create_category(self) -> None:
        print_header(title="Create Category")
        name: Optional[str] = self._get_validated_name(prompt="Enter category name: ")
        if not name:
            return
        category_type: Optional[TransactionType] = self._get_transaction_type()
        if not category_type:
            return
        category: Category = Category(uid=str(uuid.uuid4()), name=name, type=category_type)
        
        try:
            self.category_repo.create(category=category)
            print(f"\n✓ Category created successfully with ID: {category.uid}")
        except Exception as e:
            print(f"\n✗ Error creating category: {e}")
        pause()
    
    def _get_categories(self) -> list[Category]:
        categories: List[Category] = self.category_repo.get_all()
        if not categories:
            print("\n✗ No categories found.")
            pause()
        return categories
    
    def list_categories(self) -> None:
        print_header(title="List Categories")
        categories: List[Category] = self._get_categories()
        if not categories:
            return
        
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category.__str__()}")
        pause()
    
    def update_category(self) -> None:
        print_header(title="Update Category")
        categories: List[Category] = self._get_categories()
        if not categories:
            return
        item: Optional[Any] = self._select_item_from_list(items=categories, prompt="Select category number")
        if item is None:
            return
        selected_category: Category = item
        
        updated_name: Optional[str] = self._get_validated_name(prompt=f"Enter updated category name (current: {selected_category.name}): ")
        if not updated_name:
            return
        updated_category_type: Optional[TransactionType] = self._get_transaction_type()
        if not updated_category_type:
            return
        updated_category: Category = Category(uid=selected_category.uid, name=updated_name, type=updated_category_type)
        
        try:
            if self.category_repo.update(category=updated_category):
                print("\n✓ Category updated successfully.")
            else:
                print("\n✗ Failed to update category.")
        except Exception as e:
            print(f"\n✗ Error updating category: {e}")
        pause()
    
    def delete_category(self) -> None:
        print_header(title="Delete Category")
        categories: List[Category] = self._get_categories()
        if not categories:
            return
        item: Optional[Any] = self._select_item_from_list(items=categories, prompt="Select category number")
        if item is None:
            return
        selected_category: Category = item

        confirm: str = input(f"Delete category '{selected_category.name}'? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("\n✗ Deletion cancelled.")
            pause()
            return
        
        try:
            if self.category_repo.delete(uid=selected_category.uid):
                print("\n✓ Category deleted successfully.")
            else:
                print("\n✗ Failed to delete category.")
        except Exception as e:
            print(f"\n✗ Error deleting category: {e}")
        pause()
    
    def transaction_management_menu(self) -> None:
        menu_actions: dict[str, Callable[[], None]] = {
            "1": self.create_transaction,
            "2": self.list_transactions,
            "3": self.update_transaction,
            "4": self.delete_transaction,}
        
        while True:
            choice: str = self._display_menu(
                title="Transaction Management",
                options=["Create Transaction", "List Transactions", "Update Transaction", "Delete Transaction", "Back to Main Menu"])
            
            if choice in menu_actions:
                menu_actions[choice]()
            elif choice == "5":
                break
            else:
                print("\n✗ Invalid choice. Please try again.")
                pause()
    
    def create_transaction(self) -> None:
        print_header(title="Create Transaction")
        
        users: List[User] = self._get_users()
        if not users:
            return
        user: Optional[Any] = self._select_item_from_list(items=users, prompt="Select user number")
        if user is None:
            return
        selected_user: User = user
        
        categories: List[Category] = self._get_categories()
        if not categories:
            return
        category: Optional[Any] = self._select_item_from_list(items=categories, prompt="Select category number")
        if category is None:
            return
        selected_category: Category = category
        
        name: Optional[str] = self._get_validated_name(prompt="Enter transaction name: ")
        if not name:
            return
        
        amount: Optional[float] = self._get_validated_amount(prompt="Enter transaction amount: ")
        if amount is None:
            return
        
        datetime_str: str = input("\nEnter date and time (YYYY-MM-DD HH:MM): ").strip()
        transaction_datetime: Optional[float] = datetime_to_epoch(datetime_str=datetime_str)
        if transaction_datetime is None:
            pause()
            return
        
        transaction: Transaction = Transaction(
            uid=str(uuid.uuid4()), name=name, amount=amount, datetime=transaction_datetime, user=selected_user, category=selected_category)
        
        try:
            self.transaction_repo.create(transaction=transaction)
            print(f"\n✓ Transaction added successfully with ID: {transaction.uid}")
        except Exception as e:
            print(f"\n✗ Error adding transaction: {e}")
        pause()
    
    def _get_transactions(self) -> list[Transaction]:
        transactions: List[Transaction] = self.transaction_repo.get_all()
        if not transactions:
            print("\n✗ No transactions found.")
            pause()
        return transactions
    
    def list_transactions(self) -> None:
        print_header(title="List Transactions")
        transactions: List[Transaction] = self._get_transactions()
        if not transactions:
            return
        
        for i, transaction in enumerate(transactions, 1):
            print(f"{i}. {transaction.__str__()}")
        pause()
    
    def update_transaction(self) -> None:
        print_header(title="Update Transaction")

        transactions: List[Transaction] = self._get_transactions()
        if not transactions:
            return
        item: Optional[Any] = self._select_item_from_list(items=transactions, prompt="Select transaction number")
        if item is None:
            return
        selected_transaction: Transaction = item
        
        users: List[User] = self._get_users()
        if not users:
            return
        user: Optional[Any] = self._select_item_from_list(items=users, prompt="Select user number")
        if user is None:
            return
        updated_user: User = user
        
        categories: List[Category] = self._get_categories()
        if not categories:
            return
        category: Optional[Any] = self._select_item_from_list(items=categories, prompt="Select category number")
        if category is None:
            return
        updated_category: Category = category

        updated_name: Optional[str] = self._get_validated_name(prompt=f"Enter updated transaction name (current: {selected_transaction.name}): ")
        if not updated_name:
            return
        
        updated_amount: Optional[float] = self._get_validated_amount(prompt=f"Enter updated transaction amount (current: ${selected_transaction.amount:.2f}): ")
        if updated_amount is None:
            return
        
        updated_datetime_str: str = input(f"\nEnter updated date and time (YYYY-MM-DD HH:MM) (current: {epoch_to_datetime(epoch=selected_transaction.datetime)}): ").strip()
        updated_datetime: Optional[float] = datetime_to_epoch(datetime_str=updated_datetime_str)
        if updated_datetime is None:
            pause()
            return
        
        updated_transaction: Transaction = Transaction(
            uid=selected_transaction.uid, name=updated_name, amount=updated_amount, datetime=updated_datetime, user=updated_user, category=updated_category)
        
        try:
            if self.transaction_repo.update(transaction=updated_transaction):
                print("\n✓ Transaction updated successfully.")
            else:
                print("\n✗ Failed to update transaction.")
        except Exception as e:
            print(f"\n✗ Error updating transaction: {e}")
        pause()
    
    def delete_transaction(self) -> None:
        print_header(title="Delete Transaction")
        transactions: List[Transaction] = self._get_transactions()
        if not transactions:
            return
        item: Optional[Any] = self._select_item_from_list(items=transactions, prompt="Select transaction number")
        if item is None:
            return
        selected_transaction: Transaction = item
        
        confirm: str = input(f"Delete transaction '{selected_transaction.name}'? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("\n✗ Deletion cancelled.")
            pause()
            return
        
        try:
            if self.transaction_repo.delete(uid=selected_transaction.uid):
                print("\n✓ Transaction deleted successfully.")
            else:
                print("\n✗ Failed to delete transaction.")
        except Exception as e:
            print(f"\n✗ Error deleting transaction: {e}")
        pause()


def main() -> int:
    try:
        cli: MoneyManagerCLI = MoneyManagerCLI()
        cli.run()
        return 0
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        return 0
    except Exception as e:
        print(f"\n✗ An error occurred: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

# Made with Bob
