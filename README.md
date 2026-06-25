# device_systems API – v5.0.0
### EV11: Seguridad – Autenticación, Middleware, CORS, Rate Limiting y Validación Avanzada

> **Programa:** Tecnólogo en Análisis y Desarrollo de Software – SENA  
> **Ficha:** 3114227 | **Autor:** Kevin Andrés Zapata Murillo
>**Instructor:** Carlos Navia 

---

## ¿Qué hace esta API?

`device_systems` es una API REST para gestionar **usuarios**, **dispositivos tecnológicos** y **préstamos**. En esta versión (EV11) se añadió una capa completa de seguridad:

| Capacidad | Tecnología |
|---|---|
| Hash de contraseñas | `passlib[bcrypt]` |
| Tokens JWT | `python-jose` |
| Autenticación OAuth2 | FastAPI OAuth2PasswordBearer |
| Autorización por roles | Dependencias con `Depends()` |
| Middleware personalizado | `BaseHTTPMiddleware` |
| CORS | `CORSMiddleware` |
| Rate Limiting | `slowapi` |
| Validaciones avanzadas | `Pydantic v2` (`field_validator`, `ConfigDict`) |

---

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── auth/
│   │   ├── auth_routes.py      # POST /auth/register, /auth/login, GET /auth/me
│   │   ├── auth_service.py     # Lógica de registro y login
│   │   └── security.py         # bcrypt hash + JWT encode/decode
│   ├── database/
│   │   └── connection.py       # Engine, SessionLocal, Base
│   ├── dependencies/
│   │   ├── auth_dependency.py  # get_current_user, require_admin, require_admin_or_support
│   │   └── database_dependency.py
│   ├── middlewares/
│   │   └── request_middleware.py  # X-Process-Time, X-App-Name, X-Request-ID, logs
│   ├── models/
│   │   ├── user_model.py       # User (con hashed_password)
│   │   ├── device_model.py     # Device
│   │   └── loan_model.py       # Loan (FK a users y devices)
│   ├── routes/
│   │   ├── user_routes.py      # CRUD /users (protegido)
│   │   ├── device_routes.py    # CRUD /devices (protegido)
│   │   └── loan_routes.py      # Gestión /loans (protegido)
│   ├── schemas/
│   │   ├── auth_schema.py      # UserRegister, UserLogin, Token, UserPublicResponse
│   │   ├── user_schema.py      # UserUpdate, UserPatch, UserResponse
│   │   ├── device_schema.py    # DeviceCreate, DeviceResponse…
│   │   └── loan_schema.py      # LoanCreate, LoanDetailResponse…
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   └── main.py                 # FastAPI app: CORS, middleware, rate limiter, routers
├── main.py                     # Punto de entrada (uvicorn main:app)
├── .env                        # Variables de entorno (NO subir a GitHub)
├── .env.example                # Plantilla pública de variables
├── .gitignore
└── requirements.txt
```

---

## Instalación y ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/KevinZapata77/python_ev11
cd device_systems
```

### 2. Crear y activar entorno virtual
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Ejecutar el servidor
```bash
uvicorn main:app --reload
```

Abre en el navegador: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Tabla de endpoints

| Método | Ruta | Descripción | Protección |
|--------|------|-------------|-----------|
| POST | `/auth/register` | Registrar nuevo usuario | Público |
| POST | `/auth/login` | Login → retorna JWT | Público |
| GET | `/auth/me` | Datos del usuario autenticado | 🔒 Autenticado |
| GET | `/users/` | Listar usuarios | 🔒 Autenticado |
| GET | `/users/{id}` | Usuario por ID | 🔒 Autenticado |
| PUT | `/users/{id}` | Actualizar usuario completo | 🔒 Admin |
| PATCH | `/users/{id}` | Actualizar usuario parcial | 🔒 Admin |
| DELETE | `/users/{id}` | Eliminar usuario | 🔒 Admin |
| GET | `/devices/` | Listar dispositivos | Público |
| GET | `/devices/{id}` | Dispositivo por ID | Público |
| POST | `/devices/` | Crear dispositivo | 🔒 Admin/Support |
| PUT | `/devices/{id}` | Actualizar dispositivo | 🔒 Admin/Support |
| PATCH | `/devices/{id}` | Actualizar parcial | 🔒 Admin/Support |
| DELETE | `/devices/{id}` | Eliminar dispositivo | 🔒 Admin |
| GET | `/loans/` | Listar préstamos | 🔒 Admin/Support |
| GET | `/loans/details` | Préstamos con detalle | 🔒 Admin/Support |
| GET | `/loans/{id}` | Préstamo por ID | 🔒 Admin/Support |
| POST | `/loans/` | Crear préstamo | 🔒 Autenticado |
| PATCH | `/loans/{id}/return` | Devolver dispositivo | 🔒 Admin/Support |

