FROM python:3.11-slim

ARG COMMON_DIR
ARG SOURCE_DIR
ARG DOCKERFILE_DIR

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app

EXPOSE 80

WORKDIR $APP_HOME

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY $DOCKERFILE_DIR/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY $DOCKERFILE_DIR/app.py ./app.py

COPY $SOURCE_DIR/clean_etl.py $SOURCE_DIR/clean_etl.py
COPY $SOURCE_DIR/ingest_etl.py $SOURCE_DIR/ingest_etl.py
COPY $COMMON_DIR/s3handler.py $COMMON_DIR/s3handler.py
COPY $COMMON_DIR/custom_logger.py $COMMON_DIR/custom_logger.py

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]