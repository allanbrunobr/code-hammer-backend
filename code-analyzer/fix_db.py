#!/usr/bin/env python3
import os
import glob
import re

# Procurar arquivos Python
py_files = glob.glob("/srv/**/*.py", recursive=True)

# Obter string de conexão do Cloud SQL
cloud_sql_instance = os.environ.get("DB_HOST", "")

for file_path in py_files:
    try:
        with open(file_path, "r") as f:
            content = f.read()
        
        # Substituir localhost ou 127.0.0.1 pelo socket Unix
        modified = re.sub(r"postgresql://([^@]*)@(localhost|127.0.0.1)([^\'\"]*)", 
                       f"postgresql://\\1@/\\3?host={cloud_sql_instance}", content)
        modified = re.sub(r"\'(localhost|127.0.0.1)\'", f"'{cloud_sql_instance}'", modified)
        
        if modified != content:
            print(f"Corrigindo conexão de BD em: {file_path}")
            with open(file_path, "w") as f:
                f.write(modified)
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")

print("Correção de conexões de banco de dados concluída")