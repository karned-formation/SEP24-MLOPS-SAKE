FROM python:3.11

ARG SOURCE_DIR
ARG DOCKERFILE_DIR
ARG LOG_DIR

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=80

EXPOSE $PORT

WORKDIR $APP_HOME

RUN apt-get upgrade -y
RUN pip install --upgrade pip
COPY $DOCKERFILE_DIR/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY $DOCKERFILE_DIR/app.py ./app.py
COPY $SOURCE_DIR/data/clean_etl.py ./clean_etl.py
COPY $SOURCE_DIR/data/ingest_etl.py ./ingest_etl.py
COPY $SOURCE_DIR/s3handler.py ./s3handler.py
COPY $SOURCE_DIR/custom_logger.py ./custom_logger.py


CMD exec uvicorn app:app --host 0.0.0.0 --port $PORT