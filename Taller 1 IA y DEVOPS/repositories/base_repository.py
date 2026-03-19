"""
Capa de Repositorios — Interfaces abstractas.

Principios SOLID aplicados:
  S — Cada interfaz tiene una sola responsabilidad (leer O escribir).
  I — ISP: IReadRepository e IWriteRepository están segregadas;
      un servicio que sólo lee sólo depende de IReadRepository.
  D — DIP: los servicios dependen de estas abstracciones,
      nunca de la implementación SQLite concreta.
  L — LSP: cualquier repositorio concreto puede sustituir a BaseRepository
      sin romper el contrato.
  O — OCP: para cambiar el backend (p.ej. PostgreSQL) sólo se agrega
      una subclase nueva; no se modifica ningún servicio.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class IReadRepository(ABC):
    """ISP — Contrato de sólo lectura."""

    @abstractmethod
    def get_by_id(self, entity_id: int):
        ...

    @abstractmethod
    def get_all(self) -> list:
        ...


class IWriteRepository(ABC):
    """ISP — Contrato de sólo escritura."""

    @abstractmethod
    def save(self, entity):
        ...

    @abstractmethod
    def update(self, entity) -> bool:
        ...

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        ...


class BaseRepository(IReadRepository, IWriteRepository, Generic[T]):
    """
    DIP / LSP — Base concreta con inyección del gestor de BD.
    Recibe un DatabaseManager por constructor (Dependency Injection).
    """

    def __init__(self, db_manager):
        self._db = db_manager
