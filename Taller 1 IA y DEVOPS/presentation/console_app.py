"""
Capa de Presentación — Controlador principal de la consola.
SRP: única responsabilidad = orquestar la navegación entre vistas.
DIP: recibe todas las dependencias por inyección de constructor.
"""

import sys

from models.user import User
from presentation.auth_view import AuthView
from presentation.feed_view import FeedView
from presentation.connection_view import ConnectionView
from presentation.profile_view import ProfileView
from presentation.suggestion_view import SuggestionView
from repositories.notification_repository import NotificationRepository
from services.profile_service import ProfileService

SEP = "=" * 52


class ConsoleApp:
    """
    Orquestador principal de la aplicación.
    Maneja el flujo de navegación y el estado de sesión.
    """

    def __init__(
        self,
        auth_view: AuthView,
        profile_view: ProfileView,
        connection_view: ConnectionView,
        feed_view: FeedView,
        suggestion_view: SuggestionView,
        notif_repo: NotificationRepository,
        profile_service: ProfileService,
    ):
        self._auth_view       = auth_view
        self._profile_view    = profile_view
        self._connection_view = connection_view
        self._feed_view       = feed_view
        self._suggestion_view = suggestion_view
        self._notif_repo      = notif_repo
        self._profile_service = profile_service
        self._current_user: User | None = None

    # ── Punto de entrada ───────────────────────────────────────
    def run(self) -> None:
        print(f"\n{SEP}")
        print("       BIENVENIDO A LA RED SOCIAL")
        print(SEP)
        while True:
            if self._current_user is None:
                self._guest_menu()
            else:
                self._main_menu()

    # ── Menú sin sesión ────────────────────────────────────────
    def _guest_menu(self) -> None:
        print("\n  1. Iniciar sesión")
        print("  2. Registrarme")
        print("  0. Salir")
        opt = input("\n  Opción: ").strip()

        if opt == "1":
            user = self._auth_view.show_login()
            if user:
                self._current_user = user
        elif opt == "2":
            self._auth_view.show_register()
        elif opt == "0":
            print("\n  ¡Hasta pronto!\n")
            sys.exit(0)
        else:
            print("  Opción no válida.")

    # ── Menú principal (sesión activa) ─────────────────────────
    def _main_menu(self) -> None:
        unread = self._notif_repo.get_for_user(self._current_user.id, unread_only=True)
        notif_badge = f"  [{len(unread)} nueva(s)]" if unread else ""

        print(f"\n{SEP}")
        print(f"  Hola, {self._current_user.nombres}!")
        print(SEP)
        print("  1. Mi perfil")
        print("  2. Editar perfil")
        print("  3. Conexiones")
        print("  4. Feed de actividades")
        print("  5. Sugerencias de conexión")
        print(f"  6. Notificaciones{notif_badge}")
        print("  0. Cerrar sesión")

        opt = input("\n  Opción: ").strip()

        if opt == "1":
            # Refresca el usuario desde la BD para mostrar datos actualizados
            refreshed = self._profile_service.get_profile(self._current_user.id)
            if refreshed:
                self._current_user = refreshed
            self._profile_view.show_profile(self._current_user)

        elif opt == "2":
            self._profile_view.show_edit_profile(self._current_user)

        elif opt == "3":
            self._connection_view.show_menu(self._current_user)

        elif opt == "4":
            self._feed_view.show_menu(self._current_user)

        elif opt == "5":
            self._suggestion_view.show_suggestions(self._current_user)

        elif opt == "6":
            self._show_notifications()

        elif opt == "0":
            print(f"\n  ¡Hasta luego, {self._current_user.nombres}!\n")
            self._current_user = None

        else:
            print("  Opción no válida.")

    # ── Notificaciones ─────────────────────────────────────────
    def _show_notifications(self) -> None:
        notifications = self._notif_repo.get_for_user(self._current_user.id)
        if not notifications:
            print("\n  No tienes notificaciones.")
            return

        print(f"\n{SEP}")
        print("            NOTIFICACIONES")
        print(SEP)
        for n in notifications:
            bullet = "[*]" if not n.is_read else "[ ]"
            print(f"  {bullet} [{n.type}]")
            print(f"    {n.message}")
            print(f"    {n.created_at}\n")

        self._notif_repo.mark_all_read(self._current_user.id)
        print("  (Todas las notificaciones marcadas como leídas)")
