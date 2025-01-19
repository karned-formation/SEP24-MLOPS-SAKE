import json
import traceback
import boto3
import joblib
from src.custom_logger import logger
import mlflow
import subprocess
import dagshub
import os 
from src.s3handler import S3Handler

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value

def extract_relevant_metrics(metrics):
    return {'accuracy': metrics['accuracy'],
            'f1_score': metrics['avg_f1']}

def initialize_ml_flow():
    # Run the script to set up the private connection to Dagshub - To be deleted when we'll use our own MLflow server
    subprocess.run('./private_conn_dagshub.sh', shell=True, executable='/bin/bash')
    logger.info(f"Initalizing Dagshub for MLflow tracking.")
    dagshub.init(repo_owner='Belwen', repo_name='SEP24-MLOPS-SAKE', mlflow=True)

def get_env_variables():
    """Get environment variables."""
    model_path = get_env_var("MODEL_EVAL_MODEL_PATH")
    X_train_path = get_env_var("DATA_PREPROCESSING_X_TRAIN_PATH")
    y_train_path = get_env_var("DATA_PREPROCESSING_Y_TRAIN_PATH")
    X_test_path = get_env_var("DATA_PREPROCESSING_X_TEST_PATH")
    y_test_path = get_env_var("DATA_PREPROCESSING_Y_TEST_PATH")
    metrics_dir = get_env_var("MODEL_EVAL_METRICS_DIR")
    cleaned_dir = get_env_var("DATA_CLEANING_CLEANED_DATASETS_DIR")
    confusion_matrix_path = os.path.join(metrics_dir, "confusion_matrix.json")
    return model_path, X_train_path, y_train_path, X_test_path, y_test_path, metrics_dir, cleaned_dir, confusion_matrix_path


def create_mlflow_run(experiment_id, metrics, artifacts, model, commit_hash):
    """Update MLflow with the evaluation metrics. Return the run ID."""
    logger.info("Creating MLflow run...")
    mlflow.set_experiment(experiment_id)
    with mlflow.start_run() as run:
        mlflow.log_metric("test_accuracy", 1.0)
        for key, value in metrics.items():
            mlflow.log_metric(key, value)
            
        for key, value in artifacts.items():
            mlflow.log_artifact(value)
        
        mlflow.sklearn.log_model(model, get_env_var("MLFLOW_MODEL_NAME"))

        mlflow.set_tag("commit_hash", commit_hash)

        logger.info(f"Eval metrics and artifacts successfully logged to MLflow.")
    return run.info.run_id

def register_model(run_id: int):
    """Register the model in the MLflow registry."""
    try: 
        logger.info(f"Registering model in MLflow registry...")
        mlflow.register_model(
            model_uri=f"runs:/{run_id}/{get_env_var('MLFLOW_MODEL_NAME')}",
            #version=get_env_var("MLFLOW_MODEL_VERSION"),
            name=get_env_var("MLFLOW_MODEL_NAME"),
            await_registration_for=600
        )
        logger.info(f"Model successfully registered in MLflow registry. Run ID: {run_id}")
    except Exception as e:
        logger.error(f"Error registering the model in the MLflow registry: {traceback.format_exc()}")
        raise e
    
def load_metrics(file_path='metrics/scores.json'):
    with open(file_path, 'r') as f:
        scores = json.load(f)
    return scores

def save_to_mlflow(commit_hash: str) -> str:
    initialize_ml_flow()
    model_path, X_train_path, y_train_path, X_test_path, y_test_path, metrics_dir, cleaned_dir, confusion_matrix_path = get_env_variables()  
    
    file_path = os.path.join(metrics_dir, "scores.json")   
    metrics = load_metrics(file_path)  
    model = joblib.load(model_path)
    

    # Update MLflow with the evaluation metrics and artifacts
    run_id = create_mlflow_run(experiment_id=get_env_var("MLFLOW_EXPERIMENT_ID"), 
                                metrics=extract_relevant_metrics(metrics),
                                model=model,
                                artifacts={
                                    "cleaned_datasets": cleaned_dir,
                                    "X_train": X_train_path,
                                    "y_train": y_train_path,
                                    "X_test": X_test_path, 
                                    "y_test": y_test_path,
                                    "confusion_matrix": confusion_matrix_path},
                                commit_hash=commit_hash)
    logger.info(run_id)
    return run_id

def list_mlflow_runs():
    """
    Retrieve all MLflow runs
    """
    initialize_ml_flow()

    experiment_name = get_env_var("MLFLOW_EXPERIMENT_ID")

    # Fetch runs
    if experiment_name:
        runs = mlflow.search_runs(experiment_names=[experiment_name])
    else:
        # If no specific experiment, search across all experiments
        runs = mlflow.search_runs()

    # Customize columns as needed
    columns_to_display = [
        'tags.mlflow.runName', 
        'start_time', 
        'end_time', 
        'status',
        'metrics.accuracy',
       	'metrics.f1_score',	
        'tags.commit_hash'
    ]
    
    # Select and rename columns for better readability
    display_runs = runs[columns_to_display].copy()
    display_runs.columns = [col.split('.')[-1] for col in display_runs.columns]
    
    return display_runs.to_json()

def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        logger.info(f"command : {command} \nresult : {result}")
        return result.stdout.strip()
    except Exception as e:
        return "", str(e)

def git_revert_to_commit(commit_hash):
    """
    Attempt to revert to a specific commit hash
    
    Args:
        commit_hash (str): Commit hash to revert to
    
    Returns:
        tuple: (success_flag, output_message)
    """
    try:
         # Fetch the latest changes from remote
        fetch_result = subprocess.run(
            ['git', 'fetch', 'origin'], 
            capture_output=True, 
            text=True, 
            check=True
        )

        logger.info(f"GIT FETCH ORIGIN: {fetch_result}")
        
        # Revert to the specific commit
        revert_result = subprocess.run(
            ['git', 'reset', '--hard', commit_hash], 
            capture_output=True, 
            text=True, 
            check=True
        )

        
        logger.info(f"GIT REVERT: {revert_result}")

        dvc_pull_result = run_command("dvc pull")

        
        logger.info(f"DVC PULL: {dvc_pull_result}")


        return True, "Successfully reverted to commit"
    
    except subprocess.CalledProcessError as e:
        return False, f"Git revert failed: {e.stderr}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def initialize_s3_handler():
    """Initialize the S3 handler with environment variables."""
    aws_access_key_id = get_env_var("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_env_var("AWS_SECRET_ACCESS_KEY")
    aws_bucket_name = get_env_var("AWS_BUCKET_NAME")
    logger.info("S3 handler initialized.")
    return S3Handler(aws_bucket_name)

def register_model_to_s3() -> bool:
    """Register current model to S3."""
    try:
        s3 = initialize_s3_handler()
        
        # Get latest model 
        model_path = get_env_var("MODEL_TRAIN_MODEL_TRAIN_PATH")

        s3.upload_file(model_path, "models/ovrc:latest.joblib")
        
        
        
        return True
    except Exception as e:
        print(f"Error registering model: {str(e)}")
        return False