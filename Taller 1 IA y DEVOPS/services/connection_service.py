"""
Capa de Lógica de Negocio — HU3: Conexión de Usuarios.
SRP: única responsabilidad = gestión de solicitudes/conexiones.
DIP: depende de las abstracciones de repositorio, no de SQLite.
"""

from models.connection import Connection
from models.notification import Notification
from models.user import User
from repositories.connection_repository import ConnectionRepository
from repositories.notification_repository import NotificationRepository
from repositories.user_repository import UserRepository


class ConnectionService:
    """
    Gestiona el ciclo de vida de las conexiones:
    búsqueda → solicitud → aceptar/rechazar → notificación.
    """

    def __init__(
        self,
        connection_repo: ConnectionRepository,
        user_repo: UserRepository,
        notif_repo: NotificationRepository,
    ):
        self._connection_repo = connection_repo
        self._user_repo = user_repo
        self._notif_repo = notif_repo

    # ── Búsqueda ───────────────────────────────────────────────
    def search_users(self, query: str, current_user_id: int) -> list[User]:
        results = self._user_repo.search_by_name_or_hobby(query)
        return [u for u in results if u.id != current_user_id]

    # ── Solicitudes ────────────────────────────────────────────
    def send_connection_request(
        self, requester_id: int, receiver_id: int
    ) -> tuple[bool, str]:
        """Envía una solicitud de conexión y notifica al receptor."""
        if requester_id == receiver_id:
            return False, "No puedes enviarte una solicitud a ti mismo."

        receiver = self._user_repo.get_by_id(receiver_id)
        if not receiver:
            return False, "El usuario destinatario no existe."

        existing = self._connection_repo.get_connection_between(requester_id, receiver_id)
        if existing:
            estados = {"pending": "ya tiene una solicitud pendiente",
                       "accepted": "ya son conexiones",
                       "rejected": "la solicitud fue rechazada anteriormente"}
            return False, f"No se puede enviar la solicitud: {estados.get(existing.status, existing.status)}."

        requester = self._user_repo.get_by_id(requester_id)
        connection = Connection(requester_id=requester_id, receiver_id=receiver_id)
        self._connection_repo.save(connection)

        # Notificar al receptor — HU3 criterio: notificación de solicitud
        self._notif_repo.save(Notification(
            user_id=receiver_id,
            type="connection_request",
            message=f"{requester.nombre_completo} te envió una solicitud de conexión.",
        ))

        return True, f"Solicitud de conexión enviada a {receiver.nombre_completo}."

    def respond_to_request(
        self, connection_id: int, current_user_id: int, accept: bool
    ) -> tuple[bool, str]:
        """Acepta o rechaza una solicitud pendiente."""
        connection = self._connection_repo.get_by_id(connection_id)

        if not connection or connection.receiver_id != current_user_id:
            return False, "Solicitud no encontrada o no tienes permiso para responderla."

        if connection.status != "pending":
            return False, f"Esta solicitud ya fue procesada (estado: {connection.status})."

        connection.status = "accepted" if accept else "rejected"
        self._connection_repo.update(connection)

        requester = self._user_repo.get_by_id(connection.requester_id)
        receiver  = self._user_repo.get_by_id(connection.receiver_id)

        if accept:
            # Notificar al solicitante — HU3 criterio: notificación de aceptación
            self._notif_repo.save(Notification(
                user_id=connection.requester_id,
                type="connection_accepted",
                message=f"{receiver.nombre_completo} aceptó tu solicitud de conexión.",
            ))
            return True, f"¡Ahora estás conectado/a con {requester.nombre_completo}!"

        return True, f"Solicitud de {requester.nombre_completo} rechazada."

    # ── Consultas ──────────────────────────────────────────────
    def get_pending_requests(self, user_id: int) -> list[Connection]:
        return self._connection_repo.get_pending_for_user(user_id)

    def get_connections(self, user_id: int) -> list[User]:
        ids = self._connection_repo.get_accepted_ids_for_user(user_id)
        return [u for uid in ids if (u := self._user_repo.get_by_id(uid))]
