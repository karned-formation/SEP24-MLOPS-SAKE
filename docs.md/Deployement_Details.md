# CI/CD

Le **repository de code** est synchronisé avec un **repository de deploiement** - [SEP24-MLOPS-SAKE-OPS](https://github.com/karned-formation/SEP24-MLOPS-SAKE-OPS)

- Jenkins (See /sake/CI below) fait les tests et build les dockers et les poussent sur DockerHub 
- ArgoCD with Kubernetes (See /sake/charts below) Scrute le **repository de deploiement** qui désigne ce qui doit être en production

```
SEP24-MLOPS-SAKE-OPS = Repository de Deploiement
├── mlflow
│   ├── README.md       # Documentation of MLFlow server deployment
│   ├── charts          # Configuration 
│   │   │                  - Chart.yaml
│   │   │                  - deployment.yaml
│   │   │                  - service.yaml
│   │   │                  - values.yaml
│   │   ├── mlflow
│   │   └── postgre
│   └── mlflow
│       └── Dockerfile
└── sake
    ├── CI              # Jenkins files
    │   ├── clean_text
    │   ├── etl
    │   ├── file
    │   ├── frontend
    │   ├── gateway
    │   ├── ocr
    │   ├── orchestrator
    │   └── predict
    └── charts      # ArgoCD configuration with Kubernetes 
        │                - Chart.yaml
        │                - deployment.yaml
        │                - service.yaml
        │                - values.yaml
        ├── admin
        ├── admin-backend
        ├── admin-frontend
        ├── alertmanager
        ├── clean
        ├── etl
        ├── eval
        ├── file
        ├── frontend
        ├── gateway
        ├── grafana
        ├── keycloak
        ├── node-exporter
        ├── ocr
        ├── orchestrator
        ├── predict
        ├── preprocessing
        ├── prometheus
        └── train
