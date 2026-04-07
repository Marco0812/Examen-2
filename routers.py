"""
routers.py – Endpoints REST agrupados por tema
"""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

import models, schemas
from database import get_db, get_mongo_db

# Router: Usuarios (auxiliar / seed)
router_usuarios = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router_usuarios.post("/", response_model=schemas.UsuarioOut, status_code=201,
                      summary="Crear usuario")
def crear_usuario(data: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar email único antes de insertar
    existe = db.query(models.Usuario).filter(models.Usuario.email == data.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    usuario = models.Usuario(nombre=data.nombre, email=data.email)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router_usuarios.get("/", response_model=List[schemas.UsuarioOut],
                     summary="Listar usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()


# Router: Pedidos – Parte B
router_pedidos = APIRouter(prefix="/pedidos", tags=["Pedidos"])

DESCUENTO_PORCENTAJE = 0.10   # 10 %
UMBRAL_DESCUENTO     = 1000   # aplica si total > 1000


@router_pedidos.post("/", response_model=schemas.PedidoConPago, status_code=201,
                     summary="Crear pedido (con transacción)")
def crear_pedido(data: schemas.PedidoCreate, db: Session = Depends(get_db)):
    """
    Parte B – Instrucción B1
    - Calcula 10 % de descuento si total > 1000.
    - Inserta pedido + pago dentro de una transacción explícita.
    - Si ocurre cualquier error hace ROLLBACK (no queda ningún registro).
    """
    # Verificar que el usuario existe
    usuario = db.query(models.Usuario).filter(models.Usuario.id == data.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario {data.usuario_id} no encontrado.")

    # Calcular descuento
    descuento = round(data.total * DESCUENTO_PORCENTAJE, 2) if data.total > UMBRAL_DESCUENTO else 0.0
    monto_pago = round(data.total - descuento, 2)

    # TRANSACCIÓN EXPLÍCITA 
    try:
        db.execute(text("START TRANSACTION"))

        pedido = models.Pedido(
            usuario_id         = data.usuario_id,
            total              = data.total,
            descuento_aplicado = descuento,
            fecha              = datetime.utcnow(),
        )
        db.add(pedido)
        db.flush()   # obtener pedido.id sin hacer commit

        pago = models.Pago(
            pedido_id  = pedido.id,
            monto      = monto_pago,
            fecha_pago = datetime.utcnow(),
        )
        db.add(pago)
        db.commit()
        db.refresh(pedido)

    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la transacción: {str(exc)}")

    return schemas.PedidoConPago(
        pedido       = pedido,
        monto_pagado = float(monto_pago),
    )


@router_pedidos.get("/", response_model=List[schemas.PedidoOut],
                    summary="Listar pedidos")
def listar_pedidos(db: Session = Depends(get_db)):
    return db.query(models.Pedido).all()


# Router: Eventos MongoDB – Parte C
router_eventos = APIRouter(prefix="/eventos", tags=["Eventos (MongoDB)"])


@router_eventos.post("/", status_code=201, summary="Registrar evento de usuario")
def crear_evento(data: schemas.EventoCreate):
    """
    Parte C – Instrucción C1
    Inserta un documento en la colección eventos_usuario (MongoDB).
    """
    db = get_mongo_db()
    doc = {
        "usuario_id":  data.usuario_id,
        "evento":      data.evento,
        "fecha":       data.fecha,          # pymongo almacena datetime como ISODate
        "dispositivo": data.dispositivo,
    }
    if data.producto_id is not None:
        doc["producto_id"] = data.producto_id

    result = db["eventos_usuario"].insert_one(doc)
    return {"mensaje": "Evento registrado", "id": str(result.inserted_id)}


@router_eventos.get("/analisis", summary="Análisis de eventos (agregación)")
def analisis_eventos():
    """
    Parte C – Instrucción C2
    1. Evento más frecuente
    2. Total de eventos registrados
    """
    db = get_mongo_db()
    col = db["eventos_usuario"]

    # Pipeline: agrupar por evento, ordenar desc y tomar el primero
    pipeline = [
        {"$group": {"_id": "$evento", "count": {"$sum": 1}}},
        {"$sort":  {"count": -1}},
        {"$limit": 1},
    ]
    resultado = list(col.aggregate(pipeline))
    evento_frecuente = resultado[0]["_id"] if resultado else None

    total_eventos = col.count_documents({})

    return {
        "evento_mas_frecuente": evento_frecuente,
        "total_eventos": total_eventos,
    }


# Router: Dashboard integrado – Parte D
router_dashboard = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router_dashboard.get("/resumen", response_model=schemas.DashboardResumen,
                      summary="Resumen analítico integrado MySQL + MongoDB")
def dashboard_resumen(db: Session = Depends(get_db)):
    """
    Parte D – Instrucción D1
    Combina métricas de MySQL y MongoDB en un solo endpoint.
    """
    # ── MySQL: total ventas y promedio descuento ──
    fila = db.execute(
        text("SELECT COALESCE(SUM(total), 0), COALESCE(AVG(descuento_aplicado), 0) FROM pedidos")
    ).fetchone()
    total_ventas       = float(fila[0])
    promedio_descuento = round(float(fila[1]), 2)

    # ── MongoDB: evento más frecuente y total ──
    mongo = get_mongo_db()
    col   = mongo["eventos_usuario"]

    pipeline = [
        {"$group": {"_id": "$evento", "count": {"$sum": 1}}},
        {"$sort":  {"count": -1}},
        {"$limit": 1},
    ]
    resultado = list(col.aggregate(pipeline))
    evento_frecuente = resultado[0]["_id"] if resultado else None
    total_eventos    = col.count_documents({})

    return schemas.DashboardResumen(
        ventas  = schemas.VentasResumen(
            total_ventas       = total_ventas,
            promedio_descuento = promedio_descuento,
        ),
        eventos = schemas.EventosResumen(
            evento_mas_frecuente = evento_frecuente,
            total_eventos        = total_eventos,
        ),
    )