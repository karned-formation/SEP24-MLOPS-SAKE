import base64
import os
import shutil
from pathlib import Path
from uuid import uuid4

import requests

from src.s3handler import guess_extension, guess_mime_type, store_objects

def get_env_var( name ):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value


def create_folder_structure():
    uuid = str(uuid4())
    original_raw_path = f'{uuid}/original_raw'
    Path(original_raw_path).mkdir(exist_ok=True, parents=True)
    return uuid, original_raw_path


def delete_folder( folder_path ):
    try:
        shutil.rmtree(folder_path)
        print(f"Le dossier '{folder_path}' a été supprimé avec succès.")
    except FileNotFoundError:
        print(f"Erreur : Le dossier '{folder_path}' n'existe pas.")
    except PermissionError:
        print(f"Erreur : Permission refusée pour supprimer '{folder_path}'.")
    except Exception as e:
        print(f"Erreur inattendue : {e}")


def construct_objects_to_store( objects: list, prefix: str ):
    objects_to_store = []
    for index, file_base64 in enumerate(objects):
        file_content = base64.b64decode(file_base64)
        file_mime_type = guess_mime_type(file_content)
        file_extension = guess_extension(file_mime_type)
        file_name = f"{str(uuid4())}{file_extension}"
        file_name = f"{prefix}/original_raw/{file_name}" if prefix else file_name
        file_old_name = f"{index}"
        file_infos = {
            "file_name": file_name,
            "file_old_name": file_old_name,
            "file_mime_type": file_mime_type,
            "file_extension": file_extension,
            "file_content": file_content
        }
        objects_to_store.append(file_infos)
    return objects_to_store


def call_ingest( uri: str ):
    endpoint_url = (f"http://{get_env_var('DATA_ETL_DOCKER_SERVICE_ETL')}/"
                    f"{get_env_var('DATA_ETL_ROUTE_ETL_INGEST_ALL')}")
    response = requests.post(
        url=endpoint_url,
        params={"uri": f'{uri}/'}
    )
    if response.text:
        raise Exception("Le chemin fourni à ingest est invalide")


def call_clean( uri ):
    endpoint_url = f"http://{get_env_var('DATA_ETL_DOCKER_SERVICE_ETL')}/{get_env_var('DATA_ETL_ROUTE_ETL_CLEAN_ALL')}"  # TODO
    print(endpoint_url)
    response = requests.post(
        url=endpoint_url,
        params={"uri": f'{uri}/'}
    )
    if response.text:
        raise Exception("Le chemin fourni à clean est invalide")


def call_predict( uri ):
    endpoint_url = f"http://{get_env_var('PREDICT_DOCKER_SERVICE_PREDICT')}/{get_env_var('PREDICT_ROUTE_PREDICT')}"
    # TODO
    print(endpoint_url)
    response = requests.post(
        endpoint_url, params={"uri": f'{uri}/'}
    )
    prediction = dict(response.json()).get('data', 0)
    if prediction:
        return prediction
    else:
        raise Exception("Le chemin fourni à predict est invalide")


def treat( files ):
    batch_uuid = str(uuid4())
    objects_to_store = construct_objects_to_store(files, batch_uuid)
    bucket_handler = store_objects(objects_to_store)
    uri = bucket_handler.get_bucket_uri() + batch_uuid
    call_ingest(uri)
    call_clean(uri)
    prediction = call_predict(uri)
    return batch_uuid, prediction
