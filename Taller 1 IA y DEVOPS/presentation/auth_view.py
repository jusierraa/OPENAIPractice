"""
Capa de Presentación — HU1: Registro e Inicio de Sesión.
SRP: única responsabilidad = renderizar pantallas de autenticación.
"""

from services.auth_service import AuthService

SEP = "=" * 52


class AuthView:
    """Vistas de consola para registro y login."""

    def __init__(self, auth_service: AuthService):
        self._auth = auth_service

    # ── Pantallas públicas ─────────────────────────────────────
    def show_register(self) -> bool:
        print(f"\n{SEP}")
        print("        REGISTRO DE NUEVO USUARIO")
        print(SEP)
        nombres   = input("  Nombres    : ").strip()
        apellidos = input("  Apellidos  : ").strip()
        telefono  = input("  Teléfono   : ").strip()
        ubicacion = input("  Ubicación  : ").strip()
        password  = input("  Contraseña : ").strip()

        ok, msg = self._auth.register(nombres, apellidos, telefono, ubicacion, password)
        icon = "[OK]" if ok else "[X]"
        print(f"\n  {icon} {msg}")
        return ok

    def show_login(self):
        """Retorna el objeto User si el login fue exitoso, None en caso contrario."""
        print(f"\n{SEP}")
        print("              INICIAR SESIÓN")
        print(SEP)
        telefono = input("  Teléfono   : ").strip()
        password = input("  Contraseña : ").strip()

        ok, result = self._auth.login(telefono, password)
        if ok:
            print(f"\n  [OK] ¡Bienvenido/a, {result.nombre_completo}!")
            return result
        print(f"\n  [X] {result}")
        return None
