"""
Capa de Presentación — HU4: Feed de Actividades.
SRP: única responsabilidad = renderizar el feed y gestionar interacciones.
"""

from models.user import User
from services.feed_service import FeedService

SEP = "=" * 52


class FeedView:
    """Vistas de consola para el feed, publicaciones, me gusta y comentarios."""

    def __init__(self, feed_service: FeedService):
        self._service = feed_service

    # ── Menú principal ─────────────────────────────────────────
    def show_menu(self, current_user: User) -> None:
        while True:
            print(f"\n{SEP}")
            print("          FEED DE ACTIVIDADES")
            print(SEP)
            print("  1. Ver feed de mis conexiones")
            print("  2. Ver mis publicaciones")
            print("  3. Crear nueva publicación")
            print("  0. Volver al menú principal")

            opt = input("\n  Opción: ").strip()
            if opt == "1":
                self._show_feed(current_user)
            elif opt == "2":
                self._show_my_posts(current_user)
            elif opt == "3":
                self._create_post(current_user)
            elif opt == "0":
                break
            else:
                print("  Opción no válida.")

    # ── Sub-pantallas ──────────────────────────────────────────
    def _show_feed(self, current_user: User) -> None:
        posts = self._service.get_feed(current_user.id)
        if not posts:
            print("\n  Tu feed está vacío.")
            print("  Conecta con otros usuarios para ver sus publicaciones.")
            return
        self._render_posts(posts, current_user)

    def _show_my_posts(self, current_user: User) -> None:
        posts = self._service.get_my_posts(current_user.id)
        if not posts:
            print("\n  Aún no has publicado nada.")
            return
        self._render_posts(posts, current_user)

    def _render_posts(self, posts, current_user: User) -> None:
        """Muestra la lista de publicaciones y ofrece interacción."""
        print(f"\n  {'#':<4} {'Autor':<22} {'Fecha':<22} {'Likes':>6}  Contenido")
        print("  " + "-" * 70)
        for i, p in enumerate(posts, 1):
            contenido = (p.content[:35] + "...") if len(p.content) > 35 else p.content
            print(
                f"  {i:<4} {(p.autor_nombre or 'Desconocido'):<22} "
                f"{(p.created_at or ''):<22} {p.likes_count:>6}  {contenido}"
            )

        sel = input("\n  Número de publicación para interactuar (0 = salir): ").strip()
        if sel == "0" or not sel.isdigit():
            return

        idx = int(sel) - 1
        if idx < 0 or idx >= len(posts):
            print("  Selección fuera de rango.")
            return

        self._interact(posts[idx], current_user)

    def _interact(self, post, current_user: User) -> None:
        print(f"  --- Publicacion #{post.id} ---")
        print(f"  {post.autor_nombre}: {post.content}")
        print(f"  {post.likes_count} me gusta\n")
        print("  1. Dar / quitar Me gusta")
        print("  2. Comentar")
        print("  3. Ver comentarios")
        print("  0. Volver")

        opt = input("\n  Opción: ").strip()
        if opt == "1":
            ok, msg = self._service.toggle_like(post.id, current_user.id)
            print(f"\n  {'[OK]' if ok else '[X]'} {msg}")
        elif opt == "2":
            content = input("  Tu comentario: ").strip()
            ok, msg = self._service.comment_on_post(post.id, current_user.id, content)
            print(f"\n  {'[OK]' if ok else '[X]'} {msg}")
        elif opt == "3":
            comments = self._service.get_comments(post.id)
            if not comments:
                print("\n  Esta publicación no tiene comentarios aún.")
            else:
                print()
                for c in comments:
                    print(f"  [{c['created_at']}] {c['autor']}: {c['content']}")

    def _create_post(self, current_user: User) -> None:
        print(f"\n{SEP}")
        print("          NUEVA PUBLICACIÓN")
        print(SEP)
        content = input("  ¿Qué quieres compartir?\n  > ").strip()
        ok, msg = self._service.create_post(current_user.id, content)
        print(f"\n  {'[OK]' if ok else '[X]'} {msg}")
