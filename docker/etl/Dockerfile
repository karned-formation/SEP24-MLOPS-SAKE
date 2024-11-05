FROM python:3.11

ARG SOURCE_DIR
# Argument to build docker image command /!\ to be executed from root folder of Git
# Example: docker image build --build-arg DOCKERFILE_DIR=docker/clean_text -f docker/clean_text/Dockerfile . -t ms-sake-clean-text:1.0
ARG DOCKERFILE_DIR

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME /app
ENV PORT 8907

# Variables to be used in the app to access the data and store the results
# Endpoints url use container names 'ingest' and 'clean' to communicate with the other services inside the docker network
ENV OCR_ENDPOINT http://ingest:8901/txt/blocks-words 
ENV RAW_DATASET_DIR data/raw_per_classes/
ENV OCR_TEXT_DIR data/ocr_raw_per_classes/
ENV CLEAN_ENDPOINT http://clean:8903/clean
ENV CLEANED_DATASETS_DIR data/cleaned_per_classes/

EXPOSE $PORT

WORKDIR $APP_HOME

RUN apt-get upgrade -y
RUN pip install --upgrade pip
COPY $DOCKERFILE_DIR/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY $DOCKERFILE_DIR/app.py ./app.py
COPY ${SOURCE_DIR}/data/clean_all.py ./clean_all.py
COPY ${SOURCE_DIR}/data/ingest_all.py ./ingest_all.py
COPY ${SOURCE_DIR}/custom_logger.py ./custom_logger.py

CMD exec uvicorn app:app --host 0.0.0.0 --port $PORT