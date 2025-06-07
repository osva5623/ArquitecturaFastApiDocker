from fastapi import FastAPI
from api import rcs_handler

app = FastAPI(
    title="API RCS de Prueba",
    description="Una API de ejemplo con FastAPI y Swagger UI.",
    version="1.0.0"
)

app.include_router(rcs_handler.router)

