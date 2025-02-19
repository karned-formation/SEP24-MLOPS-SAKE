FROM grafana/grafana:latest

# Copy provisioning configuration for data sources and dashboards
COPY provisioning /etc/grafana/provisioning
COPY dashboards /var/lib/grafana/dashboards

EXPOSE 3000

CMD [ "grafana-reporter" ]