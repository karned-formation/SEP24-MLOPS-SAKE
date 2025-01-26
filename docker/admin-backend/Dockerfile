FROM ubuntu:latest
# ubuntu needed for installing git and openssh-server

ARG COMMON_DIR
ARG SOURCE_DIR
ARG DOCKERFILE_DIR
ARG DAGSHUB_ACCESS_KEY_ID

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=80
ENV WORKERS=1

EXPOSE ${PORT}
WORKDIR ${APP_HOME}

# install needed apps
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y python3 python3-pip python3-venv curl git openssh-server 

# install the ssh key for github in root/.ssh
RUN mkdir -p /root/.ssh        
RUN chmod -R 600 /root/.ssh/  
COPY ${DOCKERFILE_DIR}/id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa 
RUN ssh-keyscan github.com >>/root/.ssh/known_hosts

# clone github repository
RUN GIT_SSH_COMMAND="ssh -i /root/.ssh/id_rsa" git clone git@github.com:karned-formation/SEP24-MLOPS-SAKE.git
WORKDIR ${APP_HOME}/SEP24-MLOPS-SAKE

# TODO : remove the following line when merging with main
RUN git switch -f admin_front 
RUN git pull


COPY ${DOCKERFILE_DIR}/private_conn_dagshub.sh ./
RUN chmod +x private_conn_dagshub.sh

COPY ${DOCKERFILE_DIR}/app.py .

# Create virtual environment
RUN python3 -m venv .venv
# Activate virtual environment and upgrade pip
RUN .venv/bin/pip install --upgrade pip
# Install packages in the virtual environment
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

RUN . .venv/bin/activate && \
    dvc remote modify origin --local access_key_id ${DAGSHUB_ACCESS_KEY_ID} && \
    dvc remote modify origin --local secret_access_key ${DAGSHUB_ACCESS_KEY_ID} && \
    dvc pull --force || true
CMD . .venv/bin/activate && exec uvicorn app:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS} --reload