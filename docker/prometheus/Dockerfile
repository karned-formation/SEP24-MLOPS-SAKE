FROM prom/prometheus:latest

ARG DOCKERFILE_DIR

COPY ${DOCKERFILE_DIR}/prometheus.yml /etc/prometheus/prometheus.yml
COPY ${DOCKERFILE_DIR}/alerting_rules.yml /etc/prometheus/alerting_rules.yml

EXPOSE 9090