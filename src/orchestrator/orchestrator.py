from pathlib import Path
from typing import List
import os
from datetime import datetime
import requests
from typing import Optional
from src.custom_logger import logger
import pandas as pd
import shutil
from sklearn.feature_extraction.text import TfidfVectorizer
from src.s3handler import S3Handler
from uuid import uuid4



def get_env_var(name):
    """Retrieve environment variables securely."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value


def create_folder_structure():
    # uuid = '86a9a398-713c-42e9-8508-50fc5495856d' 
    uuid = str(uuid4())
    original_raw_path = f'{uuid}/original_raw'

    Path(original_raw_path).mkdir(exist_ok=True, parents=True)

    return uuid, original_raw_path

def delete_folder(folder_path):
    try:
        # Supprime le dossier et tout son contenu
        shutil.rmtree(folder_path)
        print(f"Le dossier '{folder_path}' a été supprimé avec succès.")
    except FileNotFoundError:
        print(f"Erreur : Le dossier '{folder_path}' n'existe pas.")
    except PermissionError:
        print(f"Erreur : Permission refusée pour supprimer '{folder_path}'.")
    except Exception as e:
        print(f"Erreur inattendue : {e}")



def save_images(files):
    """
    Uploads and saves a list of image files to the target folder.
    """
    saved_files = []
    uuid, target_folder = create_folder_structure()

    # Ensure the target folder exists
    Path(target_folder).mkdir(parents=True, exist_ok=True)

    for file in files:
        file_path = target_folder + '/' + file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read()) 

        saved_files.append(str(file_path))
    

    handler = initialize_s3_handler()
    handler.upload_directory(f'{uuid}/', f'{uuid}/')

    delete_folder(uuid)

    return uuid


def initialize_s3_handler():
    """Initialize the S3 handler with environment variables."""
    aws_access_key_id = get_env_var("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_env_var("AWS_SECRET_ACCESS_KEY")
    aws_bucket_name = get_env_var("AWS_BUCKET_NAME")
    logger.info("S3 handler initialized.")
    return S3Handler(aws_bucket_name)


def call_ingest(uuid):
    endpoint_url = f"http://{get_env_var('DATA_ETL_DOCKER_SERVICE_ETL')}/{get_env_var('DATA_ETL_ROUTE_ETL_INGEST_ALL')}" #TODO
    response = requests.post(
    endpoint_url,
    params={"prediction_folder": f'{uuid}/'}
    )
    if response.text:
        raise Exception("Le chemin fourni à ingest est invalide")


def call_clean(uuid):
    endpoint_url = f"http://{get_env_var('DATA_ETL_DOCKER_SERVICE_ETL')}/{get_env_var('DATA_ETL_ROUTE_ETL_CLEAN_ALL')}" # TODO
    print(endpoint_url)
    response = requests.post(
    endpoint_url,
    params={"prediction_folder": f'{uuid}/'}
    )
    if response.text:
        raise Exception("Le chemin fourni à clean est invalide")
    
def call_predict(uuid):
    endpoint_url = f"http://{get_env_var('PREDICT_DOCKER_SERVICE_PREDICT')}/{get_env_var('PREDICT_ROUTE_PREDICT')}" # TODO
    print(endpoint_url)
    response = requests.post(
    endpoint_url,
    params={"prediction_folder": f'{uuid}/'}
    )
    # print(response.json())
    prediction = dict(response.json()).get('data', 0)
    if prediction:
        return prediction
    else:
        raise Exception("Le chemin fourni à predict est invalide")


def main(files):
    uuid = save_images(files)
    
    call_ingest(uuid)
    call_clean(uuid)
    prediction = call_predict(uuid)
    
    return uuid, prediction


if __name__ == "__main__":

    main()
