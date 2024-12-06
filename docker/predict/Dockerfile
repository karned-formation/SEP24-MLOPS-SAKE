FROM python:3.11

ARG SOURCE_DIR
ARG DOCKERFILE_DIR
ARG LOG_DIR
ARG MODELS_DIR

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=80

EXPOSE $PORT

WORKDIR $APP_HOME

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

COPY $DOCKERFILE_DIR/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY $DOCKERFILE_DIR/app.py app.py
COPY $SOURCE_DIR/predict/predict.py $SOURCE_DIR/predict/predict.py
COPY $LOG_DIR/custom_logger.py  $LOG_DIR/custom_logger.py
COPY $SOURCE_DIR/s3handler.py $SOURCE_DIR/s3handler.py
COPY $MODELS_DIR/vectorizers/tfidf_vectorizer.joblib $MODELS_DIR/vectorizers/tfidf_vectorizer.joblib
COPY $MODELS_DIR/train/ovrc.joblib $MODELS_DIR/train/ovrc.joblib

CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT} --reload