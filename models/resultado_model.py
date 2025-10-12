from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QuestionResult(BaseModel):
    questao_id: str = Field(..., description="ID da questão")
    codigo: str = Field(..., description="Código da questão")
    resposta_dada: str = Field(..., description="Resposta dada pelo usuário")
    gabarito: str = Field(..., description="Gabarito correto")
    acertou: bool = Field(..., description="Se o usuário acertou a questão")


class ResultadoCreate(BaseModel):
    email: str = Field(..., description="Email do aluno que respondeu")
    disciplina: str = Field(..., description="Disciplina do resultado")
    ano: int = Field(..., ge=1, le=12, description="Ano escolar")
    respostas: List[QuestionResult] = Field(..., description="Lista de respostas")
    pontuacao: int = Field(..., ge=0, description="Pontuação obtida")
    total_questoes: int = Field(..., ge=1, description="Total de questões")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "aluno@exemplo.com",
                "disciplina": "LP",
                "ano": 5,
                "respostas": [
                    {
                        "questao_id": "68d7ef4e3e32658cf3a7ac42",
                        "codigo": "EF05LP01",
                        "resposta_dada": "B",
                        "gabarito": "B",
                        "acertou": True
                    }
                ],
                "pontuacao": 8,
                "total_questoes": 10
            }
        }


class ResultadoResponse(BaseModel):
    id: str = Field(..., description="ID do resultado")
    email: str = Field(..., description="Email do aluno que respondeu")
    disciplina: str = Field(..., description="Disciplina do resultado")
    ano: int = Field(..., description="Ano escolar")
    respostas: List[QuestionResult] = Field(..., description="Lista de respostas")
    pontuacao: int = Field(..., description="Pontuação obtida")
    total_questoes: int = Field(..., description="Total de questões")
    percentual_acerto: float = Field(..., description="Percentual de acerto")
    created_at: Optional[str] = Field(None, description="Data de criação")
    updated_at: Optional[str] = Field(None, description="Data de atualização")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "674f8a1b2c3d4e5f67890abc",
                "email": "aluno@exemplo.com",
                "disciplina": "LP",
                "ano": 5,
                "respostas": [
                    {
                        "questao_id": "68d7ef4e3e32658cf3a7ac42",
                        "codigo": "EF05LP01",
                        "resposta_dada": "B",
                        "gabarito": "B",
                        "acertou": True
                    }
                ],
                "pontuacao": 8,
                "total_questoes": 10,
                "percentual_acerto": 80.0,
                "created_at": "2024-12-03T10:30:00.000Z",
                "updated_at": "2024-12-03T10:30:00.000Z"
            }
        }
