from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Dict, Optional
from enum import Enum


class DisciplinaEnum(str, Enum):
    LP = "LP"
    MA = "MA"
    CI = "CI"


class QuestaoInner(BaseModel):
    enunciado: str
    alternativas: Dict[str, str]
    gabarito: str
    url: Optional[str] = None

    @model_validator(mode="after")
    def validar_gabarito_esta_em_alternativas(cls, model):
        alternativas = model.alternativas or {}
        gabarito = model.gabarito
        if gabarito is None:
            raise ValueError("Campo 'gabarito' é obrigatório")
        if str(gabarito) not in alternativas:
            raise ValueError("'gabarito' deve ser uma das chaves de 'alternativas'")
        return model


class QuestaoCreate(BaseModel):
    disciplina: DisciplinaEnum
    ano: str
    codigo: str
    questao: QuestaoInner


class QuestaoResponse(QuestaoCreate):
    id: str = Field(alias="_id")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        populate_by_name = True