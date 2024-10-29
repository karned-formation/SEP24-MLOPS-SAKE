FROM python:3.11

# Argument t give to build command to be executed from root folder of Git
# docker image build --build-arg DOCKERFILE_PATH=docker/clean_text -f docker/clean_text/Dockerfile .
ARG DOCKERFILE_PATH

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME /app
ENV PORT 8903

EXPOSE $PORT

WORKDIR $APP_HOME

RUN apt-get update
RUN apt-get upgrade -y
RUN pip install --upgrade pip

COPY src/data/clean_text.py ./
COPY $DOCKERFILE_PATH/download_contents.py ./
COPY $DOCKERFILE_PATH/app.py ./
COPY $DOCKERFILE_PATH/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN python3 -m spacy download fr_core_news_sm
RUN python3 -m spacy download en_core_web_sm

RUN python3 download_contents.py

CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT} --workers 1 --reload