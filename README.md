# SEP24-MLOPS-SAKE

## Documentation

- [Guide d'installation](docs.md/installation.md) : Instructions pour installer le projet.
- [Guide d'utilisation](docs.md/utilisation.md) : Comment utiliser les fonctionnalités du projet.

## Structure du projet

- **data/** : Données gérées avec DVC/Dagshub
- **docs.md/** : Autres fichiers de documentations liés à ce fichier README.md
- **notebooks/** : Notebooks du projet.
- **src/** : Code source du projet.
- **steps/** : Scripts des pipelines
- **tests/** : Tests unitaires et d'intégration

## Microservice : API REST
Un fichier Docker Compose à la racine du projet permet de lancer l'ensemble des microservices.

'''sh
docker-compose up
```

Pour accéder aux différentes documentations, il suffit de se rendre à l'adresse suivante :
OCR
http://localhost:8901/docs

ETL
http://localhost:8903/docs
