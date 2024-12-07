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

EXPOSE $PORT

WORKDIR $APP_HOME

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY $DOCKERFILE_DIR/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY $DOCKERFILE_DIR/app.py ./

COPY $SOURCE_DIR/mlflow_tracking.py $SOURCE_DIR/mlflow_tracking.py
COPY $COMMON_DIR/custom_logger.py $COMMON_DIR/custom_logger.py
COPY $STREAMLIT_DIR/admin_streamlit.py $STREAMLIT_DIR/admin_streamlit.py


COPY ${DOCKERFILE_DIR}/private_conn_dagshub.sh ./
RUN chmod +x private_conn_dagshub.sh
RUN ./private_conn_dagshub.sh

CMD exec streamlit run $STREAMLIT_DIR/admin_streamlit.py --server.port 80