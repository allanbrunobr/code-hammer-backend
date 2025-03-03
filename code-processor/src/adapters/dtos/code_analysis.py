from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum

class AnalysisTypeEnum(str, Enum):
    CODE_QUALITY = "codeQuality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUGS = "bugs"
    CODE_SMELLS = "codeSmells"
    VULNERABILITIES = "vulnerabilities"
    OWASP = "owasp"
    SOLID = "solid"
    ALL = "all"

class CodeAnalysisRequestDTO(BaseModel):
    """DTO para solicitar análise de código"""
    email: EmailStr = Field(..., description="Email do usuário")
    code: Optional[str] = None
    language: str = Field(..., description="Linguagem de programação do código")
    file_name: Optional[str] = Field(None, description="Nome do arquivo, se aplicável")
    analysis_types: List[AnalysisTypeEnum] = Field(
        default=[AnalysisTypeEnum.ALL],
        description="Tipos de análise a serem realizadas"
    )
    integration_id: Optional[str] = Field(
        None, 
        description="ID da integração a ser usada. Se não fornecido, usa a primeira integração ativa."
    )
    post_comment: bool = Field(
        default=False, 
        description="Se verdadeiro, posta o resultado como comentário no repositório."
    )

    pull_request_number: Optional[int] = Field( 
        None,
        description="Número do Pull Request a ser analisado"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "code": 'def example():\n    print("Hello World!")',
                "language": "python",
                "file_name": "example.py",
                "analysis_types": ["codeQuality", "security"],
                "integration_id": "550e8400-e29b-41d4-a716-446655440000",
                "post_comment": True,
                "pull_request_number": 123
            }
        }

class CodeAnalysisResponseDTO(BaseModel):
    """DTO para resposta da análise de código"""
    request_id: str = Field(..., description="ID da solicitação")
    message: str = Field(..., description="Mensagem informativa")
    status: str = Field(..., description="Status da solicitação")
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "Análise de código enviada. Os resultados serão processados em segundo plano.",
                "status": "processing"
            }
        }
