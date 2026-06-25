"""
Punto de entrada raíz para ejecutar la aplicación:
    uvicorn main:app --reload
"""
from app.main import app  # noqa: F401 – re-exporta la instancia FastAPI
