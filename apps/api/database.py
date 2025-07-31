from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Debug: imprimir todas as variáveis de ambiente
print("=== DEBUG: Variáveis de ambiente ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT')}")
print("===================================")

# A URL de conexão com o banco de dados agora é lida diretamente da variável de ambiente,
# que é a forma padrão em ambientes de contêiner como o Docker.
# Isso evita conflitos com arquivos .env locais.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não está definida.")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 