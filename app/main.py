"""
main.py
-------
Aplicación FastAPI v5.0.0 - device_systems
EV11: Seguridad con JWT, CORS, Middleware y Rate Limiting
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database.connection import engine, Base
from app.models import user_model, device_model, loan_model  # noqa: F401 – registra tablas
from app.auth.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.middlewares.request_middleware import RequestLoggingMiddleware

# ─── Crear tablas al iniciar (sin Alembic en dev rápido) ─────────────────────
Base.metadata.create_all(bind=engine)

# ─── Rate Limiter global ──────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ─── Metadatos OpenAPI ────────────────────────────────────────────────────────
tags_metadata = [
    {"name": "Auth",    "description": "Registro, login y perfil del usuario autenticado."},
    {"name": "Users",   "description": "CRUD de usuarios (protegido por JWT)."},
    {"name": "Devices", "description": "CRUD de dispositivos (admin/support)."},
    {"name": "Loans",   "description": "Gestión de préstamos con validaciones de negocio."},
    {"name": "Security","description": "Información sobre seguridad de la API."},
]

# ─── Instancia FastAPI ────────────────────────────────────────────────────────
app = FastAPI(
    title="device_systems API",
    description=(
        "API REST **segura** para gestión de usuarios, dispositivos y préstamos.\n\n"
        "## Seguridad\n"
        "- Autenticación con **OAuth2 + JWT** (Bearer token).\n"
        "- Contraseñas hasheadas con **bcrypt** (passlib).\n"
        "- Autorización por **roles**: `admin`, `support`, `user`.\n"
        "- **Rate limiting** para prevenir abuso.\n"
        "- **CORS** configurado para clientes frontend locales.\n"
        "- **Middleware** con trazabilidad por X-Request-ID.\n\n"
        "## Flujo de uso\n"
        "1. `POST /auth/register` → crear cuenta.\n"
        "2. `POST /auth/login` → obtener token JWT.\n"
        "3. Usar el token en el botón **Authorize** de Swagger.\n"
        "4. Acceder a rutas protegidas.\n"
    ),
    version="5.0.0",
    contact={"name": "Kevin Andrés Zapata Murillo", "email": "kevin.zapata@sena.edu.co"},
    license_info={"name": "SENA – Ficha 3114227"},
    openapi_tags=tags_metadata,
)

# ─── Rate Limiter ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# NOTA: En producción, reemplaza "*" por dominios específicos cuando uses credentials=True.
# Aquí permitimos localhost para desarrollo local.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite (React/Vue)
        "http://localhost:3000",   # Next.js / CRA
        "http://localhost:8080",   # Otros
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Middleware personalizado ─────────────────────────────────────────────────
app.add_middleware(RequestLoggingMiddleware)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)


# ─── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Security"], summary="Bienvenida y estado de la API")
def root():
    return {
        "message": "device_systems API v5.0.0 – Seguridad activada",
        "auth": "POST /auth/register | POST /auth/login | GET /auth/me",
        "docs": "/docs",
        "redoc": "/redoc",
        "nota": "Usa el token JWT en el botón Authorize de Swagger para probar rutas protegidas.",
    }
