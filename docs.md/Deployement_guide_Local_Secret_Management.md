# Local Deployement: management of secrets

## First step : register your secrets in **.env_original**
```
AWS_BUCKET_NAME=datascientest-mlops-classif
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
DAGSHUB_ACCESS_KEY_ID=
DAGSHUB_SECRET_ACCESS_KEY=
DAGSHUB_TOKEN= le même que dagshub secret
GITHUB_TOKEN=suivre la procédure ci-dessous pour le générer
GITHUB_USERNAME=votre-user-github
GITHUB_OWNER=karned-formation
GITHUB_REPO=SEP24-MLOPS-SAKE
```
Génération du Github token:
1) Aller dans https://github.com/settings/profile
2) Sélectionner "Developer Settings" tout en bas à gauche
3) Cliquer sur "Personal access tokens"/"Tokens (classic)"
4) Cliquer sur "Generate new token" / "Generate new token classic"
5) Indiquer une note et sélectionner le scope "repo"
6) Cliquer sur "generate token"
7) Copier le token et coller le dans le fichier **.env_original**

## 2nd step : generate and update the file "**.env**"
Ce programme **config_transform_as_env.py** réalise 2 choses
1) génère 2 fichiers **.env_mlops_sake** et **.env_plantUML** à partir du fichier de paramètres de notre application [params.yaml](../params.yaml) exprimé en YAML
2) créée les répertoires nécessaires dans le répertoire /data pour permettre l'exécution de la pipeline DVC Training
```
python3 src/config_transform_as_env.py
```
Explications:
- Le fichier **.env_mlops_sake** est la traduction de [params.yaml](../params.yaml) sous la forme "CONFIG_NAME=CONFIG_VALEUR"
- Le fichier **.env_plantUML** est la traduction de [params.yaml](../params.yaml) sous une forme utlisable pour paramétrer les diagrammes PlantUML (voir ../report/plantUML_models/)
- Le fichier [params.yaml](../params.yaml) permet donc de centraliser en 1 point unique tous les paramétrage
    - Ce fichier **params.yaml** sert aussi à paramètrer l'exécution de la pipeline DVC Training via [dvc.yaml](../dvc.yaml)

Ce programme **smart_merge_.env_.env_mlops_sake.py** réalise la fusion de **.env_mlops_sake** et **.env_original** dans **.env**
```
python src/smart_merge_.env_.env_mlops_sake.py
```
Le fichier **.env** est utilisé dans le fichier "[docker-compose.yaml)](../docker-compose.yaml)" et il sert aussi à définir les variables d'environnement des dockers
