from sqlalchemy import create_engine
import sys
import os
import logging

# Adiciona o diretório do projeto ao PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Importa os modelos
from src.domain.users import User
from src.domain.plans import Plan
from src.domain.subscription import Subscription
from src.domain.integration import Integration

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/config_manager")
logging.basicConfig(level=logging.INFO)
logging.info(f"Conectando ao banco de dados: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    logging.error(f"Erro ao conectar ao banco de dados: {e}")
    sys.exit(1)


def create_tables():
    # Cria todas as tabelas
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Tabelas criadas com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao criar tabelas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