---

## Flujo de autenticación

```
1. POST /auth/register   →  { name, email, password, role }
2. POST /auth/login      →  { access_token, token_type: "bearer" }
3. Swagger: botón Authorize → pegar el token
4. GET /auth/me          →  { id, name, email, role, is_active }
```

**Ejemplo de registro:**
```json
POST /auth/register
{
  "name": "Ana Pérez",
  "email": "ana@sena.edu.co",
  "password": "MiClave123",
  "role": "admin"
}
```

**Ejemplo de login:**
```json
POST /auth/login
username: ana@sena.edu.co
password: MiClave123

Respuesta:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Validaciones de contraseña (Pydantic v2)

El schema `UserRegister` usa `@field_validator` para validar que la contraseña cumpla:

- ✅ Mínimo 8 caracteres  
- ✅ Al menos una mayúscula  
- ✅ Al menos una minúscula  
- ✅ Al menos un número  
- ✅ Sin espacios en blanco  

Si no cumple, la API retorna `422 Unprocessable Entity` con el detalle del error.

---

## Cabeceras del middleware

Cada respuesta incluye automáticamente:

```
X-App-Name: device_systems
X-Process-Time: 0.0031
X-Request-ID: 8f42e9c1
```

El middleware también registra en consola:
```
2026-06-24 10:00:00 | INFO | [8f42e9c1] POST /auth/login → 200 (0.0031s)
```

---

## CORS

Configurado en `main.py` para desarrollo local:

```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

> ⚠️ **Por qué no usar `"*"` en producción con credentials=True:**  
> Cuando `allow_credentials=True`, el navegador exige un origen específico (no `"*"`).  
> Además, permitir todos los orígenes en producción expone la API a ataques CSRF.

---

## Rate Limiting

Límites configurados con `slowapi`:

| Endpoint | Límite |
|---|---|
| `POST /auth/login` | 5 req/minuto |
| `POST /auth/register` | 3 req/minuto |
| `GET /users/` | 30 req/minuto |
| `POST /loans/` | 10 req/minuto |

Cuando se supera el límite, la API responde: `429 Too Many Requests`

---

## Códigos de estado HTTP

| Caso | Código |
|---|---|
| Recurso creado | `201 Created` |
| Operación exitosa | `200 OK` |
| Eliminación exitosa | `204 No Content` |
| No autenticado / token inválido | `401 Unauthorized` |
| Sin permisos de rol | `403 Forbidden` |
| Recurso no encontrado | `404 Not Found` |
| Dato duplicado / regla de negocio | `400 Bad Request` |
| Demasiadas peticiones | `429 Too Many Requests` |
| Error de validación Pydantic | `422 Unprocessable Entity` |

---

## Cómo se aplicó Dependency Injection

Las dependencias de autenticación se definen en `auth_dependency.py` y se inyectan con `Depends()`:

```python
# Solo admin puede eliminar dispositivos
@router.delete("/{device_id}")
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),   # ← inyección de dependencia de rol
):
    ...
```

Cadena de dependencias:
```
require_admin
  └── get_current_active_user
        └── get_current_user
              └── oauth2_scheme (extrae token del header)
                    └── decode_access_token (valida JWT)
                          └── busca User en DB
```

---

## Reflexión final

Esta actividad me permitió comprender que la seguridad en una API REST no es opcional. Aprendí que:

- Las contraseñas **nunca** deben guardarse en texto plano; bcrypt las protege incluso si la base de datos es comprometida.
- Los tokens JWT permiten autenticación **sin estado** (stateless), lo que facilita escalar la aplicación.
- La autorización por roles con `Depends()` mantiene el código limpio y reutilizable.
- El middleware centraliza la trazabilidad sin tocar cada endpoint individualmente.
- Rate limiting es la primera línea de defensa contra ataques de fuerza bruta.
- CORS mal configurado puede exponer la API a ataques desde dominios maliciosos.

---

