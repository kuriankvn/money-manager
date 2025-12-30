from typing import Optional
from fastapi import APIRouter, status, HTTPException
from core.repositories import SubscriptionRepository, SubscriptionInstanceRepository
from core.domain import Subscription, SubscriptionInstance
from core.domain import SubscriptionSchema, SubscriptionResponse, SubscriptionInstanceSchema, SubscriptionInstanceResponse
from core.controller.base import BaseController


# Subscription Controller
class SubscriptionController(BaseController[Subscription, SubscriptionSchema, SubscriptionResponse]):
    """Subscription controller with CRUD operations"""
    
    def __init__(self) -> None:
        self._repository = SubscriptionRepository()
    
    @property
    def repository(self) -> SubscriptionRepository:
        return self._repository
    
    @property
    def entity_name(self) -> str:
        return "Subscription"
    
    def model_to_entity(self, uid: str, model: SubscriptionSchema) -> Subscription:
        return Subscription(
            uid=uid,
            name=model.name,
            amount=model.amount,
            frequency=model.frequency,
            interval=model.interval,
            due_day=model.due_day,
            due_month=model.due_month,
            status=model.status
        )
    
    def entity_to_response(self, entity: Subscription) -> SubscriptionResponse:
        return SubscriptionResponse(
            uid=entity.uid,
            name=entity.name,
            amount=entity.amount,
            frequency=entity.frequency,
            interval=entity.interval,
            due_day=entity.due_day,
            due_month=entity.due_month,
            status=entity.status
        )


# Subscription Instance Controller
class SubscriptionInstanceController(BaseController[SubscriptionInstance, SubscriptionInstanceSchema, SubscriptionInstanceResponse]):
    """Subscription instance controller with CRUD operations"""
    
    def __init__(self) -> None:
        self._repository = SubscriptionInstanceRepository()
        self.subscription_repo = SubscriptionRepository()
    
    @property
    def repository(self) -> SubscriptionInstanceRepository:
        return self._repository
    
    @property
    def entity_name(self) -> str:
        return "Subscription instance"
    
    def validate_dependencies(self, model: SubscriptionInstanceSchema) -> None:
        """Validate subscription exists"""
        subscription: Optional[Subscription] = self.subscription_repo.get_by_id(uid=model.subscription_id)
        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    
    def model_to_entity(self, uid: str, model: SubscriptionInstanceSchema) -> SubscriptionInstance:
        return SubscriptionInstance(
            uid=uid,
            subscription_id=model.subscription_id,
            amount=model.amount,
            due_date=model.due_date,
            transaction_id=model.transaction_id,
            status=model.status
        )
    
    def entity_to_response(self, entity: SubscriptionInstance) -> SubscriptionInstanceResponse:
        return SubscriptionInstanceResponse(
            uid=entity.uid,
            subscription_id=entity.subscription_id,
            amount=entity.amount,
            due_date=entity.due_date,
            transaction_id=entity.transaction_id,
            status=entity.status
        )


# Initialize controllers and routers
subscription_controller: SubscriptionController = SubscriptionController()
subscriptions_router: APIRouter = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

subscription_instance_controller: SubscriptionInstanceController = SubscriptionInstanceController()
subscription_instances_router: APIRouter = APIRouter(prefix="/subscription-instances", tags=["subscription-instances"])


# Subscription Routes
@subscriptions_router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(subscription_data: SubscriptionSchema) -> SubscriptionResponse:
    """Create a new subscription"""
    return subscription_controller.create(data=subscription_data)


@subscriptions_router.get("/{uid}", response_model=SubscriptionResponse)
def get_subscription(uid: str) -> SubscriptionResponse:
    """Get subscription by ID"""
    return subscription_controller.get_by_id(uid)


@subscriptions_router.get("/", response_model=list[SubscriptionResponse])
def get_all_subscriptions() -> list[SubscriptionResponse]:
    """Get all subscriptions"""
    return subscription_controller.get_all()


@subscriptions_router.put("/{uid}", response_model=SubscriptionResponse)
def update_subscription(uid: str, subscription_data: SubscriptionSchema) -> SubscriptionResponse:
    """Update subscription"""
    return subscription_controller.update(uid, data=subscription_data)


@subscriptions_router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(uid: str) -> None:
    """Delete subscription"""
    subscription_controller.delete(uid)


# Subscription Instance Routes
@subscription_instances_router.post("/", response_model=SubscriptionInstanceResponse, status_code=status.HTTP_201_CREATED)
def create_subscription_instance(instance_data: SubscriptionInstanceSchema) -> SubscriptionInstanceResponse:
    """Create a new subscription instance"""
    return subscription_instance_controller.create(data=instance_data)


@subscription_instances_router.get("/{uid}", response_model=SubscriptionInstanceResponse)
def get_subscription_instance(uid: str) -> SubscriptionInstanceResponse:
    """Get subscription instance by ID"""
    return subscription_instance_controller.get_by_id(uid)


@subscription_instances_router.get("/", response_model=list[SubscriptionInstanceResponse])
def get_all_subscription_instances() -> list[SubscriptionInstanceResponse]:
    """Get all subscription instances"""
    return subscription_instance_controller.get_all()


@subscription_instances_router.put("/{uid}", response_model=SubscriptionInstanceResponse)
def update_subscription_instance(uid: str, instance_data: SubscriptionInstanceSchema) -> SubscriptionInstanceResponse:
    """Update subscription instance"""
    return subscription_instance_controller.update(uid, data=instance_data)


@subscription_instances_router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription_instance(uid: str) -> None:
    """Delete subscription instance"""
    subscription_instance_controller.delete(uid)

# Made with Bob
