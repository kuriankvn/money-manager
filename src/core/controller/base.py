from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any
from fastapi import HTTPException, status
from pydantic import BaseModel
from core.repositories.base import IRepository
from core.utils import generate_uid
from core.utils.exceptions import DuplicateEntityError

T = TypeVar(name='T')  # Entity type
TModel = TypeVar(name='TModel', bound=BaseModel)  # Model type
TResponse = TypeVar(name='TResponse', bound=BaseModel)  # Response type


class BaseController(ABC, Generic[T, TModel, TResponse]):
    """Base controller with common CRUD logic"""
    
    @property
    @abstractmethod
    def repository(self) -> IRepository[T]:
        """Return the repository for this controller"""
        pass
    
    @property
    @abstractmethod
    def entity_name(self) -> str:
        """Return the entity name (e.g., 'Category', 'Account')"""
        pass
    
    @abstractmethod
    def model_to_entity(self, uid: str, model: TModel) -> T:
        """Convert model to entity with given uid"""
        pass
    
    @abstractmethod
    def entity_to_response(self, entity: T) -> TResponse:
        """Convert entity to response model"""
        pass
    
    def validate_dependencies(self, model: TModel) -> None:
        """Override to validate foreign key dependencies before create/update"""
        pass
    
    def create(self, data: TModel) -> TResponse:
        """Create entity"""
        self.validate_dependencies(model=data)
        
        uid: str = generate_uid()
        entity: T = self.model_to_entity(uid, model=data)
        
        try:
            self.repository.create(entity=entity)
        except DuplicateEntityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        
        return self.entity_to_response(entity)
    
    def get_by_id(self, uid: str) -> TResponse:
        """Get entity by ID"""
        entity: Optional[T] = self.repository.get_by_id(uid=uid)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.entity_name} not found"
            )
        return self.entity_to_response(entity)
    
    def get_all(self) -> list[TResponse]:
        """Get all entities"""
        entities: list[T] = self.repository.get_all()
        return [self.entity_to_response(entity) for entity in entities]
    
    def update(self, uid: str, data: TModel) -> TResponse:
        """Update entity"""
        existing: Optional[T] = self.repository.get_by_id(uid=uid)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.entity_name} not found"
            )
        
        self.validate_dependencies(model=data)
        
        entity: T = self.model_to_entity(uid, model=data)
        
        try:
            success: bool = self.repository.update(entity=entity)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Update failed"
                )
        except DuplicateEntityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        
        return self.entity_to_response(entity)
    
    def delete(self, uid: str) -> None:
        """Delete entity"""
        success: bool = self.repository.delete(uid=uid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.entity_name} not found"
            )

# Made with Bob