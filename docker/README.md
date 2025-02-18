# docker/ folder structure
```
┌──────────────────────────────────────────────────────────────────────────────────────
│ DOCKER definitions
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
```

# Overview of the Docker architecture
![Project_overview](../docs/Project_overview.png)

- USER-Frontend = Docker "**frontend**"
- Predict-Orchestrator = Docker "**orchestrator**"
- ADMIN-Grafana = Docker "**grafana**"
- ADMIN-Frontend = Docker "**admin-frontend**"
- TRAINING-Admin-Backend = Docker "**admin-backend**"

See [Business case High Level overview](project_overview_business_cases.md) (click to see the differents steps)

# User Prediction Pipeline (docker architecture)
![User_predictions_overview](../docs/User_predictions_overview.png)

# User Feedback Management (docker architecture)
![User_Feedback_overview](../docs/User_Feedback_overview.png)

# User Feedback Loop (docker architecture)
![Admin_Feedback_Loop_overview](../docs/Admin_Feedback_Loop_overview.png)

# Admin Training Pipeline (docker architecture)
![Admin_train_Overview](../docs/Admin_train_Overview.png)

# Admin Monitoring (docker architecture)
![Admin_Monitoring](../docs/Admin_Monitoring.png)