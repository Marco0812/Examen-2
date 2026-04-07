"""
main.py – Punto de entrada de la aplicación FastAPI
Parte A – Instrucción A1
"""
from fastapi import FastAPI
from database import Base, engine
from routers import router_usuarios, router_pedidos, router_eventos, router_dashboard

# Crear tablas MySQL al arrancar (si no existen)
Base.metadata.create_all(bind=engine)

# Aplicación
app = FastAPI(
    title       = "E-Commerce API",
    description = (
        "Backend RESTful con FastAPI, MySQL y MongoDB.\n\n"
        "**Parcial 2 – Administración de Bases de Datos**\n\n"
        "Cubre: modelo relacional, transacciones, NoSQL y endpoint analítico integrado."
    ),
    version     = "1.0.0",
    docs_url    = "/docs",          # Swagger UI disponible en /docs
    redoc_url   = "/redoc",
)

# Registrar routers 
app.include_router(router_usuarios)
app.include_router(router_pedidos)
app.include_router(router_eventos)
app.include_router(router_dashboard)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "mensaje": "API E-Commerce funcionando correctamente."}