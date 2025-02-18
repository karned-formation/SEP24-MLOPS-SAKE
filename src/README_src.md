# src/ folder structure
```
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
