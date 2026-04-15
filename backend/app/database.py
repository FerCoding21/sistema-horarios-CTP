from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Motor de conexión a PostgreSQL
engine = create_engine(settings.database_url)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Clase base para los modelos
Base = declarative_base()

# Dependencia reutilizable en todos los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()