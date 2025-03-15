#!/bin/bash

# Definir variáveis baseadas nos valores ambientais
export DB_HOST=${DB_HOST}

# Executar script de correção das strings de conexão
python /srv/fix_db.py

# Iniciar a aplicação
exec uvicorn src.main:app --host 0.0.0.0 --port 8080