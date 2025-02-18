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
├── docs                    Folder documentation : some diagrams
├── notebooks               Notebooks - DEPRECATED (to reshape according to source code updates)
├── report                  About PlantUML documentation + Slides
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ CONFIGURATION of Dockers and programs
├── params.yaml                 All the configuration parameters
├── secrets                     Folders with the secrets to connect to Amazon S3
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
```
- [docker/](../docker/README_docker.md) : read details
```
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ SOURCE CODE
```
- [src/](../src/README_src.md) : read details
```
└──────────────────────────────────────────────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────────────────────
│ TESTS of the source folders "src" and "docker"
├── tests
```
- [tests/](../tests/README_tests.md) : read details
```
└──────────────────────────────────────────────────────────────────────────────────────