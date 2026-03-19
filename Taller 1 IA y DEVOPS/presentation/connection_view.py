"""
Capa de Presentación — HU3: Conexión de Usuarios.
SRP: única responsabilidad = renderizar pantallas de conexiones.
"""

from models.user import User
from repositories.user_repository import UserRepository
from services.connection_service import ConnectionService

SEP = "=" * 52


class ConnectionView:
    """Vistas de consola para buscar usuarios, enviar y gestionar solicitudes."""

    def __init__(
        self,
        connection_service: ConnectionService,
        user_repo: UserRepository,
    ):
        self._service  = connection_service
        self._user_repo = user_repo

    # ── Menú principal ─────────────────────────────────────────
    def show_menu(self, current_user: User) -> None:
        while True:
            print(f"\n{SEP}")
            print("              CONEXIONES")
            print(SEP)
            print("  1. Buscar usuarios (por nombre o hobby)")
            print("  2. Ver solicitudes pendientes recibidas")
            print("  3. Ver mis conexiones aceptadas")
            print("  0. Volver al menú principal")

            opt = input("\n  Opción: ").strip()
            if opt == "1":
                self._search_and_connect(current_user)
            elif opt == "2":
                self._view_pending(current_user)
            elif opt == "3":
                self._view_connections(current_user)
            elif opt == "0":
                break
            else:
                print("  Opción no válida.")

    # ── Sub-pantallas ──────────────────────────────────────────
    def _search_and_connect(self, current_user: User) -> None:
        query = input("\n  Buscar por nombre o hobby: ").strip()
        if not query:
            print("  La búsqueda no puede estar vacía.")
            return

        results = self._service.search_users(query, current_user.id)
        if not results:
            print(f"\n  No se encontraron usuarios con '{query}'.")
            return

        print(f"\n  {'ID':>4}  {'Nombre':<26}  {'Ubicación':<16}  Hobbies")
        print("  " + "-" * 68)
        for u in results:
            print(f"  {u.id:>4}  {u.nombre_completo:<26}  {u.ubicacion:<16}  {u.hobbies}")

        target = input("\n  ID del usuario para enviar solicitud (0 = cancelar): ").strip()
        if target == "0" or not target.isdigit():
            return

        ok, msg = self._service.send_connection_request(current_user.id, int(target))
        icon = "[OK]" if ok else "[X]"
        print(f"\n  {icon} {msg}")

    def _view_pending(self, current_user: User) -> None:
        pending = self._service.get_pending_requests(current_user.id)
        if not pending:
            print("\n  No tienes solicitudes pendientes.")
            return

        print(f"\n  {'Sol.ID':<7}  {'De usuario':<26}  {'Fecha':<20}")
        print("  " + "-" * 60)
        for c in pending:
            user = self._user_repo.get_by_id(c.requester_id)
            nombre = user.nombre_completo if user else f"ID {c.requester_id}"
            print(f"  {c.id:<7}  {nombre:<26}  {c.created_at}")

        action = input("\n  ID de la solicitud a responder (0 = cancelar): ").strip()
        if action == "0" or not action.isdigit():
            return

        accept = input("  ¿Aceptar? (s/n): ").strip().lower() == "s"
        ok, msg = self._service.respond_to_request(int(action), current_user.id, accept)
        icon = "[OK]" if ok else "[X]"
        print(f"\n  {icon} {msg}")

    def _view_connections(self, current_user: User) -> None:
        connections = self._service.get_connections(current_user.id)
        if not connections:
            print("\n  Aún no tienes conexiones aceptadas.")
            return

        print(f"\n  {'ID':>4}  {'Nombre':<26}  {'Ubicación':<16}  Hobbies")
        print("  " + "-" * 68)
        for u in connections:
            print(f"  {u.id:>4}  {u.nombre_completo:<26}  {u.ubicacion:<16}  {u.hobbies}")
