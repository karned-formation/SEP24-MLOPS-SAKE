FROM python:3.11

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=8904

EXPOSE $PORT

WORKDIR $APP_HOME

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY preprocessing.py ./

CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT}