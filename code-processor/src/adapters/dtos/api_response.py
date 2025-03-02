from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class ApiResponseDTO(BaseModel, Generic[T]):
    """DTO genérico para respostas da API"""
    success: bool = Field(..., description="Indica se a requisição foi bem-sucedida")
    message: str = Field(..., description="Mensagem informativa")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta")
    data: Optional[T] = Field(None, description="Dados da resposta")
    errors: Optional[List[str]] = Field(None, description="Lista de erros, se aplicável")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operação bem-sucedida",
                "timestamp": "2025-03-02T12:34:56.789Z",
                "data": {"id": "550e8400-e29b-41d4-a716-446655440000"},
                "errors": None
            }
        }
