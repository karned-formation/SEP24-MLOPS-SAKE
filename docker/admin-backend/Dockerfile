FROM ubuntu:latest

# Define environment variables
ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 

EXPOSE 80
WORKDIR /app

# Install necessary packages
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y python3 python3-pip python3-venv git openssh-server 

# install the ssh key for github in root/.ssh
RUN mkdir -p /root/.ssh        
RUN chmod -R 600 /root/.ssh/  
COPY id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa 
RUN ssh-keyscan github.com >>/root/.ssh/known_hosts

# clone github repository
RUN GIT_SSH_COMMAND="ssh -i /root/.ssh/id_rsa" git clone git@github.com:karned-formation/SEP24-MLOPS-SAKE.git

WORKDIR /app/SEP24-MLOPS-SAKE

RUN git pull
RUN git switch -f prod 

# Create and set up virtual environment
RUN python3 -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install --no-cache-dir -r requirements.txt

# Create and set up virtual environment
RUN python3 -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install --no-cache-dir -r requirements.txt

# Ensure the data structure exists
RUN mkdir -p data/raw_per_classes/0 \
    data/raw_per_classes/1 \
    data/raw_per_classes/2 \
    data/ocr_raw_per_classes/0 \
    data/ocr_raw_per_classes/1 \
    data/ocr_raw_per_classes/2 \
    data/cleaned_per_classes/0 \
    data/cleaned_per_classes/1 \
    data/cleaned_per_classes/2 \
    data/processed/test \
    data/processed/train \
    metrics \
    models/train \
    models/vectorizers

# Set up DVC credentials at runtime, not during build
RUN . .venv/bin/activate && \
    --mount=type=secret,id=secrets \
    export $(cat /run/secrets/secrets | xargs) && \
    dagshub login --token "$DAGSHUB_TOKEN" && \
    dvc remote modify origin --local access_key_id "$DAGSHUB_ACCESS_KEY_ID" && \
    dvc remote modify origin --local secret_access_key "$DAGSHUB_SECRET_ACCESS_KEY" && \
    dvc pull --force || true

RUN apt-get update && apt-get install -y libmagic1 libmagic-dev

# Copy app at the root
COPY app.py .

CMD ["/bin/sh", "-c", ". .venv/bin/activate && exec uvicorn app:app --host 0.0.0.0 --port 80 --reload"]
