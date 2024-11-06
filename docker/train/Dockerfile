FROM python:3.11

ARG SOURCE_DIR
ARG DOCKERFILE_DIR
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=8905

EXPOSE $PORT

WORKDIR $APP_HOME

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

COPY $DOCKERFILE_DIR/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY $DOCKERFILE_DIR/app.py ./
COPY $SOURCE_DIR/train.py ./

CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT}