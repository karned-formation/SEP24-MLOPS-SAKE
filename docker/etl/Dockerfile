FROM python:3.11-slim AS builder

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

COPY docker/etl/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 80
WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install libmagic1 -y && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY docker/etl/app.py ./app.py
COPY src/data/clean_etl.py src/data/clean_etl.py
COPY src/data/ingest_etl.py src/data/ingest_etl.py
COPY src/s3handler.py src/s3handler.py
COPY src/custom_logger.py src/custom_logger.py

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]