# Project folder structure
```
├── data                    Data only managed with DVC/DagsHub through pipelines
│   ├── cleaned
│   ├── models
│   ├── processed
│   ├── raw
│   └── vectorizers
├── doc_classification.egg-info     To ease the import of local packages
├── docs.md                 Documentations markdown used by README.txt
├── export_requirements     [TEMPORARY] during dev: export requirement (pip freeze / conda list -e)
├── notebooks               Notebooks
├── references              External data
├── report                  Reports used for documentation
│   ├── Exemple_plantUML    Some plantUML examples
│   └── plantUML_models     PlantUML Models (sources and output images) used for the documentation
├── src                     Source code
│   ├── data                To manage the data
│   ├── models              To manage the models
│   └── preprocessing       To manage the preprocessing of the features
├── steps                   Steps used in pipeline
│   ├── etl                 Docker for ETL (clean bag of words)
│   ├── preprocessing       Docker for preprocessing (vectorize bag of words)
│   ├── tests               [TO BE CLARIFIED] Tests for Dockers
│   └── training            Docker for training
└── tests                   [TO BE CLARIFIED] Tests
```
