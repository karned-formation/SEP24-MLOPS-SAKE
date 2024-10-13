# SEP24-MLOPS-SAKE

### Environnement
Créer l'environnement anaconda avec python 3.11
```conda create --name env_mlops python=3.11```

Activer l'environnement
```conda activate env_mlops```

Ajouter conda-forge channel pour la recherche de packages
```conda config --append channels conda-forge```

Créer un Kernel (pour les notebooks)
```conda install -n env_mlops ipykernel --update-deps --force-reinstall```

Installer les librairies requises
```conda install --yes --file requirements.txt```

Mettre à jour la liste des librairies requises
```conda list -e > requirements.txt```

Notes : 
importer les stopwords
```
import nltk
nltk.download('stopwords')
nltk.download('punkt_tab')
```
importer 
python3 -m spacy download fr_core_news_sm
python3 -m spacy download en_core_web_sm

### Importer les données avec DVC

dvc remote modify origin --local access_key_id YOUR_ACCESS_KEY
dvc remote modify origin --local secret_access_key YOUR_ACCESS_KEY

rm -rf data/raw_data
rm -rf .dvc/cache
dvc fetch data/raw_data.dvc
dvc pull 
dvc checkout


### Architecture des dossiers



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
