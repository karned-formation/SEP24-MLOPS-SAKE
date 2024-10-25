# Déploiement d'un serveur MLFlow
- PostGreSQL
- MLFlow
- GCS

## Déploiement

Création du namespace "sake" pour le déploiement.
```sh
kubectl create namespace sake
```

## Déploiement de PostGreSQL

**Création du secret**
```sh
PASSWORD=$(LC_CTYPE=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 32 | base64)
kubectl create secret generic mlflow-postgres-secret \
  --from-literal=postgres-password=$PASSWORD \
  -n sake
```

**Récupérer le mot de passe**
```sh
kubectl get secret mlflow-postgres-secret -n sake -o jsonpath='{.data.postgres-password}' | base64 -d
```

Utilisation d'un chart Helm afin de centraliser les variables dans un fichier values.yaml.
```sh
helm install postgre -n sake -f ./postgre/values.yaml --generate-name 
```

### problèmes rencontrés
- La création du PVC créé un dossier Lost&Found (chez OVh en tout cas) il faut donc utiliser un sous-dossier pour la base de données MLFow.


## Déploiement de MLFlow
Le déploiement du pod MLFlow exploite le secret défini pour le pod PostGreSQL déployé précédement.

Le déploiement nécessite un stockage externe (Google Cloud Storage) afin de stocker les métriques et les modèles.
- Il faut créer un bucket pour MLFow sur GCP.
- Il faut créer un compte de service sur GCP et lui attribuer les droits sur le bucket MLFlow.
- Une fois le fichier JSON téléchargé en local, créer un secret pour le stocker dans Kubernetes.

**Création du secret**
```sh
kubectl create secret generic sake-gcp-secret \
  --from-file=service-account-key.json=<path/to/service-account-key.json> \
  -n sake
```

**Déploiement du pod**
```sh
helm install mlflow -n sake -f ./mlflow/values.yaml --generate-name 
```

**Mise à jour**
```sh
helm list -A
helm upgrade --install <deployment_name> ./mlflow -n sake -f ./mlflow/values.yaml
```

### problèmes rencontrés

2024/10/25 06:26:19 ERROR mlflow.cli: No module named 'psycopg2'
Création d'un image Docker pour MLFlow qui contient le module psycopg2.
```txt
FROM ghcr.io/mlflow/mlflow:v2.17.0
RUN pip install psycopg2-binary
````

## Connexion 

```sh
 kubectl port-forward -n sake <pod_name> 5000:5000
```
