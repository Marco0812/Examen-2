"""
mongo_setup.py – Crea la colección eventos_usuario con validación de esquema
Ejecutar una sola vez: python mongo_setup.py
"""
from database import get_mongo_db

def setup_mongo_collection():
    db = get_mongo_db()
    collection_name = "eventos_usuario"

    # Eliminar colección existente para recrearla con validador
    if collection_name in db.list_collection_names():
        db[collection_name].drop()
        print(f"Colección '{collection_name}' eliminada.")

    # Crear colección con validación de esquema JSON Schema
    db.create_collection(
        collection_name,
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["usuario_id", "evento", "fecha", "dispositivo"],
                "properties": {
                    "usuario_id": {
                        "bsonType": "int",
                        "description": "Debe ser un entero y es requerido"
                    },
                    "evento": {
                        "bsonType": "string",
                        "description": "Debe ser un string y es requerido"
                    },
                    "fecha": {
                        "bsonType": "date",
                        "description": "Debe ser una fecha ISODate y es requerida"
                    },
                    "dispositivo": {
                        "bsonType": "string",
                        "enum": ["web", "mobile"],
                        "description": "Solo permite 'web' o 'mobile'"
                    },
                    "producto_id": {
                        "bsonType": ["int", "null"],
                        "description": "Entero opcional"
                    }
                }
            }
        },
        validationLevel="strict",
        validationAction="error"
    )

    # Índice para mejorar búsquedas por usuario y evento
    db[collection_name].create_index([("usuario_id", 1)])
    db[collection_name].create_index([("evento", 1)])

    print(f"Colección '{collection_name}' creada con validación de esquema.")


if __name__ == "__main__":
    setup_mongo_collection()