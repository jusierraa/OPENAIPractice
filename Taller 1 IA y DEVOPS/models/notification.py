"""
Modelo de dominio — Notificación.
SRP: sólo representa una notificación para un usuario.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Notification:
    user_id:    int
    type:       str          # connection_request | connection_accepted
    message:    str
    is_read:    bool = False
    id:         Optional[int] = None
    created_at: Optional[str] = None
