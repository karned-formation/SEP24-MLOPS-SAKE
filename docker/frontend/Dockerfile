FROM python:3.11-slim AS builder

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir streamlit

FROM python:3.11-slim

EXPOSE 80
WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install libmagic1 -y && rm -rf /var/lib/apt/lists/*

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENV STREAMLIT_WATCHDOG=0

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app.py app.py
COPY .streamlit/config.toml .streamlit/config.toml
COPY pages/feedback.py pages/feedback.py
COPY src/s3handler.py src/s3handler.py 
COPY src/custom_logger.py src/custom_logger.py 
COPY src/utils/files.py src/utils/files.py

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=80", "--server.address=0.0.0.0", "--global.developmentMode=false"]