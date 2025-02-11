FROM python:3.11-slim AS builder

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y curl unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

RUN aws --version

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

RUN --mount=type=secret,id=aws_secrets \
    export $(cat /run/secrets/aws_secrets | xargs) && \
    aws s3 cp s3://datascientest-mlops-classif/models/ovrc:latest.joblib /app/models/ovrc.joblib --region=eu-north-1 && \
    aws s3 cp s3://datascientest-mlops-classif/models/tfidf_vectorizer.joblib /app/models/tfidf_vectorizer.joblib --region=eu-north-1

FROM python:3.11-slim AS runtime

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
EXPOSE 80

COPY --from=builder /install /usr/local

COPY app.py app.py
COPY src/predict/predict.py src/predict/predict.py
COPY src/custom_logger.py src/custom_logger.py

COPY --from=builder /app/models/ovrc.joblib /app/models/ovrc.joblib
COPY --from=builder /app/models/tfidf_vectorizer.joblib /app/models/tfidf_vectorizer.joblib

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]