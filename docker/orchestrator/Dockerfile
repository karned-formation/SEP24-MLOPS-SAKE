FROM python:3.11-slim AS builder

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

COPY docker/orchestrator/requirements.txt requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV DATA_ETL_DOCKER_SERVICE_ETL=etl-service
ENV DATA_ETL_ROUTE_ETL_INGEST_ALL=etl/ingest
ENV DATA_ETL_ROUTE_ETL_CLEAN_ALL=etl/clean
ENV PREDICT_DOCKER_SERVICE_PREDICT=predict-service
ENV PREDICT_ROUTE_PREDICT=predict

EXPOSE 80
WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install libmagic1 -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY src/s3handler.py src/s3handler.py
COPY src/orchestrator/orchestrator.py src/orchestrator/orchestrator.py
COPY src/custom_logger.py src/custom_logger.py
COPY docker/orchestrator/app.py app.py

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]