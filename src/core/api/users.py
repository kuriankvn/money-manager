from fastapi import APIRouter, HTTPException, status
from core.repositories.user import UserRepository
from core.models.user import User
from core.schemas.user import UserCreate, UserUpdate, UserResponse
from core.utils import generate_uid
from core.exceptions import DuplicateEntityError

router: APIRouter = APIRouter(prefix="/users", tags=["users"])
user_repo: UserRepository = UserRepository()


@router.post(path="/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate) -> UserResponse:
    """Create a new user"""
    uid: str = generate_uid()
    user: User = User(uid=uid, name=user_data.name)
    try:
        user_repo.create(entity=user)
    except DuplicateEntityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
    return UserResponse(uid=user.uid, name=user.name)


@router.get(path="/{uid}", response_model=UserResponse)
def get_user(uid: str) -> UserResponse:
    """Get user by ID"""
    user: User | None = user_repo.get_by_id(uid=uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(uid=user.uid, name=user.name)


@router.get(path="/", response_model=list[UserResponse])
def get_all_users() -> list[UserResponse]:
    """Get all users"""
    users: list[User] = user_repo.get_all()
    return [UserResponse(uid=user.uid, name=user.name) for user in users]


@router.put(path="/{uid}", response_model=UserResponse)
def update_user(uid: str, user_data: UserUpdate) -> UserResponse:
    """Update user"""
    existing_user: User | None = user_repo.get_by_id(uid=uid)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user: User = User(uid=uid, name=user_data.name)
    try:
        success: bool = user_repo.update(entity=user)
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Update failed")
    except DuplicateEntityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
    return UserResponse(uid=user.uid, name=user.name)


@router.delete(path="/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(uid: str) -> None:
    """Delete user"""
    success: bool = user_repo.delete(uid=uid)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
