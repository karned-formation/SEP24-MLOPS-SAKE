FROM python:3.11-slim AS builder

ARG COMMON_DIR
ARG SOURCE_DIR
ARG DOCKERFILE_DIR

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app

WORKDIR $APP_HOME

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY $DOCKERFILE_DIR/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python3 -m spacy download fr_core_news_sm && \
    python3 -m spacy download en_core_web_sm

COPY $DOCKERFILE_DIR/app.py ./
COPY $DOCKERFILE_DIR/download_contents.py ./

COPY $SOURCE_DIR/clean_text.py $SOURCE_DIR/clean_text.py
COPY $COMMON_DIR/custom_logger.py $COMMON_DIR/custom_logger.py

RUN python3 download_contents.py

FROM python:3.11-slim AS runtime

ARG APP_HOME=/app
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=80
ENV WORKERS=1

EXPOSE $PORT

WORKDIR $APP_HOME

COPY --from=builder $APP_HOME $APP_HOME

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]