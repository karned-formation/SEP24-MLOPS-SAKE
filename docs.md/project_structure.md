# Project folder structure
```
├── .dockerignore
├── .dvc
│   └── config
├── .dvcignore
├── .gitignore
├── doc_classification.egg-info     To ease the import of local packages
├── setup.py

├── params.yaml                     All the configuration parameters

├── data                            Data mainly managed with DVC/DagsHub through pipelines
│   ├── raw.dvc
│   └── working_dataset.csv

├── docker                          The dockers 
│   ├── api_gateway
│   ├── clean_text
│   ├── etl
│   ├── eval
│   ├── preprocessing
│   └── train
├── docker-compose.yaml             The Docker-compose declaration

├── README.md                       The documentation of the project
├── docs.md                         Documentations markdown used by README.md
├── dvc.lock
├── dvc.yaml

├── environment.yml                 
├── requirements.txt
├── export_requirements             TEMPORARY during dev: export requirement (pip freeze / conda list -e)

├── infra                           The installation of MLFlow Server
│   ├── mlflow
│   │   ├── README.md
│   └── sake
│       └── charts
│           ├── etl
│           └── gateway

├── metrics                 The outputs metrics of the pipeline
│   ├── confusion_matrix.json
│   └── scores.json

├── notebooks               Notebook - DEPRECATED (to reshape according to source code updates)
│   ├── 01-Eddie-Get_Data_Invoice_Donuts.ipynb
│   ├── 02-Generic_BagOfWord_Try_models_DEPRECATED.ipynb
│   └── 03-Ingest-Notebook_DEPRECATED.ipynb

├── references              External data

├── report                  About PlantUML documentation
│   ├── Exemple_plantUML
│   └── plantUML_models     PlantUML Models (sources and output images) 
│       ├── out
│       └── src

├── scripts                     Various bash scripts
├── tools                       Various windows batches

├── src                         Source code
│   ├── data                    To manage the data
│   │   ├── structure_raw.py
│   │   ├── clean_text.py
│   │   ├── clean_all.py
│   │   └── ingest_all.py
│   ├── preprocessing           To manage the preprocessing of the features
│   │   └── preprocessing.py
│   ├── train                   To manage the training of the model
│   │   └── train.py
│   └── eval                    To manage the evaluation of the model
│       └── eval.py

└── tests                       Tests [UNDER CONSTRUCTION]

