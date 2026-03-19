# Red Social — Taller 1 IA y DEVOPS

Aplicación de red social de consola implementada en Python con arquitectura en capas y principios **SOLID**.

---

## Arquitectura

```
Taller 1 IA y DEVOPS/
│
├── main.py                          ← Punto de entrada + ensamblaje DI
│
├── database/
│   └── db_manager.py                ← Conexión SQLite + DDL de tablas
│
├── models/                          ← Entidades del dominio (POJOs)
│   ├── user.py
│   ├── post.py
│   ├── connection.py
│   └── notification.py
│
├── repositories/                    ← Capa de datos (acceso a SQLite)
│   ├── base_repository.py           ← Interfaces abstractas (ISP + DIP)
│   ├── user_repository.py
│   ├── post_repository.py
│   ├── connection_repository.py
│   └── notification_repository.py
│
├── services/                        ← Lógica de negocio (una por HU)
│   ├── auth_service.py              ← HU1: Registro / Login
│   ├── profile_service.py           ← HU2: Perfil
│   ├── connection_service.py        ← HU3: Conexiones
│   ├── feed_service.py              ← HU4: Feed
│   └── suggestion_service.py        ← HU5: Sugerencias
│
└── presentation/                    ← Capa de presentación (consola)
    ├── console_app.py               ← Controlador / navegación
    ├── auth_view.py
    ├── profile_view.py
    ├── connection_view.py
    ├── feed_view.py
    └── suggestion_view.py
```

### Capas

| Capa | Contenido | Justificación |
|---|---|---|
| **Presentación** | `presentation/` | Interfaz de consola. Desacoplada de la lógica; fácil de sustituir por una UI gráfica o web. |
| **Lógica de negocio** | `services/` | Contiene las reglas de cada historia de usuario. Independiente del motor de BD. |
| **Datos** | `repositories/` + `database/` | Acceso a SQLite mediante el patrón Repository. SQLite elegido por ser local, sin configuración y con soporte nativo en Python. |

---

## Principios SOLID aplicados

| Principio | Cómo se aplica |
|---|---|
| **S** Single Responsibility | Cada clase tiene una única razón de cambio: cada servicio gestiona una HU; cada repositorio gestiona una tabla. |
| **O** Open / Closed | `BaseRepository` define el contrato; cambiar el backend de BD implica agregar una nueva clase, no modificar los servicios. |
| **L** Liskov Substitution | Todos los repositorios concretos cumplen íntegramente el contrato de `BaseRepository` y son sustituibles. |
| **I** Interface Segregation | `IReadRepository` e `IWriteRepository` están separadas; un servicio que sólo lee no depende de métodos de escritura. |
| **D** Dependency Inversion | Los servicios reciben repositorios por inyección de constructor en `main.py`; nunca instancian sus dependencias. |

---

## Esquema de base de datos (SQLite)

| Tabla | Campos clave |
|---|---|
| `users` | id, nombres, apellidos, telefono (UNIQUE), ubicacion, password_hash, descripcion, hobbies, foto_perfil |
| `posts` | id, user_id (FK), content, created_at |
| `connections` | id, requester_id (FK), receiver_id (FK), status (pending/accepted/rejected) |
| `comments` | id, post_id (FK), user_id (FK), content |
| `likes` | id, post_id (FK), user_id (FK) — UNIQUE(post_id, user_id) |
| `notifications` | id, user_id (FK), type, message, is_read |

---

## Historias de Usuario implementadas

### HU1 — Registro de Usuario
- Campos requeridos: nombres, apellidos, teléfono, ubicación, contraseña.
- Validaciones: todos los campos obligatorios, teléfono numérico único, contraseña ≥ 6 caracteres.
- Contraseña almacenada como hash SHA-256 (nunca en texto plano).
- Mensaje de confirmación con ID asignado al registrarse.

### HU2 — Creación / Edición de Perfil
- Editar descripción, hobbies (separados por coma) y ruta de foto de perfil.
- Se valida que la ruta de foto exista en el sistema de archivos.
- Los cambios se persisten inmediatamente en la BD.

### HU3 — Conexión de Usuarios
- Búsqueda por nombre o hobby (búsqueda parcial, insensible a mayúsculas).
- Envío de solicitud de conexión con notificación automática al receptor.
- Aceptar / rechazar solicitudes pendientes.
- Al aceptar, el solicitante recibe una notificación de confirmación.

### HU4 — Feed de Actividades
- Muestra publicaciones recientes de las conexiones aceptadas, ordenadas por fecha.
- Interacciones disponibles: dar/quitar "me gusta" y comentar.
- Sección separada para ver las propias publicaciones.
- Creación de nuevas publicaciones desde el mismo menú.

### HU5 — Sugerencias de Conexión
- Analiza hobbies en común (intersección de listas) y misma ubicación.
- Ordena sugerencias por relevancia (más criterios = mayor prioridad).
- Excluye conexiones ya existentes, solicitudes enviadas y recibidas pendientes.
- Permite enviar solicitud directamente desde la lista de sugerencias.

---

## Requisitos

- Python **3.10** o superior (se usa `match`-compatible type hints como `X | Y`).
- Sin dependencias externas. Sólo librería estándar (`sqlite3`, `hashlib`, `os`, `sys`, `abc`, `dataclasses`).

---

## Ejecución

```bash
# Desde la carpeta del proyecto
cd "Taller 1 IA y DEVOPS"
python main.py
```

La primera ejecución crea automáticamente el archivo `red_social.db` en la misma carpeta.

---

## Flujo de uso sugerido

1. **Registrar** dos o más usuarios (opción 2 del menú inicial).
2. **Iniciar sesión** con uno de ellos (opción 1).
3. Ir a **Editar perfil** (opción 2) y agregar hobbies y ubicación.
4. Ir a **Conexiones → Buscar usuarios** (opción 3) y enviar una solicitud.
5. Cerrar sesión (opción 0) e iniciar con el otro usuario.
6. Ir a **Conexiones → Solicitudes pendientes** y aceptar la solicitud.
7. Crear publicaciones desde **Feed → Crear nueva publicación** (opción 4).
8. Volver al primer usuario y ver el **Feed** con las publicaciones de la conexión.
9. Explorar las **Sugerencias de conexión** (opción 5) para ver recomendaciones.
10. Revisar **Notificaciones** (opción 6) para ver todas las alertas del sistema.
