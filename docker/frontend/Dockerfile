FROM python:3.11-slim
EXPOSE 80
WORKDIR /app

ENV URL_BACKEND=https://sake.karned.bzh

COPY requirements.txt requirements.txt
COPY frontend.py frontend.py

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["streamlit", "run", "frontend.py", "--server.port=80", "--server.address=0.0.0.0"]