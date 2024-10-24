# Déploiement d'un serveur MLFlow
- PostGreSQL
- MLFlow

## Installation
```sh
kubectl create namespace sake
helm install postgre -n sake -f ./postgre/values.yaml --generate-name 
```

La création du PVC créé un dossier Lost&Found (chez OVh en tout cas) il faut donc utiliser un sous-dossier pour la base de données MLFow.

Le déploiement du pod MLFlow exploite le secret défini pour le pod PostGreSQL.

Il faut créer un bucket pour MLFow sur GCP.
Il faut créer un compte de service sur GCP et lui attribuer les droits sur le bucket MLFlow.
Une fois le fichier JSON téléchargé en local 

```sh
kubectl create secret generic sake-gcp-secret \
  --from-file=service-account-key.json=<path/to/service-account-key.json> \
  -n sake

helm install mlflow -n sake -f ./mlflow/values.yaml --generate-name 
```