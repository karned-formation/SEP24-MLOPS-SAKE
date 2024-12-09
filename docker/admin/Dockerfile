FROM python:3.11
# la version "python:3.11-slim" provoque un probleme car "private_conn_dagshub.sh" s'appuie sur des fonctions non présentes dans ce docker

ARG COMMON_DIR
ARG SOURCE_DIR
ARG DOCKERFILE_DIR
ARG STREAMLIT_DIR

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=80
ENV WORKERS=1
ENV STREAMLIT_DIR ${STREAMLIT_DIR}

EXPOSE ${PORT}

RUN git clone https://github.com/karned-formation/SEP24-MLOPS-SAKE.git
RUN cd SEP24-MLOPS-SAKE/
# remove the following line when merging with main
RUN git switch training_admin_launch 
RUN git pull

WORKDIR ${APP_HOME}/SEP24-MLOPS-SAKE

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY ${DOCKERFILE_DIR}/private_conn_dagshub.sh ./
RUN chmod +x private_conn_dagshub.sh
RUN ./private_conn_dagshub.sh



CMD dvc pull && exec streamlit run ${STREAMLIT_DIR}/admin_streamlit.py --server.port 80