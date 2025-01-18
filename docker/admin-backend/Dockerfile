FROM python:3.11
# la version "python:3.11-slim" provoque un probleme car "private_conn_dagshub.sh" s'appuie sur des fonctions non présentes dans ce docker

ARG COMMON_DIR
ARG SOURCE_DIR
ARG DOCKERFILE_DIR
ARG STREAMLIT_DIR
ARG DAGSHUB_ACCESS_KEY_ID


ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=80
ENV WORKERS=1
ENV STREAMLIT_DIR ${STREAMLIT_DIR}

EXPOSE ${PORT}
WORKDIR ${APP_HOME}

RUN git clone https://github.com/karned-formation/SEP24-MLOPS-SAKE.git 
WORKDIR ${APP_HOME}/SEP24-MLOPS-SAKE
# remove the following line when merging with main
RUN git switch admin_front
RUN git pull

#  installs everything needed, then removes Rust and curl after DVC is installed to keep the final image smaller
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    export PATH="/root/.cargo/bin:${PATH}" && \
    python3 -m venv .venv && \
    . .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt 


COPY ${DOCKERFILE_DIR}/private_conn_dagshub.sh ./
RUN chmod +x private_conn_dagshub.sh
RUN ./private_conn_dagshub.sh

RUN rustup self uninstall -y && \ 
apt-get remove -y curl && \
apt-get autoremove -y && \
rm -rf /var/lib/apt/lists/*


CMD dvc remote modify origin --local access_key_id ${DAGSHUB_ACCESS_KEY_ID} && dvc remote modify origin --local secret_access_key ${DAGSHUB_ACCESS_KEY_ID} && dvc pull --force && exec uvicorn app:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS}