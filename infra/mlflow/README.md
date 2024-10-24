# Déploiement d'un serveur MLFlow
- PostGreSQL
- MLFlow

## Installation
```sh
kubectl create namespace sake
 helm install postgre -n sake -f ./postgre/values.yaml --generate-name 
```

La création du PVC créé un dossier Lost&Found (chez OVh en tout cas) il faut donc utiliser un sous-dossier pour la base de données MLFow.