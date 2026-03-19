"""
Capa de Datos — Repositorio de Publicaciones.
SRP: única responsabilidad = acceso a las tablas 'posts', 'comments' y 'likes'.
"""

from typing import Optional
from models.post import Post
from repositories.base_repository import BaseRepository


class PostRepository(BaseRepository[Post]):

    # ── Lectura ────────────────────────────────────────────────
    def get_by_id(self, post_id: int) -> Optional[Post]:
        with self._db.get_connection() as conn:
            row = conn.execute(
                """SELECT p.*,
                          u.nombres || ' ' || u.apellidos AS autor_nombre,
                          (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.id) AS likes_count
                   FROM posts p
                   JOIN users u ON p.user_id = u.id
                   WHERE p.id = ?""",
                (post_id,),
            ).fetchone()
            return self._to_post(row) if row else None

    def get_all(self) -> list[Post]:
        with self._db.get_connection() as conn:
            rows = conn.execute(
                """SELECT p.*,
                          u.nombres || ' ' || u.apellidos AS autor_nombre,
                          (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.id) AS likes_count
                   FROM posts p
                   JOIN users u ON p.user_id = u.id
                   ORDER BY p.created_at DESC"""
            ).fetchall()
            return [self._to_post(r) for r in rows]

    def get_feed_for_user(self, user_id: int) -> list[Post]:
        """Devuelve publicaciones de las conexiones aceptadas del usuario."""
        with self._db.get_connection() as conn:
            rows = conn.execute(
                """SELECT p.*,
                          u.nombres || ' ' || u.apellidos AS autor_nombre,
                          (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.id) AS likes_count
                   FROM posts p
                   JOIN users u ON p.user_id = u.id
                   JOIN connections c
                     ON (c.requester_id = ? AND c.receiver_id  = p.user_id)
                     OR (c.receiver_id  = ? AND c.requester_id = p.user_id)
                   WHERE c.status = 'accepted'
                   ORDER BY p.created_at DESC""",
                (user_id, user_id),
            ).fetchall()
            return [self._to_post(r) for r in rows]

    def get_by_user_id(self, user_id: int) -> list[Post]:
        with self._db.get_connection() as conn:
            rows = conn.execute(
                """SELECT p.*,
                          u.nombres || ' ' || u.apellidos AS autor_nombre,
                          (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.id) AS likes_count
                   FROM posts p
                   JOIN users u ON p.user_id = u.id
                   WHERE p.user_id = ?
                   ORDER BY p.created_at DESC""",
                (user_id,),
            ).fetchall()
            return [self._to_post(r) for r in rows]

    def get_comments(self, post_id: int) -> list[dict]:
        with self._db.get_connection() as conn:
            rows = conn.execute(
                """SELECT c.content, c.created_at,
                          u.nombres || ' ' || u.apellidos AS autor
                   FROM comments c
                   JOIN users u ON c.user_id = u.id
                   WHERE c.post_id = ?
                   ORDER BY c.created_at ASC""",
                (post_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    # ── Escritura ──────────────────────────────────────────────
    def save(self, post: Post) -> Post:
        with self._db.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO posts (user_id, content) VALUES (?, ?)",
                (post.user_id, post.content),
            )
            conn.commit()
            post.id = cur.lastrowid
            return post

    def update(self, post: Post) -> bool:
        with self._db.get_connection() as conn:
            affected = conn.execute(
                "UPDATE posts SET content=? WHERE id=?",
                (post.content, post.id),
            ).rowcount
            conn.commit()
            return affected > 0

    def delete(self, post_id: int) -> bool:
        with self._db.get_connection() as conn:
            affected = conn.execute(
                "DELETE FROM posts WHERE id=?", (post_id,)
            ).rowcount
            conn.commit()
            return affected > 0

    def add_comment(self, post_id: int, user_id: int, content: str) -> None:
        with self._db.get_connection() as conn:
            conn.execute(
                "INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
                (post_id, user_id, content),
            )
            conn.commit()

    def toggle_like(self, post_id: int, user_id: int) -> str:
        """Alterna el 'me gusta'. Devuelve 'added' o 'removed'."""
        with self._db.get_connection() as conn:
            existing = conn.execute(
                "SELECT id FROM likes WHERE post_id=? AND user_id=?",
                (post_id, user_id),
            ).fetchone()
            if existing:
                conn.execute(
                    "DELETE FROM likes WHERE post_id=? AND user_id=?",
                    (post_id, user_id),
                )
                conn.commit()
                return "removed"
            conn.execute(
                "INSERT INTO likes (post_id, user_id) VALUES (?, ?)",
                (post_id, user_id),
            )
            conn.commit()
            return "added"

    # ── Mapeo fila → objeto ────────────────────────────────────
    @staticmethod
    def _to_post(row) -> Post:
        keys = row.keys()
        post = Post(
            id=row["id"],
            user_id=row["user_id"],
            content=row["content"],
            created_at=row["created_at"],
            autor_nombre=row["autor_nombre"] if "autor_nombre" in keys else None,
            likes_count=row["likes_count"] if "likes_count" in keys else 0,
        )
        return post
