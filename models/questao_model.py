from pydantic import BaseModel, Field
from typing import List, Optional

class Disciplina(BaseModel):
    codigo: str
    nome: str

class Ano(BaseModel):
    codigo: int
    descricao: str

class Alternativa(BaseModel):
    letra: str
    texto: str

class Questao(BaseModel):
    tipo: str
    enunciado: str
    imagem: Optional[str] = None
    alternativas: List[Alternativa]
    gabarito: str
    explicacao: str

class Metadados(BaseModel):
    nivel_dificuldade: str
    tempo_estimado_segundos: int
    tags: List[str]

class QuestaoCreate(BaseModel):
    disciplina: Disciplina
    ano: Ano
    codigo_habilidade: str
    questao: Questao
    metadados: Metadados

class QuestaoResponse(BaseModel):
    id: str = Field(alias="_id")
    disciplina: Disciplina
    ano: Ano
    codigo_habilidade: str
    questao: Questao
    metadados: Metadados
    
    class Config:
        populate_by_name = True