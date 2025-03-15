FROM python:3.10

WORKDIR /srv

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Copiar scripts auxiliares
COPY fix_db.py /srv/fix_db.py
COPY start.sh /srv/start.sh
RUN chmod +x /srv/fix_db.py /srv/start.sh

# Definir variáveis de ambiente
ENV APPLICATION_ORIGINS=*
ENV APPLICATION_API_KEYS=minhachavedeautenticacao
ENV SQLALCHEMY_DATABASE_URI=postgresql://postgres:M3t4tr0n@/config_manager?host=/cloudsql/arcane-text-377602:us-central1:postgres-instance
ENV DATABASE_URL=postgresql://postgres:M3t4tr0n@/config_manager?host=/cloudsql/arcane-text-377602:us-central1:postgres-instance
ENV DB_USER=postgres
ENV DB_PASSWORD=M3t4tr0n
ENV DB_NAME=config_manager
ENV DB_PORT=5432
ENV PYTHONPATH=/srv

EXPOSE 8083
CMD ["/srv/start.sh"]