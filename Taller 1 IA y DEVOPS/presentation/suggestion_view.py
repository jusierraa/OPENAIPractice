"""
Capa de Presentación — HU5: Sugerencias de Conexión.
SRP: única responsabilidad = renderizar la sección de sugerencias.
"""

from models.user import User
from services.connection_service import ConnectionService
from services.suggestion_service import SuggestionService

SEP = "=" * 52


class SuggestionView:
    """Vista de consola para sugerencias de nuevas conexiones."""

    def __init__(
        self,
        suggestion_service: SuggestionService,
        connection_service: ConnectionService,
    ):
        self._suggestion_service = suggestion_service
        self._connection_service = connection_service

    # ── Pantalla principal ─────────────────────────────────────
    def show_suggestions(self, current_user: User) -> None:
        print(f"\n{SEP}")
        print("        SUGERENCIAS DE CONEXIÓN")
        print(SEP)

        suggestions = self._suggestion_service.get_suggestions(current_user.id)

        if not suggestions:
            print("\n  No hay sugerencias disponibles en este momento.")
            print("  Consejo: completa tus hobbies y ubicación en tu perfil")
            print("  para recibir mejores sugerencias.")
            return

        print(f"\n  {'#':<4}  {'Nombre':<26}  {'Ubicación':<16}  Razón")
        print("  " + "-" * 75)
        for i, (user, reason) in enumerate(suggestions, 1):
            print(f"  {i:<4}  {user.nombre_completo:<26}  {user.ubicacion:<16}  {reason}")

        action = input(
            "\n  Número para enviar solicitud a ese usuario (0 = cancelar): "
        ).strip()
        if action == "0" or not action.isdigit():
            return

        idx = int(action) - 1
        if idx < 0 or idx >= len(suggestions):
            print("  Selección fuera de rango.")
            return

        target_user, _ = suggestions[idx]
        ok, msg = self._connection_service.send_connection_request(
            current_user.id, target_user.id
        )
        icon = "[OK]" if ok else "[X]"
        print(f"\n  {icon} {msg}")
