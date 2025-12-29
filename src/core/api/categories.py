from fastapi import APIRouter, HTTPException, status
from core.repositories.category import CategoryRepository
from core.repositories.user import UserRepository
from core.models.category import Category
from core.models.user import User
from core.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from core.utils import generate_uid

router: APIRouter = APIRouter(prefix="/categories", tags=["categories"])
category_repo: CategoryRepository = CategoryRepository()
user_repo: UserRepository = UserRepository()


@router.post(path="/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategoryCreate) -> CategoryResponse:
    """Create a new category"""
    user: User | None = user_repo.get_by_id(uid=category_data.user_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    uid: str = generate_uid()
    category: Category = Category(uid=uid, name=category_data.name, user=user)
    category_repo.create(entity=category)
    return CategoryResponse(
        uid=category.uid,
        name=category.name,
        user_uid=user.uid,
        user_name=user.name
    )


@router.get(path="/{uid}", response_model=CategoryResponse)
def get_category(uid: str) -> CategoryResponse:
    """Get category by ID"""
    category: Category | None = category_repo.get_by_id(uid=uid)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return CategoryResponse(
        uid=category.uid,
        name=category.name,
        user_uid=category.user.uid,
        user_name=category.user.name
    )


@router.get(path="/", response_model=list[CategoryResponse])
def get_all_categories() -> list[CategoryResponse]:
    """Get all categories"""
    categories: list[Category] = category_repo.get_all()
    return [
        CategoryResponse(
            uid=cat.uid,
            name=cat.name,
            user_uid=cat.user.uid,
            user_name=cat.user.name
        )
        for cat in categories
    ]


@router.put(path="/{uid}", response_model=CategoryResponse)
def update_category(uid: str, category_data: CategoryUpdate) -> CategoryResponse:
    """Update category"""
    existing_category: Category | None = category_repo.get_by_id(uid=uid)
    if not existing_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    user: User | None = user_repo.get_by_id(uid=category_data.user_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    category: Category = Category(uid=uid, name=category_data.name, user=user)
    success: bool = category_repo.update(entity=category)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Update failed")
    
    return CategoryResponse(
        uid=category.uid,
        name=category.name,
        user_uid=user.uid,
        user_name=user.name
    )


@router.delete(path="/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(uid: str) -> None:
    """Delete category"""
    success: bool = category_repo.delete(uid=uid)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
