"""
Capa de Lógica de Negocio — HU2: Creación/Edición de Perfil.
SRP: única responsabilidad = gestión del perfil de usuario.
DIP: depende de la abstracción UserRepository.
"""

import os
from models.user import User
from repositories.user_repository import UserRepository


class ProfileService:
    """Gestiona la consulta y actualización del perfil de un usuario."""

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def get_profile(self, user_id: int) -> User | None:
        return self._user_repo.get_by_id(user_id)

    def update_profile(
        self,
        user: User,
        descripcion: str | None = None,
        hobbies: str | None = None,
        foto_perfil: str | None = None,
    ) -> tuple[bool, str]:
        """
        Actualiza descripción, hobbies y/o foto de perfil.
        Sólo modifica los campos que se pasan como argumento.
        Retorna (True, mensaje_éxito) o (False, mensaje_error).
        """
        if descripcion is not None:
            user.descripcion = descripcion.strip()

        if hobbies is not None:
            user.hobbies = hobbies.strip()

        if foto_perfil is not None:
            ruta = foto_perfil.strip()
            if ruta and not os.path.exists(ruta):
                return False, f"La ruta de la foto no existe: '{ruta}'"
            user.foto_perfil = ruta

        if self._user_repo.update(user):
            return True, "Perfil actualizado correctamente."
        return False, "No se pudo actualizar el perfil. Intenta de nuevo."

    def get_all_users_except(self, current_user_id: int) -> list[User]:
        """Devuelve todos los usuarios excepto el actual (útil para búsquedas)."""
        return [u for u in self._user_repo.get_all() if u.id != current_user_id]
