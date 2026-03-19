"""
Capa de Datos — Repositorio de Usuarios.
SRP: única responsabilidad = acceso a la tabla 'users'.
LSP: cumple íntegramente el contrato de BaseRepository.
"""

from typing import Optional
from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):

    # ── Lectura ────────────────────────────────────────────────
    def get_by_id(self, user_id: int) -> Optional[User]:
        with self._db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return self._to_user(row) if row else None

    def get_all(self) -> list[User]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM users").fetchall()
            return [self._to_user(r) for r in rows]

    def get_by_telefono(self, telefono: str) -> Optional[User]:
        with self._db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE telefono = ?", (telefono,)
            ).fetchone()
            return self._to_user(row) if row else None

    def search_by_name_or_hobby(self, query: str) -> list[User]:
        """Búsqueda parcial e insensible a mayúsculas por nombre o hobby."""
        q = f"%{query.lower()}%"
        with self._db.get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM users
                   WHERE LOWER(nombres)   LIKE ?
                      OR LOWER(apellidos) LIKE ?
                      OR LOWER(hobbies)   LIKE ?""",
                (q, q, q),
            ).fetchall()
            return [self._to_user(r) for r in rows]

    # ── Escritura ──────────────────────────────────────────────
    def save(self, user: User) -> User:
        with self._db.get_connection() as conn:
            cur = conn.execute(
                """INSERT INTO users
                   (nombres, apellidos, telefono, ubicacion, password_hash,
                    descripcion, hobbies, foto_perfil)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user.nombres, user.apellidos, user.telefono,
                    user.ubicacion, user.password_hash,
                    user.descripcion, user.hobbies, user.foto_perfil,
                ),
            )
            conn.commit()
            user.id = cur.lastrowid
            return user

    def update(self, user: User) -> bool:
        with self._db.get_connection() as conn:
            affected = conn.execute(
                """UPDATE users
                   SET nombres=?, apellidos=?, telefono=?, ubicacion=?,
                       descripcion=?, hobbies=?, foto_perfil=?
                   WHERE id=?""",
                (
                    user.nombres, user.apellidos, user.telefono,
                    user.ubicacion, user.descripcion, user.hobbies,
                    user.foto_perfil, user.id,
                ),
            ).rowcount
            conn.commit()
            return affected > 0

    def delete(self, user_id: int) -> bool:
        with self._db.get_connection() as conn:
            affected = conn.execute(
                "DELETE FROM users WHERE id = ?", (user_id,)
            ).rowcount
            conn.commit()
            return affected > 0

    # ── Mapeo fila → objeto ────────────────────────────────────
    @staticmethod
    def _to_user(row) -> User:
        return User(
            id=row["id"],
            nombres=row["nombres"],
            apellidos=row["apellidos"],
            telefono=row["telefono"],
            ubicacion=row["ubicacion"],
            password_hash=row["password_hash"],
            descripcion=row["descripcion"] or "",
            hobbies=row["hobbies"] or "",
            foto_perfil=row["foto_perfil"] or "",
            created_at=row["created_at"],
        )
