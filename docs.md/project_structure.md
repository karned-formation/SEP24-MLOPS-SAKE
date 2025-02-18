# Project folder structure
```
┌──────────────────────────────────────────────────────────────────────────────────────
│ GENERAL Configuration 
├── .dockerignore
├── .dvc
│   └── config
├── .dvcignore
├── .gitignore
├── doc_classification.egg-info
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ DOCUMENTATION
├── README.md               The documentation of the project
├── docs.md                 Folder documentations markdown used by README.md
├── docs                    Folder documentation for gateway
├── notebooks               Notebooks - DEPRECATED (to reshape according to source code updates)
├── report                  About PlantUML documentation
│   ├── Exemple_plantUML
│   └── plantUML_models     PlantUML Models (sources and output images) 
│       ├── out
│       └── src
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ CONFIGURATION of Dockers and programs
├── params.yaml                 All the configuration parameters
├── secrets                     Contains the secret for S3
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ PACKAGE to build up the deployment environment
├── requirements.txt
├── environment.yml
├── export_requirements         TEMPORARY during dev: export requirement (pip freeze / conda list -e)
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ DVC folder
├── data                        Data managed with DVC/DagsHub through DVC pipelines
│   └── raw_per_classes.dvc
├── metrics
├── models
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ DVC PIPELINE for TRAINING
├── dvc.lock
├── dvc.yaml
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ MISCELLEANOUS ASSETS
├── references              DEPRECATED (original dataset)
├── scripts                 Various utility bash scripts
├── tools                   Various utility batch scripts
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ DOCKER definitions
├── docker-compose.yaml         How to build locally the Dockers
├── docker                      
│   ┌────────────────────────────────────────
│   │ COMMON DOCKERS used in several pipeline
│   ├── etl             Extract Tranform Load (ocerize and clean pictures)
│   │                   Used in Pipeline Training by docker "admin-backend"
│   │                   Used in Pipeline Prediction by docker "orchestrator"
│   ├── clean_text      Clean the ocerized text
│   │                   Used by docker "etl"
│   ├── file            Save data under Amazon S3
│   │                   Used in Pipeline Training by docker "admin-backend"
│   │                   Used in Pipeline Prediction by docker "orchestrator"
│   ┌────────────────────────────────────────
│   │ DOCKERS for the PIPELINE TRAINING
│   ├── admin-frontend  Streamlit Admin frontend
│   ├── admin-backend   Main Docker for the Pipeline Training
│   │                     * Implementing DVC pipeline (dvc repro)
│   │                     * Save data : git/dvc commit/push
│   │                     * MLFlow save experiment
│   │                     * Ability to register a model
│   │                     * Ability to restore another previous experiment
│   ├── preprocessing   Perform the preprocessing of data (vectorize and split)
│   ├── train           Perform the trainig of model
│   ├── eval            Perform the evaluation of model
│   ┌────────────────────────────────────────
│   │ DOCKERS for the PIPELINE PREDICTION
│   ├── frontend        Streamlit User frontend
│   ├── orchestrator    Main Docker for the Pipeline Prediction
│   ├── predict         Perform a prediction with a model
│   ┌────────────────────────────────────────
│   │ DOCKERS for the MONITORING
│   ├── prometheus
│   ├── grafana
│   ├── alertmanager
│   ┌────────────────────────────────────────
│   │ DOCKER for Deployment
│   ├── gateway         Manage interface open to Streamlit User/Admin frontend
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ SOURCE CODE
├── src
│   ┌───────────────────────────────────────────────────────────────
│   │ COMMON BASIC FUNCTIONS used by different functions listed below
│   ├── check_structure.py
│   ├── common_utils.py
│   ├── config.py
│   ├── config_manager.py
│   ├── smart_merge_.env_.env_mlops_sake.py
│   ├── config_transform_as_env.py
│   ├── custom_logger.py
│   ├── entity.py
│   ├── s3handler.py
│   ├── save_commit_hash.py
│   └── utils               
│   ┌───────────────────────────────────────────────────────────────
│   │ COMMON SOURCE CODE for the several dockers
│   ├── data            To manage the ingest and cleaning of pictures
│   │                   Used by docker "etl" and "clean_text"
│   ├── file            To manage the usage of Amazon S3
│   │                   Used by docker "admin-backend" and "orchestrator"
│   ┌───────────────────────────────────────────────────────────────
│   │ SOURCE CODE for the dockers involved in PIPELINE TRAINING or MONITORING
│   ├── streamlit       To manage the Admin FrontEnd
│   │                   Used by docker "admin-backend"
│   ├── admin           To manange the Pipeline Training
│   │                   Used by docker "admin-frontend"
│   ├── preprocessing   To manage the preprocessing of the features
│   ├── train           To manage the training of the model
│   ├── eval            To manage the evaluation of the model
│   ┌───────────────────────────────────────────────────────────────
│   │ SOURCE CODE for the dockers involved in PIPELINE PREDICTION
│   ├── frontend        To manage the User FrontEnd
│   │                   Used by docker "frontend"
│   ├── orchestrator    To manage the Pipeline Prediction
│   │                   Used by docker "orchestrator"
│   ├── predict         To manage the predictions
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ TESTS of the source folders "src" and "docker"
├── tests
│   ├── functional      Tests at a functional level checking one Docker
│   │   └── docker
│   │       ├── etl
│   │       ├── ocr
│   │       ├── orchestrator
│   │       └── predict
│   ├── integration     Integration Tests of Dockers
│   ├── requests        End to End test of high level interface
│   └── unit            Unitary test of functions in "src" folder
└──────────────────────────────────────────────────────────────────────────────────────