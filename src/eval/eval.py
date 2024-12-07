import pandas as pd
import numpy as np
from imblearn.metrics import classification_report_imbalanced
import json
import os
import subprocess
import joblib 
import traceback

from src.custom_logger import logger

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value

def get_env_variables():
    """Get environment variables."""
    model_path = get_env_var("MODEL_EVAL_MODEL_PATH")
    X_test_path = get_env_var("DATA_PREPROCESSING_X_TEST_PATH")
    y_test_path = get_env_var("DATA_PREPROCESSING_Y_TEST_PATH")
    metrics_dir = get_env_var("MODEL_EVAL_METRICS_DIR")
    host_uid = get_env_var("HOST_UID")
    host_gid = get_env_var("HOST_GID")
    return model_path, X_test_path, y_test_path, metrics_dir, host_uid, host_gid

def load_variables(model_path, X_test_path, y_test_path):
    """Load the model, X_test, and y_test from specified file paths."""
    model = joblib.load(model_path)
    X_test = joblib.load(X_test_path)
    y_test = joblib.load(y_test_path)
    return model, X_test, y_test

def get_accuracy(model, X_test, y_test):
    """Calculate and return model accuracy on the test data."""
    return model.score(X_test, y_test)

def get_confusion_matrix(y_test, y_pred):
    """Generate a confusion matrix from true and predicted labels."""
    return pd.crosstab(y_test, y_pred, rownames=['True Class'], colnames=['Predicted Class'])

def convert_numpy_types(obj):
    """Convert NumPy types in an object to native Python types recursively."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, np.float64) or isinstance(obj, np.float32):
        return float(obj)
    elif isinstance(obj, np.int64) or isinstance(obj, np.int32):
        return int(obj)
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

def get_metrics(model, X_test, y_test, y_pred):
    """Compute classification metrics, convert types, and return as JSON."""
    report = classification_report_imbalanced(y_test, y_pred, output_dict=True)
    report['accuracy'] = get_accuracy(model, X_test, y_test)
    report = convert_numpy_types(report)
    return report

def save_json_metrics(metrics, metrics_dir):
    """Save metrics as a JSON file at the specified file path."""
    file_path = os.path.join(metrics_dir, "scores.json")
    if metrics_dir and not os.path.exists(metrics_dir):
        os.makedirs(metrics_dir)
    with open(file_path, 'w') as json_file:
        json.dump(metrics, json_file)
    logger.info(f"Metrics saved successfully to {file_path}.")


def save_confusion_matrix(confusion_matrix, confusion_matrix_path):
    """Save the confusion matrix to a JSON file."""
    confusion_matrix.to_json(confusion_matrix_path)
    logger.info(f"Confusion matrix saved successfully to {confusion_matrix_path}.")


def set_permissions_of_host_volume_owner(host_uid, host_gid):
    """ pour mettre en place les permissions du propriétaire hôte des volumes 
        - sur chacun des volumes montés dans "/app/"
        - pour tous les dossiers et fichiers dans ces volumes
    """
    if host_uid and host_gid: # si les valeurs sont bien récupérées
        with open('/proc/mounts', 'r') as mounts_file:
            app_mounts = [line.split()[1] for line in mounts_file if line.split()[1].startswith("/app/")]

        for mount_point in app_mounts:
            try:
                subprocess.run(["chown", "-R", f"{host_uid}:{host_gid}", mount_point], check=True)
                logger.info(f"Permissions mises à jour pour {mount_point} avec UID={host_uid} et GID={host_gid}.")
            except subprocess.CalledProcessError as e:
                logger.error(f"Erreur lors de la modification des permissions de {mount_point} : {e}")
    else:
        logger.error("UID ou GID de l'hôte non définis.")


def evaluate(model, X_test, y_test, metrics_dir):
    """Evaluate the model and save the metrics."""    
    logger.info("Evaluating the model...")
    y_pred = model.predict(X_test)   
    metrics = get_metrics(model, X_test, y_test, y_pred)
    save_json_metrics(metrics, metrics_dir)

    # Save the confusion matrix as a JSON file
    confusion_matrix = get_confusion_matrix(y_test, y_pred)
    confusion_matrix_path = os.path.join(metrics_dir, "confusion_matrix.json")
    save_confusion_matrix(confusion_matrix, confusion_matrix_path)
    logger.info("Model evaluation complete. Accuracy: {:.2f}%".format(metrics['accuracy']*100))
    return metrics, confusion_matrix_path
    

def main():
    """Run model prediction, calculate metrics, and save results."""  

    STAGE_NAME = "Stage: eval"   
    try:
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")
        model_path, X_test_path, y_test_path, metrics_dir, host_uid, host_gid = get_env_variables()
                
        # Load the variables and evaluate the model
        model, X_test, y_test = load_variables(model_path, X_test_path, y_test_path)
        evaluate(model, X_test, y_test, metrics_dir)

        # pour mettre en place les permissions du propriétaire hôte des volumes (pour la création de dossier ou de fichiers)
        set_permissions_of_host_volume_owner(host_uid, host_gid)
        logger.info(f">>>>> {STAGE_NAME} / END <<<<<")
    except Exception as e:
        logger.error(f"Erreur lors de l'évaluation du modèle : {traceback.format_exc()}")
        raise e

# Execute main function
if __name__ == "__main__":
    main()