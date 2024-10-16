# Lancement des Microservices : API REST
Un fichier Docker Compose à la racine du projet permet de lancer l'ensemble des microservices.

```sh
docker-compose up
```

Pour accéder aux différentes documentations, il suffit de se rendre à l'adresse suivante :
- OCR : http://localhost:8901/docs
- ETL : http://localhost:8903/docs

# Lancement de la pipeline

```sh
dvc repro
```
