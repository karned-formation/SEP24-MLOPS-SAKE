# SEP24-MLOPS-SAKE

### Environnement
Créer l'environnement anaconda avec python 3.11
```conda create --name env_mlops python=3.11```

Activer l'environnement
```conda activate env_mlops```

Ajouter conda-forge channel pour la recherche de packages
```conda config --append channels conda-forge```

Cr�er un Kernel (pour les notebooks)
```conda install -n env_mlops ipykernel --update-deps --force-reinstall```

Installer les librairies requises
```conda install --yes --file requirements.txt```

Mettre à jour la liste des librairies requises
```conda list -e > requirements.txt```

Notes : 
importer les stopwords
>>> import nltk
>>> nltk.download('stopwords')
>>> nltk.download('punkt_tab')

importer 
python3 -m spacy download fr_core_news_sm
python3 -m spacy download en_core_web_sm

### Architecture des dossiers

