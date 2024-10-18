# Installer les outils/logiciels nécessaires

Installer Docker Desktop (Linux / MacOS / Windows) : 
	https://docs.docker.com/engine/install/

# Installer son environnement Python 3.11 "env_mlops"

## Créer son environnement avec Conda
Créer l'environnement conda avec python 3.11
```sh
conda env create -f environment.yml 
conda activate env_mlops 
```

Créer un Kernel (pour les notebooks Jupyter et/ou VS Code)
```sh
conda install -n env_mlops ipykernel --update-deps --force-reinstall --yes
python -m ipykernel install --user --name=env_mlops --display-name "env_mlops"
conda install jupyter --yes
```

Windows: lancer ce batch pour avoir un alias python3 sur pyhton (copie)
```sh
alias_python3_with_python.bat
```

## Créer son environnement avec Venv / Pip
`✨ /!\ au préalable : python 3.11 doit être installé et être la version active`

Créer l'environnement venv
```sh
python -m venv env_mlops
source env_mlops/bin/activate
pip install -r requirements.txt
```

## Installer packages complémentaires

Pour avoir les stop-words de spacy
```sh
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm
```

Pour permettre l'accès aux packages développés dans ce repository
```sh
pip install -e .
```

# Mise en place de DVC

Configuration de DVC (cela est récupérable sur le site) https://dagshub.com/Belwen/SEP24-MLOPS-SAKE
```sh
dvc remote modify origin --local access_key_id YOUR_ACCESS_KEY
dvc remote modify origin --local secret_access_key YOUR_ACCESS_KEY
```

Récupération des données
```sh
dvc pull 
```
