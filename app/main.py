from fastapi import FastAPI
from api import rcs_handler
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API RCS de Prueba",
    description="Una API de ejemplo con FastAPI y Swagger UI.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["https://tu-dominio.com"]
    allow_credentials=True,
    allow_methods=["*"],  # incluye OPTIONS, POST, etc.
    allow_headers=["*"],
)

app.include_router(rcs_handler.router)
