from fastapi import APIRouter, HTTPException, status
from core.repositories.subscription import SubscriptionRepository
from core.repositories.user import UserRepository
from core.repositories.category import CategoryRepository
from core.models.subscription import Subscription, Interval
from core.models.user import User
from core.models.category import Category
from core.schemas.subscription import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
from core.utils import generate_uid

router: APIRouter = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
subscription_repo: SubscriptionRepository = SubscriptionRepository()
user_repo: UserRepository = UserRepository()
category_repo: CategoryRepository = CategoryRepository()


@router.post(path="/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(subscription_data: SubscriptionCreate) -> SubscriptionResponse:
    """Create a new subscription"""
    user: User | None = user_repo.get_by_id(uid=subscription_data.user_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    category: Category | None = category_repo.get_by_id(uid=subscription_data.category_uid)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    uid: str = generate_uid()
    subscription: Subscription = Subscription(
        uid=uid,
        name=subscription_data.name,
        amount=subscription_data.amount,
        interval=Interval(value=subscription_data.interval),
        multiplier=subscription_data.multiplier,
        user=user,
        category=category,
        active=subscription_data.active
    )
    subscription_repo.create(entity=subscription)
    return SubscriptionResponse(
        uid=subscription.uid,
        name=subscription.name,
        amount=subscription.amount,
        interval=subscription.interval.value,
        multiplier=subscription.multiplier,
        user_uid=user.uid,
        user_name=user.name,
        category_uid=category.uid,
        category_name=category.name,
        active=subscription.active
    )


@router.get(path="/{uid}", response_model=SubscriptionResponse)
def get_subscription(uid: str) -> SubscriptionResponse:
    """Get subscription by ID"""
    subscription: Subscription | None = subscription_repo.get_by_id(uid=uid)
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    return SubscriptionResponse(
        uid=subscription.uid,
        name=subscription.name,
        amount=subscription.amount,
        interval=subscription.interval.value,
        multiplier=subscription.multiplier,
        user_uid=subscription.user.uid,
        user_name=subscription.user.name,
        category_uid=subscription.category.uid,
        category_name=subscription.category.name,
        active=subscription.active
    )


@router.get(path="/", response_model=list[SubscriptionResponse])
def get_all_subscriptions() -> list[SubscriptionResponse]:
    """Get all subscriptions"""
    subscriptions: list[Subscription] = subscription_repo.get_all()
    return [
        SubscriptionResponse(
            uid=sub.uid,
            name=sub.name,
            amount=sub.amount,
            interval=sub.interval.value,
            multiplier=sub.multiplier,
            user_uid=sub.user.uid,
            user_name=sub.user.name,
            category_uid=sub.category.uid,
            category_name=sub.category.name,
            active=sub.active
        )
        for sub in subscriptions
    ]


@router.put(path="/{uid}", response_model=SubscriptionResponse)
def update_subscription(uid: str, subscription_data: SubscriptionUpdate) -> SubscriptionResponse:
    """Update subscription"""
    existing_subscription: Subscription | None = subscription_repo.get_by_id(uid=uid)
    if not existing_subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    
    user: User | None = user_repo.get_by_id(uid=subscription_data.user_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    category: Category | None = category_repo.get_by_id(uid=subscription_data.category_uid)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    subscription: Subscription = Subscription(
        uid=uid,
        name=subscription_data.name,
        amount=subscription_data.amount,
        interval=Interval(value=subscription_data.interval),
        multiplier=subscription_data.multiplier,
        user=user,
        category=category,
        active=subscription_data.active
    )
    success: bool = subscription_repo.update(entity=subscription)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Update failed")
    
    return SubscriptionResponse(
        uid=subscription.uid,
        name=subscription.name,
        amount=subscription.amount,
        interval=subscription.interval.value,
        multiplier=subscription.multiplier,
        user_uid=user.uid,
        user_name=user.name,
        category_uid=category.uid,
        category_name=category.name,
        active=subscription.active
    )


@router.delete(path="/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(uid: str) -> None:
    """Delete subscription"""
    success: bool = subscription_repo.delete(uid=uid)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
