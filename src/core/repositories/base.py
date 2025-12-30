from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic, Any
import sqlite3
from core.storage.init_db import get_connection
from core.utils import DuplicateEntityError

T = TypeVar(name='T')


class IRepository(ABC, Generic[T]):
    """Base repository interface for CRUD operations"""
    
    @abstractmethod
    def create(self, entity: T) -> str:
        """Create a new entity and return its ID"""
        pass
    
    @abstractmethod
    def get_by_id(self, uid: str) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> list[T]:
        """Get all entities"""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        """Update entity and return success status"""
        pass
    
    @abstractmethod
    def delete(self, uid: str) -> bool:
        """Delete entity by ID and return success status"""
        pass


class BaseRepository(IRepository[T], ABC):
    """Generic base repository with common CRUD operations"""
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Return the table name for this repository"""
        pass
    
    @property
    @abstractmethod
    def columns(self) -> list[str]:
        """Return list of column names (excluding uid)"""
        pass
    
    @abstractmethod
    def _entity_to_values(self, entity: T) -> tuple[Any, ...]:
        """Convert entity to tuple of values for database (uid first, then other columns)"""
        pass
    
    @abstractmethod
    def _row_to_entity(self, row: tuple[Any, ...]) -> T:
        """Convert database row to entity"""
        pass
    
    def _get_insert_sql(self) -> str:
        all_cols: list[str] = ['uid'] + self.columns
        placeholders: str = ', '.join(['?'] * len(all_cols))
        return f"INSERT INTO {self.table_name} ({', '.join(all_cols)}) VALUES ({placeholders})"
    
    def _get_update_sql(self) -> str:
        set_clause: str = ', '.join([f"{col} = ?" for col in self.columns])
        return f"UPDATE {self.table_name} SET {set_clause} WHERE uid = ?"
    
    def _get_select_sql(self) -> str:
        all_cols: list[str] = ['uid'] + self.columns
        return f"SELECT {', '.join(all_cols)} FROM {self.table_name}"
    
    def create(self, entity: T) -> str:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        try:
            values: tuple[Any, ...] = self._entity_to_values(entity)
            cursor.execute(self._get_insert_sql(), values)
            connection.commit()
            return values[0]
        except sqlite3.IntegrityError as e:
            raise DuplicateEntityError(f"Entity already exists") from e
        finally:
            connection.close()
    
    def get_by_id(self, uid: str) -> Optional[T]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(f"{self._get_select_sql()} WHERE uid = ?", (uid,))
        row = cursor.fetchone()
        connection.close()
        
        if row:
            return self._row_to_entity(row)
        return None
    
    def get_all(self) -> list[T]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(self._get_select_sql())
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        return [self._row_to_entity(row) for row in rows]
    
    def update(self, entity: T) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        try:
            values: tuple[Any, ...] = self._entity_to_values(entity)
            # Reorder: columns values first, then uid
            update_values: tuple[Any, ...] = values[1:] + (values[0],)
            cursor.execute(self._get_update_sql(), update_values)
            affected: int = cursor.rowcount
            connection.commit()
            return affected > 0
        except sqlite3.IntegrityError as e:
            raise DuplicateEntityError(f"Entity already exists") from e
        finally:
            connection.close()
    
    def delete(self, uid: str) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {self.table_name} WHERE uid = ?", (uid,))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0
