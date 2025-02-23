FROM grafana/grafana:latest

# Copy provisioning configuration for data sources and dashboards
COPY provisioning /etc/grafana/provisioning
COPY dashboards /var/lib/grafana/dashboards

ENV GF_SERVER_HTTP_PORT=3000
EXPOSE 3000

CMD [ "grafana-reporter" ]