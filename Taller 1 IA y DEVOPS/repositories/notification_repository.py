"""
Capa de Datos — Repositorio de Notificaciones.
SRP: única responsabilidad = acceso a la tabla 'notifications'.
"""

from typing import Optional
from models.notification import Notification
from repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):

    # ── Lectura ────────────────────────────────────────────────
    def get_by_id(self, notif_id: int) -> Optional[Notification]:
        with self._db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM notifications WHERE id=?", (notif_id,)
            ).fetchone()
            return self._to_notif(row) if row else None

    def get_all(self) -> list[Notification]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM notifications").fetchall()
            return [self._to_notif(r) for r in rows]

    def get_for_user(self, user_id: int, unread_only: bool = False) -> list[Notification]:
        with self._db.get_connection() as conn:
            sql = "SELECT * FROM notifications WHERE user_id=?"
            params: list = [user_id]
            if unread_only:
                sql += " AND is_read=0"
            sql += " ORDER BY created_at DESC"
            rows = conn.execute(sql, params).fetchall()
            return [self._to_notif(r) for r in rows]

    # ── Escritura ──────────────────────────────────────────────
    def save(self, notif: Notification) -> Notification:
        with self._db.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)",
                (notif.user_id, notif.type, notif.message),
            )
            conn.commit()
            notif.id = cur.lastrowid
            return notif

    def update(self, notif: Notification) -> bool:
        with self._db.get_connection() as conn:
            affected = conn.execute(
                "UPDATE notifications SET is_read=? WHERE id=?",
                (1 if notif.is_read else 0, notif.id),
            ).rowcount
            conn.commit()
            return affected > 0

    def mark_all_read(self, user_id: int) -> None:
        with self._db.get_connection() as conn:
            conn.execute(
                "UPDATE notifications SET is_read=1 WHERE user_id=?", (user_id,)
            )
            conn.commit()

    def delete(self, notif_id: int) -> bool:
        with self._db.get_connection() as conn:
            affected = conn.execute(
                "DELETE FROM notifications WHERE id=?", (notif_id,)
            ).rowcount
            conn.commit()
            return affected > 0

    # ── Mapeo fila → objeto ────────────────────────────────────
    @staticmethod
    def _to_notif(row) -> Notification:
        return Notification(
            id=row["id"],
            user_id=row["user_id"],
            type=row["type"],
            message=row["message"],
            is_read=bool(row["is_read"]),
            created_at=row["created_at"],
        )
