"""
Capa de Datos — Repositorio de Conexiones.
SRP: única responsabilidad = acceso a la tabla 'connections'.
"""

from typing import Optional
from models.connection import Connection
from repositories.base_repository import BaseRepository


class ConnectionRepository(BaseRepository[Connection]):

    # ── Lectura ────────────────────────────────────────────────
    def get_by_id(self, connection_id: int) -> Optional[Connection]:
        with self._db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM connections WHERE id=?", (connection_id,)
            ).fetchone()
            return self._to_connection(row) if row else None

    def get_all(self) -> list[Connection]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM connections").fetchall()
            return [self._to_connection(r) for r in rows]

    def get_pending_for_user(self, user_id: int) -> list[Connection]:
        """Solicitudes recibidas que están pendientes de respuesta."""
        with self._db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM connections WHERE receiver_id=? AND status='pending'",
                (user_id,),
            ).fetchall()
            return [self._to_connection(r) for r in rows]

    def get_sent_pending_for_user(self, user_id: int) -> list[int]:
        """IDs de usuarios a quienes se enviaron solicitudes aún pendientes."""
        with self._db.get_connection() as conn:
            rows = conn.execute(
                "SELECT receiver_id FROM connections WHERE requester_id=? AND status='pending'",
                (user_id,),
            ).fetchall()
            return [r["receiver_id"] for r in rows]

    def get_accepted_ids_for_user(self, user_id: int) -> list[int]:
        """IDs de usuarios con quienes hay conexión aceptada."""
        with self._db.get_connection() as conn:
            rows = conn.execute(
                """SELECT requester_id, receiver_id FROM connections
                   WHERE (requester_id=? OR receiver_id=?) AND status='accepted'""",
                (user_id, user_id),
            ).fetchall()
            result = []
            for r in rows:
                other = r["receiver_id"] if r["requester_id"] == user_id else r["requester_id"]
                result.append(other)
            return result

    def get_connection_between(self, user1_id: int, user2_id: int) -> Optional[Connection]:
        with self._db.get_connection() as conn:
            row = conn.execute(
                """SELECT * FROM connections
                   WHERE (requester_id=? AND receiver_id=?)
                      OR (requester_id=? AND receiver_id=?)""",
                (user1_id, user2_id, user2_id, user1_id),
            ).fetchone()
            return self._to_connection(row) if row else None

    # ── Escritura ──────────────────────────────────────────────
    def save(self, connection: Connection) -> Connection:
        with self._db.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO connections (requester_id, receiver_id, status) VALUES (?, ?, ?)",
                (connection.requester_id, connection.receiver_id, connection.status),
            )
            conn.commit()
            connection.id = cur.lastrowid
            return connection

    def update(self, connection: Connection) -> bool:
        with self._db.get_connection() as conn:
            affected = conn.execute(
                "UPDATE connections SET status=? WHERE id=?",
                (connection.status, connection.id),
            ).rowcount
            conn.commit()
            return affected > 0

    def delete(self, connection_id: int) -> bool:
        with self._db.get_connection() as conn:
            affected = conn.execute(
                "DELETE FROM connections WHERE id=?", (connection_id,)
            ).rowcount
            conn.commit()
            return affected > 0

    # ── Mapeo fila → objeto ────────────────────────────────────
    @staticmethod
    def _to_connection(row) -> Connection:
        return Connection(
            id=row["id"],
            requester_id=row["requester_id"],
            receiver_id=row["receiver_id"],
            status=row["status"],
            created_at=row["created_at"],
        )
