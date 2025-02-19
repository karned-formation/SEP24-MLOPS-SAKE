import base64
from io import BytesIO
import os

import joblib
import requests
from src.custom_logger import logger
import json


from src.utils.env import get_env_var

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


def serialize_object(obj):
    buffer = BytesIO()
    joblib.dump(obj, buffer)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')  # Encode as Base64 string for pydantic

def call_eval(eval_endpoint, X_test, y_test, model):
    headers = {'Content-Type':'application/json'}
    json_payload = {"X_test": serialize_object(X_test),
                    "y_test": serialize_object(y_test),
                    "model": serialize_object(model)}
    return requests.post(eval_endpoint, json=json_payload, headers=headers)

def eval():
    X_test_path = get_env_var("DATA_PREPROCESSING_X_TEST_PATH")
    y_test_path = get_env_var("DATA_PREPROCESSING_Y_TEST_PATH")
    model_path = get_env_var("MODEL_EVAL_MODEL_PATH")
    metrics_dir = get_env_var("MODEL_EVAL_METRICS_DIR")
    model_path = get_env_var("MODEL_TRAIN_MODEL_TRAIN_PATH")
    eval_endpoint = get_env_var("MODEL_EVAL_ENDPOINT_EVAL")

    STAGE_NAME = "Stage: EVAL"
    try:
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")

        response = call_eval(eval_endpoint, joblib.load(X_test_path),joblib.load(y_test_path), joblib.load(model_path))
        json_response = response.json()

        with open(f"{metrics_dir}/scores.json", "w") as f:
            json.dump(json.loads(json_response["scores"]), f)
        
        with open(f"{metrics_dir}/confusion_matrix.json", "w") as f:
            json.dump(json.loads(json_response["confusion_matrix"]), f)
        
        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")

    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e

if __name__ == "__main__":
    eval()