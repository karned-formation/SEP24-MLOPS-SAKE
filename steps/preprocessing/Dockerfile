FROM python:3.12.7

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME /app
ENV PORT 8904

EXPOSE $PORT

WORKDIR $APP_HOME

RUN apt-get update
RUN apt-get upgrade -y
RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY train.py ./

CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT}