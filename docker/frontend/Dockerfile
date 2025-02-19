FROM python:3.11-slim AS builder

ARG DOCKERFILE_DIR

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

COPY ${DOCKERFILE_DIR}/requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir streamlit

FROM python:3.11-slim

ARG DOCKERFILE_DIR
ARG SOURCE_DIR
ARG COMMON_DIR

EXPOSE 80
WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install libmagic1 -y && rm -rf /var/lib/apt/lists/*

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY ${DOCKERFILE_DIR}/app.py app.py
COPY ${SOURCE_DIR}/.streamlit/config.toml .streamlit/config.toml
COPY ${SOURCE_DIR}/pages/feedback.py pages/feedback.py
COPY ${COMMON_DIR}/s3handler.py src/s3handler.py 
COPY ${COMMON_DIR}/custom_logger.py src/custom_logger.py 
COPY ${COMMON_DIR}/utils/files.py src/utils/files.py

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=80", "--server.address=0.0.0.0"]