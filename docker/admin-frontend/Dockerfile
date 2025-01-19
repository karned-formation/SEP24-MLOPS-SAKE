FROM python:3.11

ARG COMMON_DIR
ARG SOURCE_DIR
ARG DOCKERFILE_DIR

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=80
ENV WORKERS=1

EXPOSE ${PORT}
WORKDIR ${APP_HOME}


RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY $DOCKERFILE_DIR/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ${SOURCE_DIR}/admin-frontend.py admin-frontend.py

CMD streamlit run admin-frontend.py --server.port ${PORT}