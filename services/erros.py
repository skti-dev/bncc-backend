"""Módulo centralizado de exceções para a camada de serviços.

Definições:
- ServiceError: exceção base para erros na camada de serviço.
- NotFoundError: recurso não encontrado (mapeável para 404 na API).
- ValidationError: erro de validação de dados de entrada.
- DatabaseError: encapsula erros da camada de persistência.
"""
from __future__ import annotations

class ServiceError(Exception):
    """Erro genérico na camada de serviço."""
    pass


class NotFoundError(ServiceError):
    """Recurso não encontrado."""
    pass


class ValidationError(ServiceError):
    """Dados de entrada inválidos."""
    pass


class DatabaseError(ServiceError):
    """Erros relacionados ao banco de dados."""
    pass
