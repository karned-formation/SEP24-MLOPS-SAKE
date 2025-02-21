FROM grafana/grafana:latest

# Copy provisioning configuration for data sources and dashboards
COPY provisioning /etc/grafana/provisioning
COPY dashboards /var/lib/grafana/dashboards

ENV GF_SERVER_HTTP_PORT=80
EXPOSE 80

CMD [ "grafana-reporter" ]