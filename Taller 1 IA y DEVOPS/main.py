"""
Red Social — Punto de entrada de la aplicación.

Arquitectura en capas:
  ┌─────────────────────────────────────────────────┐
  │  Presentación  (presentation/)  ← consola       │
  │  Lógica de negocio (services/)  ← HU 1-5        │
  │  Datos (repositories/ + database/) ← SQLite     │
  └─────────────────────────────────────────────────┘

Aquí se realiza el ensamblaje (Dependency Injection):
los servicios reciben sus repositorios; las vistas reciben
sus servicios. Ninguna capa conoce los detalles internos
de la capa inferior (DIP — Dependency Inversion Principle).
"""

import sys
import os

# Habilita UTF-8 en la salida estándar (necesario en Windows con cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Asegura que el directorio del proyecto esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Capa de datos ──────────────────────────────────────────────
from database.db_manager import DatabaseManager
from repositories.user_repository import UserRepository
from repositories.post_repository import PostRepository
from repositories.connection_repository import ConnectionRepository
from repositories.notification_repository import NotificationRepository

# ── Capa de lógica de negocio ──────────────────────────────────
from services.auth_service import AuthService
from services.profile_service import ProfileService
from services.connection_service import ConnectionService
from services.feed_service import FeedService
from services.suggestion_service import SuggestionService

# ── Capa de presentación ───────────────────────────────────────
from presentation.auth_view import AuthView
from presentation.profile_view import ProfileView
from presentation.connection_view import ConnectionView
from presentation.feed_view import FeedView
from presentation.suggestion_view import SuggestionView
from presentation.console_app import ConsoleApp


def main() -> None:
    # 1. Infraestructura de base de datos
    db = DatabaseManager()

    # 2. Repositorios (capa de datos)
    user_repo       = UserRepository(db)
    post_repo       = PostRepository(db)
    connection_repo = ConnectionRepository(db)
    notif_repo      = NotificationRepository(db)

    # 3. Servicios (capa de lógica de negocio) — inyección de repositorios
    auth_service       = AuthService(user_repo)
    profile_service    = ProfileService(user_repo)
    connection_service = ConnectionService(connection_repo, user_repo, notif_repo)
    feed_service       = FeedService(post_repo, connection_repo)
    suggestion_service = SuggestionService(user_repo, connection_repo)

    # 4. Vistas (capa de presentación) — inyección de servicios
    auth_view       = AuthView(auth_service)
    profile_view    = ProfileView(profile_service)
    connection_view = ConnectionView(connection_service, user_repo)
    feed_view       = FeedView(feed_service)
    suggestion_view = SuggestionView(suggestion_service, connection_service)

    # 5. Controlador principal — inyección de vistas
    app = ConsoleApp(
        auth_view=auth_view,
        profile_view=profile_view,
        connection_view=connection_view,
        feed_view=feed_view,
        suggestion_view=suggestion_view,
        notif_repo=notif_repo,
        profile_service=profile_service,
    )

    app.run()


if __name__ == "__main__":
    main()
