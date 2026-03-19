"""
Capa de Presentación — HU2: Creación/Edición de Perfil.
SRP: única responsabilidad = renderizar pantallas del perfil.
"""

from models.user import User
from services.profile_service import ProfileService

SEP = "=" * 52


class ProfileView:
    """Vistas de consola para ver y editar perfil."""

    def __init__(self, profile_service: ProfileService):
        self._service = profile_service

    # ── Pantallas públicas ─────────────────────────────────────
    def show_profile(self, user: User) -> None:
        print(f"\n{SEP}")
        print("                MI PERFIL")
        print(SEP)
        print(f"  ID          : {user.id}")
        print(f"  Nombre      : {user.nombre_completo}")
        print(f"  Teléfono    : {user.telefono}")
        print(f"  Ubicación   : {user.ubicacion}")
        print(f"  Descripción : {user.descripcion or '(sin descripción)'}")
        print(f"  Hobbies     : {user.hobbies or '(sin hobbies)'}")
        print(f"  Foto perfil : {user.foto_perfil or '(sin foto)'}")
        print(f"  Miembro desde : {user.created_at}")
        print(SEP)

    def show_edit_profile(self, user: User) -> bool:
        print(f"\n{SEP}")
        print("             EDITAR PERFIL")
        print(SEP)
        print("  (Deja en blanco para conservar el valor actual)\n")

        descripcion = input(f"  Descripción [{user.descripcion}]\n  > ").strip()
        hobbies     = input(f"  Hobbies (separados por coma) [{user.hobbies}]\n  > ").strip()
        foto        = input(f"  Ruta foto de perfil [{user.foto_perfil}]\n  > ").strip()

        # Si el usuario no escribió nada, mantenemos el valor actual
        descripcion = descripcion if descripcion else user.descripcion
        hobbies     = hobbies     if hobbies     else user.hobbies
        foto        = foto        if foto        else user.foto_perfil

        ok, msg = self._service.update_profile(user, descripcion, hobbies, foto)
        icon = "[OK]" if ok else "[X]"
        print(f"\n  {icon} {msg}")
        return ok
