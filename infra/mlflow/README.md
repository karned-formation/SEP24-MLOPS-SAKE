# Déploiement d'un serveur MLFlow
- PostGreSQL
- MLFlow

## Installation
```sh
kubectl create namespace sake
 helm install postgre -n sake -f ./postgre/values.yaml --generate-name 
```