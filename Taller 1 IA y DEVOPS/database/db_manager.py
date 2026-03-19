"""
Capa de Datos — Gestor de conexión SQLite y creación del esquema.
SRP: única responsabilidad = gestionar la conexión y el DDL.
"""

import sqlite3
import os

# La base de datos se crea en la raíz del proyecto (misma carpeta que main.py)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "red_social.db")


class DatabaseManager:
    """
    Gestiona la conexión SQLite y asegura que el esquema exista.
    OCP: para cambiar el motor de BD sólo se cambia esta clase,
         los repositorios no se modifican (DIP).
    """

    def __init__(self, db_path: str = DB_PATH):
        self._db_path = db_path
        self._initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Devuelve una conexión nueva con Row factory activada."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize_schema(self) -> None:
        """Crea todas las tablas si no existen (idempotente)."""
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombres      TEXT    NOT NULL,
                    apellidos    TEXT    NOT NULL,
                    telefono     TEXT    NOT NULL UNIQUE,
                    ubicacion    TEXT    NOT NULL,
                    password_hash TEXT   NOT NULL,
                    descripcion  TEXT    DEFAULT '',
                    hobbies      TEXT    DEFAULT '',
                    foto_perfil  TEXT    DEFAULT '',
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS posts (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    INTEGER NOT NULL,
                    content    TEXT    NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS connections (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    requester_id INTEGER NOT NULL,
                    receiver_id  INTEGER NOT NULL,
                    status       TEXT    NOT NULL DEFAULT 'pending',
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (receiver_id)  REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE (requester_id, receiver_id)
                );

                CREATE TABLE IF NOT EXISTS comments (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id    INTEGER NOT NULL,
                    user_id    INTEGER NOT NULL,
                    content    TEXT    NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id)  REFERENCES posts(id)  ON DELETE CASCADE,
                    FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS likes (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    UNIQUE (post_id, user_id),
                    FOREIGN KEY (post_id) REFERENCES posts(id)  ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id)  ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS notifications (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    INTEGER NOT NULL,
                    type       TEXT    NOT NULL,
                    message    TEXT    NOT NULL,
                    is_read    INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)
            conn.commit()
