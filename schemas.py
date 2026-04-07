"""
schemas.py – Esquemas Pydantic para validación de entrada/salida
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field


# ─────────────────────────────────────────────
# Usuarios
# ─────────────────────────────────────────────
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    email:  str = Field(..., max_length=150)


class UsuarioOut(UsuarioCreate):
    id: int

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Pedidos  (Parte B)
# ─────────────────────────────────────────────
class PedidoCreate(BaseModel):
    usuario_id: int = Field(..., gt=0, description="ID del usuario que realiza el pedido")
    total:      float = Field(..., ge=0, description="Total del pedido antes de descuento")


class PedidoOut(BaseModel):
    id:                 int
    usuario_id:         int
    total:              float
    descuento_aplicado: float
    fecha:              datetime

    class Config:
        from_attributes = True


class PedidoConPago(BaseModel):
    pedido:  PedidoOut
    monto_pagado: float


# ─────────────────────────────────────────────
# Eventos MongoDB  (Parte C)
# ─────────────────────────────────────────────
class EventoCreate(BaseModel):
    usuario_id:  int       = Field(..., description="ID del usuario")
    evento:      str       = Field(..., description="Nombre del evento")
    fecha:       datetime  = Field(..., description="Fecha ISO del evento")
    dispositivo: Literal["web", "mobile"] = Field(..., description="Dispositivo: web o mobile")
    producto_id: Optional[int] = Field(None, description="ID del producto (opcional)")


class EventoOut(EventoCreate):
    id: str  # _id de MongoDB convertido a string


# ─────────────────────────────────────────────
# Dashboard  (Parte D)
# ─────────────────────────────────────────────
class VentasResumen(BaseModel):
    total_ventas:        float
    promedio_descuento:  float


class EventosResumen(BaseModel):
    evento_mas_frecuente: Optional[str]
    total_eventos:        int


class DashboardResumen(BaseModel):
    ventas:   VentasResumen
    eventos:  EventosResumen