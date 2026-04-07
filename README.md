Backend RESTful con **FastAPI**, **MySQL** y **MongoDB**.

---

## Estructura del proyecto

```
ecommerce_api/
├── main.py          # Punto de entrada FastAPI
├── database.py      # Conexiones MySQL (SQLAlchemy) y MongoDB (PyMongo)
├── models.py        # Modelos ORM SQLAlchemy (tablas MySQL)
├── schemas.py       # Esquemas Pydantic (validación entrada/salida)
├── routers.py       # Endpoints agrupados por tema
├── mongo_setup.py   # Script de inicialización de colección MongoDB
├── init_db.sql      # DDL manual + procedimiento almacenado MySQL
├── requirements.txt
└── .env.example
```

---

## Instalación y configuración

### 1. Clonar / descomprimir el proyecto
```bash
cd ecommerce_api
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales de MySQL y MongoDB
```

### 4. Crear base de datos MySQL
Opción A – automática al levantar la API (SQLAlchemy crea las tablas):
> Solo funciona si la base de datos `ecommerce_db` ya existe en el servidor.

```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Opción B – ejecutar el script completo (incluye procedimiento almacenado):
```bash
mysql -u root -p < init_db.sql
```

### 5. Inicializar colección MongoDB con validación
```bash
python mongo_setup.py
```

### 6. Levantar el servidor
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI disponible en: **http://localhost:8000/docs**

---

## Endpoints

### Usuarios
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/usuarios/` | Crear usuario |
| GET  | `/usuarios/` | Listar usuarios |

### Pedidos (con transacción – Parte B)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/pedidos/` | Crear pedido + pago (transacción explícita) |
| GET  | `/pedidos/` | Listar pedidos |

### Eventos MongoDB (Parte C)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/eventos/` | Registrar evento de usuario |
| GET  | `/eventos/analisis` | Evento más frecuente y total |

### Dashboard (Parte D)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/dashboard/resumen` | Resumen integrado MySQL + MongoDB |

---

## Pruebas documentadas

### A1 – Crear usuario
```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Ana López", "email": "ana@mail.com"}'
```
**Respuesta esperada:**
```json
{"id": 1, "nombre": "Ana López", "email": "ana@mail.com"}
```

---

### B1 – Crear pedido (total > 1000, aplica descuento)
```bash
curl -X POST http://localhost:8000/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 1, "total": 2000}'
```
**Respuesta esperada:**
```json
{
  "pedido": {
    "id": 1,
    "usuario_id": 1,
    "total": 2000.0,
    "descuento_aplicado": 200.0,
    "fecha": "2024-06-01T10:00:00"
  },
  "monto_pagado": 1800.0
}
```

---

### B1 – Crear pedido (total ≤ 1000, sin descuento)
```bash
curl -X POST http://localhost:8000/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 1, "total": 500}'
```
**Respuesta esperada:**
```json
{
  "pedido": {"id": 2, "total": 500.0, "descuento_aplicado": 0.0, ...},
  "monto_pagado": 500.0
}
```

---

### C1 – Registrar evento MongoDB
```bash
curl -X POST http://localhost:8000/eventos/ \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 1,
    "evento": "click_producto",
    "fecha": "2024-06-01T10:05:00",
    "dispositivo": "web",
    "producto_id": 42
  }'
```
**Respuesta esperada:**
```json
{"mensaje": "Evento registrado", "id": "665f3a..."}
```

---

### C2 – Análisis de eventos
```bash
curl http://localhost:8000/eventos/analisis
```
**Respuesta esperada:**
```json
{
  "evento_mas_frecuente": "click_producto",
  "total_eventos": 5
}
```

---

### D1 – Dashboard resumen
```bash
curl http://localhost:8000/dashboard/resumen
```
**Respuesta esperada:**
```json
{
  "ventas": {
    "total_ventas": 2500.0,
    "promedio_descuento": 100.0
  },
  "eventos": {
    "evento_mas_frecuente": "click_producto",
    "total_eventos": 5
  }
}
```

---

## Lógica de negocio – Transacción (Parte B)

La transacción en `POST /pedidos/` sigue este flujo:

```
START TRANSACTION
  ├─ INSERT INTO pedidos (usuario_id, total, descuento, fecha)
  ├─ FLUSH  →  obtiene pedido.id
  ├─ INSERT INTO pagos (pedido_id, monto, fecha_pago)
  └─ COMMIT
       ↓ si cualquier paso falla → ROLLBACK (no queda ningún registro)
```

El descuento se calcula como:
- `total > 1000` → `descuento = total × 10 %`
- `total ≤ 1000` → `descuento = 0`

---

## Modelo MongoDB – Validación de esquema (Parte C)

La colección `eventos_usuario` tiene un validador JSON Schema:

| Campo | Tipo | Restricción |
|-------|------|-------------|
| `usuario_id` | int | Requerido |
| `evento` | string | Requerido |
| `fecha` | date (ISODate) | Requerido |
| `dispositivo` | string | Requerido, enum: `["web", "mobile"]` |
| `producto_id` | int | Opcional |

---

## Criterios de evaluación cubiertos

| Componente | Implementación |
|------------|---------------|
| Diseño modelo relacional (25%) | `models.py` + `init_db.sql` con PK, FK, UNIQUE, CHECK, NOT NULL |
| Transacciones y lógica de negocio (30%) | `routers.py` → `crear_pedido()` con START TRANSACTION / COMMIT / ROLLBACK |
| MongoDB y análisis (20%) | `mongo_setup.py` (validación JSON Schema) + endpoint `/eventos/analisis` con `$group`, `$sort`, `$limit` |
| Endpoint integrado y arquitectura (25%) | `GET /dashboard/resumen` integra MySQL + MongoDB |