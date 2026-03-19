"""
Modelo de dominio — Usuario.
SRP: sólo representa los datos de un usuario.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    nombres:       str
    apellidos:     str
    telefono:      str
    ubicacion:     str
    password_hash: str
    descripcion:   str = ""
    hobbies:       str = ""
    foto_perfil:   str = ""
    id:            Optional[int] = None
    created_at:    Optional[str] = None

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"

    @property
    def hobbies_list(self) -> list[str]:
        """Devuelve los hobbies como lista normalizada en minúsculas."""
        return [h.strip().lower() for h in self.hobbies.split(",") if h.strip()]
