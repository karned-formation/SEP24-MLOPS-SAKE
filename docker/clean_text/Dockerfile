FROM python:3.11-slim AS builder

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
EXPOSE 80

COPY --from=builder /install /usr/local

COPY docker/clean_text/app.py /app/
COPY docker/clean_text/download_contents.py /app/
COPY src/data/clean_text.py /app/src/data/clean_text.py
COPY src/custom_logger.py /app/src/custom_logger.py

RUN python3 -m spacy download fr_core_news_sm && \
    python3 -m spacy download en_core_web_sm

RUN python3 /app/download_contents.py

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]