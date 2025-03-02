import sys
import os
from sqlalchemy import create_engine, MetaData, text

# Adiciona o diretório do config-manager ao sys.path
config_manager_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config-manager/src'))
sys.path.insert(0, config_manager_path)

DATABASE_URL = "postgresql://user:password@localhost:5432/config_manager"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

def recreate_tables():
    metadata.reflect(bind=engine)

    # Remove a coluna password se existir
    with engine.connect() as connection:
        connection.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS password;"))
        connection.commit()

    # Importando as classes do modelo
    from domain.users import User
    from domain.plans import Plan
    from domain.subscription import Subscription

    metadata.create_all(bind=engine)  # Cria todas as tabelas
    print("Tabelas recriadas com sucesso!")

if __name__ == "__main__":
    recreate_tables()
