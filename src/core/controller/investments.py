from typing import Optional
from fastapi import APIRouter, status, HTTPException
from core.repositories import (
    InvestmentRepository,
    InvestmentValueSnapshotRepository,
    InvestmentPlanRepository,
    InvestmentPlanInstanceRepository
)
from core.domain import Investment, InvestmentValueSnapshot, InvestmentPlan, InvestmentPlanInstance
from core.domain import (
    InvestmentSchema, InvestmentResponse,
    InvestmentValueSnapshotSchema, InvestmentValueSnapshotResponse,
    InvestmentPlanSchema, InvestmentPlanResponse,
    InvestmentPlanInstanceSchema, InvestmentPlanInstanceResponse
)
from core.controller.base import BaseController


# Investment Controller
class InvestmentController(BaseController[Investment, InvestmentSchema, InvestmentResponse]):
    """Investment controller with CRUD operations"""
    
    def __init__(self) -> None:
        self._repository = InvestmentRepository()
    
    @property
    def repository(self) -> InvestmentRepository:
        return self._repository
    
    @property
    def entity_name(self) -> str:
        return "Investment"
    
    def model_to_entity(self, uid: str, model: InvestmentSchema) -> Investment:
        return Investment(
            uid=uid,
            name=model.name,
            start_date=model.start_date,
            status=model.status
        )
    
    def entity_to_response(self, entity: Investment) -> InvestmentResponse:
        return InvestmentResponse(
            uid=entity.uid,
            name=entity.name,
            start_date=entity.start_date,
            status=entity.status
        )


# Investment Snapshot Controller
class InvestmentSnapshotController(BaseController[InvestmentValueSnapshot, InvestmentValueSnapshotSchema, InvestmentValueSnapshotResponse]):
    """Investment snapshot controller with CRUD operations"""
    
    def __init__(self) -> None:
        self._repository = InvestmentValueSnapshotRepository()
        self.investment_repo = InvestmentRepository()
    
    @property
    def repository(self) -> InvestmentValueSnapshotRepository:
        return self._repository
    
    @property
    def entity_name(self) -> str:
        return "Investment snapshot"
    
    def validate_dependencies(self, model: InvestmentValueSnapshotSchema) -> None:
        """Validate investment exists"""
        investment: Optional[Investment] = self.investment_repo.get_by_id(uid=model.investment_id)
        if not investment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")
    
    def model_to_entity(self, uid: str, model: InvestmentValueSnapshotSchema) -> InvestmentValueSnapshot:
        return InvestmentValueSnapshot(
            uid=uid,
            investment_id=model.investment_id,
            date=model.date,
            current_value=model.current_value
        )
    
    def entity_to_response(self, entity: InvestmentValueSnapshot) -> InvestmentValueSnapshotResponse:
        return InvestmentValueSnapshotResponse(
            uid=entity.uid,
            investment_id=entity.investment_id,
            date=entity.date,
            current_value=entity.current_value
        )


# Investment Plan Controller
class InvestmentPlanController(BaseController[InvestmentPlan, InvestmentPlanSchema, InvestmentPlanResponse]):
    """Investment plan controller with CRUD operations"""
    
    def __init__(self) -> None:
        self._repository = InvestmentPlanRepository()
        self.investment_repo = InvestmentRepository()
    
    @property
    def repository(self) -> InvestmentPlanRepository:
        return self._repository
    
    @property
    def entity_name(self) -> str:
        return "Investment plan"
    
    def validate_dependencies(self, model: InvestmentPlanSchema) -> None:
        """Validate investment exists"""
        investment: Optional[Investment] = self.investment_repo.get_by_id(uid=model.investment_id)
        if not investment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")
    
    def model_to_entity(self, uid: str, model: InvestmentPlanSchema) -> InvestmentPlan:
        return InvestmentPlan(
            uid=uid,
            investment_id=model.investment_id,
            amount=model.amount,
            frequency=model.frequency,
            interval=model.interval,
            status=model.status
        )
    
    def entity_to_response(self, entity: InvestmentPlan) -> InvestmentPlanResponse:
        return InvestmentPlanResponse(
            uid=entity.uid,
            investment_id=entity.investment_id,
            amount=entity.amount,
            frequency=entity.frequency,
            interval=entity.interval,
            status=entity.status
        )


