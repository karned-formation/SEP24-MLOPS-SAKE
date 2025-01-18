FROM python:3.11
# la version "python:3.11-slim" provoque un probleme car "private_conn_dagshub.sh" s'appuie sur des fonctions non présentes dans ce docker

ARG COMMON_DIR
ARG SOURCE_DIR
ARG DOCKERFILE_DIR
ARG DAGSHUB_ACCESS_KEY_ID


ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=80
ENV WORKERS=1

EXPOSE ${PORT}
WORKDIR ${APP_HOME}

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN git clone https://github.com/karned-formation/SEP24-MLOPS-SAKE.git 
WORKDIR ${APP_HOME}/SEP24-MLOPS-SAKE
# remove the following line when merging with main
RUN git switch admin_front
RUN git pull

RUN pip install --no-cache-dir -r requirements.txt

COPY ${DOCKERFILE_DIR}/private_conn_dagshub.sh ./
RUN chmod +x private_conn_dagshub.sh

CMD dvc remote modify origin --local access_key_id ${DAGSHUB_ACCESS_KEY_ID} && dvc remote modify origin --local secret_access_key ${DAGSHUB_ACCESS_KEY_ID} && dvc pull --force && cd ${APP_HOME}/SEP24-MLOPS-SAKE && exec uvicorn app:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS}