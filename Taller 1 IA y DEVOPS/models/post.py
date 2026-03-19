"""
Modelo de dominio — Publicación.
SRP: sólo representa los datos de una publicación.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Post:
    user_id:      int
    content:      str
    id:           Optional[int] = None
    created_at:   Optional[str] = None
    autor_nombre: Optional[str] = None
    likes_count:  int = 0
    comments:     list = field(default_factory=list)
