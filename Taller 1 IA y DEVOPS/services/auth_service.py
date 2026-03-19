"""
Capa de Lógica de Negocio — HU1: Registro e Inicio de Sesión.
SRP: única responsabilidad = autenticación de usuarios.
DIP: depende de la abstracción UserRepository, no de SQLite.
"""

import hashlib
from models.user import User
from repositories.user_repository import UserRepository


class AuthService:
    """Gestiona el registro y la autenticación de usuarios."""

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    # ── API pública ────────────────────────────────────────────
    def register(
        self,
        nombres: str,
        apellidos: str,
        telefono: str,
        ubicacion: str,
        password: str,
    ) -> tuple[bool, str]:
        """
        Registra un nuevo usuario.
        Retorna (True, mensaje_éxito) o (False, mensaje_error).
        """
        # Validaciones de entrada
        if not all([nombres.strip(), apellidos.strip(),
                    telefono.strip(), ubicacion.strip(), password.strip()]):
            return False, "Todos los campos son obligatorios."

        if not telefono.strip().isdigit():
            return False, "El teléfono debe contener únicamente dígitos."

        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres."

        if self._user_repo.get_by_telefono(telefono.strip()):
            return False, f"El teléfono '{telefono}' ya está registrado en el sistema."

        user = User(
            nombres=nombres.strip(),
            apellidos=apellidos.strip(),
            telefono=telefono.strip(),
            ubicacion=ubicacion.strip(),
            password_hash=self._hash(password),
        )
        saved = self._user_repo.save(user)
        return True, (
            f"¡Registro exitoso! Bienvenido/a, {saved.nombre_completo}. "
            f"Tu ID de usuario es: {saved.id}"
        )

    def login(self, telefono: str, password: str) -> tuple[bool, "User | str"]:
        """
        Autentica un usuario.
        Retorna (True, objeto_User) o (False, mensaje_error).
        """
        user = self._user_repo.get_by_telefono(telefono.strip())
        if not user:
            return False, "El teléfono ingresado no está registrado."
        if user.password_hash != self._hash(password):
            return False, "Contraseña incorrecta."
        return True, user

    # ── Helpers privados ───────────────────────────────────────
    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
