"""
request_middleware.py
---------------------
Middleware personalizado que:
- Mide el tiempo de respuesta.
- Agrega cabeceras X-Process-Time, X-App-Name y X-Request-ID.
- Registra en consola: método, ruta, código de estado y tiempo.
"""
import time
import uuid
import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("device_systems")
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generar o propagar un ID único por petición
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        # Agregar cabeceras personalizadas
        response.headers["X-App-Name"] = "device_systems"
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-Request-ID"] = request_id

        # Log en consola
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"→ {response.status_code} ({process_time:.4f}s)"
        )

        return response
