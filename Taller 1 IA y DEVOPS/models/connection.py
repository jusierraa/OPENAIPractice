"""
Modelo de dominio — Solicitud / Conexión entre usuarios.
SRP: sólo representa el vínculo entre dos usuarios.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Connection:
    requester_id: int
    receiver_id:  int
    status:       str = "pending"   # pending | accepted | rejected
    id:           Optional[int] = None
    created_at:   Optional[str] = None
