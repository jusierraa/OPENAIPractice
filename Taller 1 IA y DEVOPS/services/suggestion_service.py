"""
Capa de Lógica de Negocio — HU5: Sugerencias de Conexión.
SRP: única responsabilidad = generación de sugerencias basadas en hobbies/ubicación.
DIP: depende de las abstracciones de repositorio.
"""

from models.user import User
from repositories.connection_repository import ConnectionRepository
from repositories.user_repository import UserRepository


class SuggestionService:
    """
    Analiza los hobbies y la ubicación del usuario para generar
    sugerencias de conexión ordenadas por relevancia.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        connection_repo: ConnectionRepository,
    ):
        self._user_repo = user_repo
        self._connection_repo = connection_repo

    def get_suggestions(self, user_id: int) -> list[tuple[User, str]]:
        """
        Devuelve lista de (User, razón_de_sugerencia) ordenada por relevancia.
        Se excluyen: el propio usuario, conexiones ya aceptadas,
        solicitudes recibidas pendientes y solicitudes enviadas pendientes.
        """
        current_user = self._user_repo.get_by_id(user_id)
        if not current_user:
            return []

        # IDs a excluir de las sugerencias
        accepted_ids  = set(self._connection_repo.get_accepted_ids_for_user(user_id))
        received_pending = {
            c.requester_id
            for c in self._connection_repo.get_pending_for_user(user_id)
        }
        sent_pending = set(self._connection_repo.get_sent_pending_for_user(user_id))
        excluded = accepted_ids | received_pending | sent_pending | {user_id}

        my_hobbies = set(current_user.hobbies_list)
        suggestions: list[tuple[User, str, int]] = []

        for user in self._user_repo.get_all():
            if user.id in excluded:
                continue

            reasons: list[str] = []
            score = 0

            shared = my_hobbies & set(user.hobbies_list)
            if shared:
                reasons.append(f"Hobbies en común: {', '.join(sorted(shared))}")
                score += len(shared)

            if (
                current_user.ubicacion.strip().lower()
                == user.ubicacion.strip().lower()
                and user.ubicacion.strip()
            ):
                reasons.append("Misma ubicación")
                score += 1

            if reasons:
                suggestions.append((user, " | ".join(reasons), score))

        # Ordenar de mayor a menor relevancia
        suggestions.sort(key=lambda x: x[2], reverse=True)
        return [(user, reason) for user, reason, _ in suggestions]
