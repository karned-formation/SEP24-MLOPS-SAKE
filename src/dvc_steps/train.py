import base64
from io import BytesIO
import os
import joblib
import requests
from src.custom_logger import logger

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value

def save_object_locally(encoded_str, path):
    obj_bytes = base64.b64decode(encoded_str)  
    buffer = BytesIO(obj_bytes)  
    obj = joblib.load(buffer)  
    joblib.dump(obj, path) 
 
def serialize_object(obj):
    buffer = BytesIO()
    joblib.dump(obj, buffer)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')  # Encode as Base64 string for pydantic

def call_train(train_endpoint, X_train, y_train):
    headers = {'Content-Type':'application/json'}
    json_payload = {"X_train": serialize_object(X_train),
                    "y_train": serialize_object(y_train)}
    return requests.post(train_endpoint, json=json_payload, headers=headers)
    

def train():
    X_train_path = get_env_var("DATA_PREPROCESSING_X_TRAIN_PATH")
    y_train_path = get_env_var("DATA_PREPROCESSING_Y_TRAIN_PATH")
    train_endpoint = get_env_var("MODEL_TRAIN_ENDPOINT_TRAIN")
    model_path = get_env_var("MODEL_TRAIN_MODEL_TRAIN_PATH")
    STAGE_NAME = "Stage: TRAIN"
    try:
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")

        response = call_train(train_endpoint, joblib.load(X_train_path),joblib.load(y_train_path))
        json_response = response.json()  
        
        save_object_locally(json_response["ovrc"], model_path)

        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")

    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e

if __name__ == "__main__":
    train()