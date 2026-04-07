"""
models.py – Modelos SQLAlchemy (tablas MySQL)
Parte A – Instrucción A2
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DECIMAL, DateTime,
    ForeignKey, CheckConstraint
)
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id     = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email  = Column(String(150), nullable=False, unique=True)


class Pedido(Base):
    __tablename__ = "pedidos"

    __table_args__ = (
        CheckConstraint("total >= 0", name="chk_total_positivo"),
    )

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id          = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    total               = Column(DECIMAL(10, 2), nullable=False)
    descuento_aplicado  = Column(DECIMAL(10, 2), nullable=False, default=0)
    fecha               = Column(DateTime, nullable=False, default=datetime.utcnow)


class Pago(Base):
    __tablename__ = "pagos"

    __table_args__ = (
        CheckConstraint("monto > 0", name="chk_monto_positivo"),
    )

    id         = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id  = Column(Integer, ForeignKey("pedidos.id", ondelete="RESTRICT"), nullable=False)
    monto      = Column(DECIMAL(10, 2))
    fecha_pago = Column(DateTime, nullable=False, default=datetime.utcnow)