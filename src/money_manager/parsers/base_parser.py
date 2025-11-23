from abc import ABC, abstractmethod

import pyarrow as pa


class BaseParser(ABC):
    
    @abstractmethod
    def get_bank_name(self) -> str:
        pass
    
    @abstractmethod
    def validate_statement(self, pdf_path: str) -> bool:
        pass

    @abstractmethod
    def parse(self, pdf_path: str) -> pa.Table:
        pass
    
    @staticmethod
    def get_schema() -> pa.Schema:
        return pa.schema([
            ("datetime", pa.timestamp("s")),
            ("description", pa.string()),
            ("amount", pa.float64()),
            ("type", pa.string()),
        ])
