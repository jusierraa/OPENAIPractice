"""
Capa de Lógica de Negocio — HU4: Feed de Actividades.
SRP: única responsabilidad = gestión de publicaciones e interacciones.
DIP: depende de las abstracciones de repositorio.
"""

from models.post import Post
from repositories.post_repository import PostRepository
from repositories.connection_repository import ConnectionRepository


class FeedService:
    """
    Gestiona el feed de actividades:
      - Ver publicaciones de conexiones.
      - Crear publicaciones propias.
      - Comentar y dar 'me gusta'.
    """

    def __init__(self, post_repo: PostRepository, connection_repo: ConnectionRepository):
        self._post_repo = post_repo
        self._connection_repo = connection_repo

    # ── Feed ───────────────────────────────────────────────────
    def get_feed(self, user_id: int) -> list[Post]:
        """Devuelve las publicaciones recientes de las conexiones aceptadas."""
        return self._post_repo.get_feed_for_user(user_id)

    def get_my_posts(self, user_id: int) -> list[Post]:
        return self._post_repo.get_by_user_id(user_id)

    # ── Publicaciones ──────────────────────────────────────────
    def create_post(self, user_id: int, content: str) -> tuple[bool, str]:
        if not content.strip():
            return False, "El contenido de la publicación no puede estar vacío."
        post = Post(user_id=user_id, content=content.strip())
        saved = self._post_repo.save(post)
        return True, f"Publicación creada exitosamente (ID #{saved.id})."

    # ── Interacciones ──────────────────────────────────────────
    def comment_on_post(
        self, post_id: int, user_id: int, content: str
    ) -> tuple[bool, str]:
        if not content.strip():
            return False, "El comentario no puede estar vacío."
        if not self._post_repo.get_by_id(post_id):
            return False, "La publicación no fue encontrada."
        self._post_repo.add_comment(post_id, user_id, content.strip())
        return True, "Comentario agregado correctamente."

    def toggle_like(self, post_id: int, user_id: int) -> tuple[bool, str]:
        if not self._post_repo.get_by_id(post_id):
            return False, "La publicación no fue encontrada."
        result = self._post_repo.toggle_like(post_id, user_id)
        msg = "Me gusta agregado." if result == "added" else "Me gusta eliminado."
        return True, msg

    def get_comments(self, post_id: int) -> list[dict]:
        return self._post_repo.get_comments(post_id)
