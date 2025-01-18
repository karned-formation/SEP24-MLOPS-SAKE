FROM python:3.11-slim AS builder

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir streamlit

FROM python:3.11-slim

EXPOSE 80
WORKDIR /app

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENV URL_BACKEND=https://sake.karned.bzh

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY frontend.py frontend.py

ENTRYPOINT ["streamlit", "run", "frontend.py", "--server.port=80", "--server.address=0.0.0.0"]