# Investment Plan Instance Controller
class InvestmentPlanInstanceController(BaseController[InvestmentPlanInstance, InvestmentPlanInstanceSchema, InvestmentPlanInstanceResponse]):
    """Investment plan instance controller with CRUD operations"""
    
    def __init__(self) -> None:
        self._repository = InvestmentPlanInstanceRepository()
        self.plan_repo = InvestmentPlanRepository()
    
    @property
    def repository(self) -> InvestmentPlanInstanceRepository:
        return self._repository
    
    @property
    def entity_name(self) -> str:
        return "Investment plan instance"
    
    def validate_dependencies(self, model: InvestmentPlanInstanceSchema) -> None:
        """Validate investment plan exists"""
        plan: Optional[InvestmentPlan] = self.plan_repo.get_by_id(uid=model.investment_plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment plan not found")
    
    def model_to_entity(self, uid: str, model: InvestmentPlanInstanceSchema) -> InvestmentPlanInstance:
        return InvestmentPlanInstance(
            uid=uid,
            investment_plan_id=model.investment_plan_id,
            amount=model.amount,
            due_date=model.due_date,
            transaction_id=model.transaction_id,
            status=model.status
        )
    
    def entity_to_response(self, entity: InvestmentPlanInstance) -> InvestmentPlanInstanceResponse:
        return InvestmentPlanInstanceResponse(
            uid=entity.uid,
            investment_plan_id=entity.investment_plan_id,
            amount=entity.amount,
            due_date=entity.due_date,
            transaction_id=entity.transaction_id,
            status=entity.status
        )


# Initialize controllers and routers
investment_controller: InvestmentController = InvestmentController()
investments_router: APIRouter = APIRouter(prefix="/investments", tags=["investments"])

investment_snapshot_controller: InvestmentSnapshotController = InvestmentSnapshotController()
investment_snapshots_router:APIRouter = APIRouter(prefix="/investment-snapshots", tags=["investment-snapshots"])

investment_plan_controller: InvestmentPlanController = InvestmentPlanController()
investment_plans_router: APIRouter = APIRouter(prefix="/investment-plans", tags=["investment-plans"])

investment_plan_instance_controller: InvestmentPlanInstanceController = InvestmentPlanInstanceController()
investment_plan_instances_router: APIRouter = APIRouter(prefix="/investment-plan-instances", tags=["investment-plan-instances"])


# Investment Routes
@investments_router.post("/", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
def create_investment(investment_data: InvestmentSchema) -> InvestmentResponse:
    """Create a new investment"""
    return investment_controller.create(data=investment_data)


@investments_router.get("/{uid}", response_model=InvestmentResponse)
def get_investment(uid: str) -> InvestmentResponse:
    """Get investment by ID"""
    return investment_controller.get_by_id(uid)


@investments_router.get("/", response_model=list[InvestmentResponse])
def get_all_investments() -> list[InvestmentResponse]:
    """Get all investments"""
    return investment_controller.get_all()


@investments_router.put("/{uid}", response_model=InvestmentResponse)
def update_investment(uid: str, investment_data: InvestmentSchema) -> InvestmentResponse:
    """Update investment"""
    return investment_controller.update(uid, data=investment_data)


@investments_router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment(uid: str) -> None:
    """Delete investment"""
    investment_controller.delete(uid)


# Investment Snapshot Routes
@investment_snapshots_router.post("/", response_model=InvestmentValueSnapshotResponse, status_code=status.HTTP_201_CREATED)
def create_snapshot(snapshot_data: InvestmentValueSnapshotSchema) -> InvestmentValueSnapshotResponse:
    """Create a new investment value snapshot"""
    return investment_snapshot_controller.create(data=snapshot_data)


@investment_snapshots_router.get("/{uid}", response_model=InvestmentValueSnapshotResponse)
def get_snapshot(uid: str) -> InvestmentValueSnapshotResponse:
    """Get investment value snapshot by ID"""
    return investment_snapshot_controller.get_by_id(uid)


@investment_snapshots_router.get("/", response_model=list[InvestmentValueSnapshotResponse])
def get_all_snapshots() -> list[InvestmentValueSnapshotResponse]:
    """Get all investment value snapshots"""
    return investment_snapshot_controller.get_all()


@investment_snapshots_router.put("/{uid}", response_model=InvestmentValueSnapshotResponse)
def update_snapshot(uid: str, snapshot_data: InvestmentValueSnapshotSchema) -> InvestmentValueSnapshotResponse:
    """Update investment value snapshot"""
    return investment_snapshot_controller.update(uid, data=snapshot_data)


@investment_snapshots_router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snapshot(uid: str) -> None:
    """Delete investment value snapshot"""
    investment_snapshot_controller.delete(uid)


# Investment Plan Routes
@investment_plans_router.post("/", response_model=InvestmentPlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(plan_data: InvestmentPlanSchema) -> InvestmentPlanResponse:
    """Create a new investment plan"""
    return investment_plan_controller.create(data=plan_data)


@investment_plans_router.get("/{uid}", response_model=InvestmentPlanResponse)
def get_plan(uid: str) -> InvestmentPlanResponse:
    """Get investment plan by ID"""
    return investment_plan_controller.get_by_id(uid)


@investment_plans_router.get("/", response_model=list[InvestmentPlanResponse])
def get_all_plans() -> list[InvestmentPlanResponse]:
    """Get all investment plans"""
    return investment_plan_controller.get_all()


@investment_plans_router.put("/{uid}", response_model=InvestmentPlanResponse)
def update_plan(uid: str, plan_data: InvestmentPlanSchema) -> InvestmentPlanResponse:
    """Update investment plan"""
    return investment_plan_controller.update(uid, data=plan_data)


@investment_plans_router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(uid: str) -> None:
    """Delete investment plan"""
    investment_plan_controller.delete(uid)


# Investment Plan Instance Routes
@investment_plan_instances_router.post("/", response_model=InvestmentPlanInstanceResponse, status_code=status.HTTP_201_CREATED)
def create_plan_instance(instance_data: InvestmentPlanInstanceSchema) -> InvestmentPlanInstanceResponse:
    """Create a new investment plan instance"""
    return investment_plan_instance_controller.create(data=instance_data)


@investment_plan_instances_router.get("/{uid}", response_model=InvestmentPlanInstanceResponse)
def get_plan_instance(uid: str) -> InvestmentPlanInstanceResponse:
    """Get investment plan instance by ID"""
    return investment_plan_instance_controller.get_by_id(uid)


@investment_plan_instances_router.get("/", response_model=list[InvestmentPlanInstanceResponse])
def get_all_plan_instances() -> list[InvestmentPlanInstanceResponse]:
    """Get all investment plan instances"""
    return investment_plan_instance_controller.get_all()


@investment_plan_instances_router.put("/{uid}", response_model=InvestmentPlanInstanceResponse)
def update_plan_instance(uid: str, instance_data: InvestmentPlanInstanceSchema) -> InvestmentPlanInstanceResponse:
    """Update investment plan instance"""
    return investment_plan_instance_controller.update(uid, data=instance_data)


@investment_plan_instances_router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan_instance(uid: str) -> None:
    """Delete investment plan instance"""
    investment_plan_instance_controller.delete(uid)

# Made with Bob