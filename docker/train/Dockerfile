FROM python:3.11-slim AS builder

ARG DOCKERFILE_DIR

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY ${DOCKERFILE_DIR}/requirements.txt requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime

ARG DOCKERFILE_DIR
ARG SOURCE_DIR
ARG COMMON_DIR

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
EXPOSE 80

COPY --from=builder /install /usr/local

COPY ${DOCKERFILE_DIR}/app.py app.py
COPY ${SOURCE_DIR}/train.py src/train/train.py
COPY ${COMMON_DIR}/custom_logger.py src/custom_logger.py

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]