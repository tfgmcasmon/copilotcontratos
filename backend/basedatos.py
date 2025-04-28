from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de la base de datos (aquí estamos usando SQLite en local)
DATABASE_URL = "sqlite:///./legaltask.db"  # Este archivo .db se crea automáticamente

# Crear el motor de conexión
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # Solo necesario para SQLite
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base de datos base
Base = declarative_base()
