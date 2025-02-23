# Install required softwares & tools

- [x] Install Docker Desktop (Linux / MacOS / Windows) : 
	https://docs.docker.com/engine/install/

- [x] Install VS Code : https://code.visualstudio.com/download

- [x] Install Plant UML Extension in VS Code : 
	https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml
	with settings:
  - "plantuml.diagramsRoot": "report/plantUML_models/src"
  - "plantuml.exportOutDir": "report/plantUML_models/out"
  - "plantuml.server": "http://www.plantuml.com/plantuml"
  - "plantuml.exportFormat": "png"
  - "plantuml.exportIncludeFolderHeirarchy": true
  - "plantuml.exportSubFolder": false

# Install environment Python 3.11 "env_mlops"

The environment may be installed either through conda or through VirtualEnv/Pip

## Create environment through Conda
- Create environment through Conda with python 3.11 and install packages
	```sh
	conda env create -f environment.yml 
	conda activate env_mlops 
	```

- [Windows] Run this batch get an alias 'python3' for 'pyhton' (copy)
	```sh
	tools/alias_python3_with_python.bat
	```

- Create Kernel (used for notebooks Jupyter and/or VS Code)
	```sh
	conda install -n env_mlops ipykernel --update-deps --force-reinstall --yes
	python3 -m ipykernel install --user --name=env_mlops --display-name "env_mlops"
	conda install jupyter --yes
	```

## Create environment with VEnv / Pip
- /!\ Pre-requisites : **python 3.11** shall be installed and be the active version

- Create environment venv and install packages
	```sh
	python3 -m venv env_mlops
	source env_mlops/bin/activate
	pip install -r requirements.txt
	```

## Install complementary packages in the environnement "env_mlops"

- To get stop-words from spacy
	```sh
	python3 -m spacy download fr_core_news_sm
	python3 -m spacy download en_core_web_sm
	```

# Configure DVC

- Configuration DVC (accessible from site https://dagshub.com/Belwen/SEP24-MLOPS-SAKE)
	```sh
	dvc remote modify origin --local access_key_id YOUR_ACCESS_KEY
	dvc remote modify origin --local secret_access_key YOUR_ACCESS_KEY
	```

- Get the last updated DVC data
	```sh
	dvc pull 
	```
# Prerequisites for Dagshub with MLflow
```
dagshub login --token [YOUR_PRIVATE_TOKEN] <--- Replace with your token generated in your Dagshub profile
```


