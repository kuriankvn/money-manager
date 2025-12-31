from typing import Any
from core.repositories.base import BaseRepository
from core.domain import Investment, InvestmentValueSnapshot, InvestmentPlan, InvestmentPlanInstance
from core.domain.base import InvestmentStatus, Frequency, InvestmentPlanStatus, InvestmentPlanInstanceStatus


class InvestmentRepository(BaseRepository[Investment]):
    @property
    def table_name(self) -> str:
        return "investments"
    
    @property
    def columns(self) -> list[str]:
        return ["name", "start_date", "status"]
    
    def _entity_to_values(self, entity: Investment) -> tuple[Any, ...]:
        return (entity.uid, entity.name, entity.start_date, entity.status.value)
    
    def _row_to_entity(self, row: tuple[Any, ...]) -> Investment:
        return Investment(
            uid=row[0],
            name=row[1],
            start_date=row[2],
            status=InvestmentStatus(value=row[3]))


class InvestmentValueSnapshotRepository(BaseRepository[InvestmentValueSnapshot]):
    @property
    def table_name(self) -> str:
        return "investment_value_snapshots"
    
    @property
    def columns(self) -> list[str]:
        return ["investment_id", "date", "current_value"]
    
    def _entity_to_values(self, entity: InvestmentValueSnapshot) -> tuple[Any, ...]:
        return (entity.uid, entity.investment_id, entity.date, entity.current_value)
    
    def _row_to_entity(self, row: tuple[Any, ...]) -> InvestmentValueSnapshot:
        return InvestmentValueSnapshot(
            uid=row[0],
            investment_id=row[1],
            date=row[2],
            current_value=row[3])


class InvestmentPlanRepository(BaseRepository[InvestmentPlan]):
    @property
    def table_name(self) -> str:
        return "investment_plans"
    
    @property
    def columns(self) -> list[str]:
        return ["investment_id", "amount", "frequency", "interval", "due_day", "due_month", "status"]
    
    def _entity_to_values(self, entity: InvestmentPlan) -> tuple[Any, ...]:
        return (entity.uid, entity.investment_id, entity.amount, entity.frequency.value,
                entity.interval, entity.due_day, entity.due_month, entity.status.value)
    
    def _row_to_entity(self, row: tuple[Any, ...]) -> InvestmentPlan:
        return InvestmentPlan(
            uid=row[0],
            investment_id=row[1],
            amount=row[2],
            frequency=Frequency(value=row[3]),
            interval=row[4],
            due_day=row[5],
            due_month=row[6],
            status=InvestmentPlanStatus(value=row[7]))


class InvestmentPlanInstanceRepository(BaseRepository[InvestmentPlanInstance]):
    @property
    def table_name(self) -> str:
        return "investment_plan_instances"
    
    @property
    def columns(self) -> list[str]:
        return ["investment_plan_id", "amount", "due_date", "transaction_id", "status"]
    
    def _entity_to_values(self, entity: InvestmentPlanInstance) -> tuple[Any, ...]:
        return (entity.uid, entity.investment_plan_id, entity.amount, entity.due_date,
                entity.transaction_id, entity.status.value)
    
    def _row_to_entity(self, row: tuple[Any, ...]) -> InvestmentPlanInstance:
        return InvestmentPlanInstance(
            uid=row[0],
            investment_plan_id=row[1],
            amount=row[2],
            due_date=row[3],
            transaction_id=row[4],
            status=InvestmentPlanInstanceStatus(value=row[5]))

# Made with Bob
