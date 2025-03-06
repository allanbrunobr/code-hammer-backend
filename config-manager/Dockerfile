FROM python:3.10

RUN apt-get update && apt-get install -y wget
RUN wget -O /usr/local/bin/wait-for-it https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it

WORKDIR /srv

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .


# Definir argumentos de build
ARG APPLICATION_URL=http://localhost:5000/
ARG APPLICATION_ORIGINS=*
ARG APPLICATION_API_KEYS=/path/to/application_default_credentials.json
ARG DB_USER=postgres
ARG DB_PASSWORD=@M3t4tr0n@
ARG DB_NAME=postgres
ARG DB_HOST=db.rwptfpwqnjaghvkzjukx.supabase.co
ARG DB_PORT=5432
ARG GOOGLE_API_KEY=AIzaSyAu4BEFz_G_e8DLWKizgsT_d6nqF9LWZ3g
ARG GOOGLE_AI_MODEL_NAME=gemini-1.5-flash
ARG GOOGLE_PROJECT=arcane-text-377602
ARG GOOGLE_LOCATION=us-central1
ARG GOOGLE_AI_EMBEDDINGS_MODEL_NAME=textembedding-gecko@003
ARG SECRET_KEY=mysecretkey
ARG ALGORITHM=HS256
ARG ACCESS_TOKEN_EXPIRE_MINUTES=30
ARG PROJECT_ID=arcane-text-377602
ARG TOPIC_ID=code-to-analyze
ARG SUBSCRIPTION_ID=code-to-analyze-sub

# Transferir os valores de ARG para ENV (para tempo de execução)
ENV APPLICATION_URL=${APPLICATION_URL}
ENV APPLICATION_ORIGINS=${APPLICATION_ORIGINS}
ENV APPLICATION_API_KEYS=${APPLICATION_API_KEYS}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_NAME=${DB_NAME}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}
ENV GOOGLE_AI_MODEL_NAME=${GOOGLE_AI_MODEL_NAME}
ENV GOOGLE_PROJECT=${GOOGLE_PROJECT}
ENV GOOGLE_LOCATION=${GOOGLE_LOCATION}
ENV GOOGLE_AI_EMBEDDINGS_MODEL_NAME=${GOOGLE_AI_EMBEDDINGS_MODEL_NAME}
ENV SECRET_KEY=${SECRET_KEY}
ENV ALGORITHM=${ALGORITHM}
ENV ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
ENV PROJECT_ID=${PROJECT_ID}
ENV TOPIC_ID=${TOPIC_ID}
ENV SUBSCRIPTION_ID=${SUBSCRIPTION_ID}


ENV PYTHONPATH=/srv

EXPOSE 8082
CMD ["/usr/local/bin/wait-for-it", "postgres:5432", "--", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8082"]
