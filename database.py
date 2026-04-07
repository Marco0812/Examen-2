import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


# MySQL / SQLAlchemy
MYSQL_HOST     = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT     = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER     = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "AOKKuAH6rXbsBdxs")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ecommerce_db")

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,          # verifica conexión antes de usarla
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency: sesión de base de datos MySQL."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# MongoDB / PyMongo
MONGO_URI      = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "ecommerce_logs")

mongo_client = MongoClient(MONGO_URI)
mongo_db     = mongo_client[MONGO_DATABASE]


def get_mongo_db():
    """Retorna la base de datos MongoDB."""
    return mongo_db