FROM grafana/grafana:latest
ARG DOCKERFILE_DIR

# Copy provisioning configuration for data sources and dashboards
COPY ${DOCKERFILE_DIR}/provisioning /etc/grafana/provisioning
COPY ${DOCKERFILE_DIR}/dashboards /var/lib/grafana/dashboards

EXPOSE 3000

CMD [ "grafana-reporter" ]