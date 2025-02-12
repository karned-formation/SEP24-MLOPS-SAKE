import base64
import logging
from uuid import uuid4
import pandas as pd
import requests
from typing import List, Optional
from src.utils.env import get_env_var


def call_extract( uri: str ):
    url = (get_env_var('ENDPOINT_URL_EXTRACT'))
    response = requests.post(
        url=url,
        params={"uri": f'{uri}/'}
    )


def call_transform( uri ):
    url = (get_env_var('ENDPOINT_URL_TRANSFORM'))
    response = requests.post(
        url=url,
        params={"uri": f'{uri}/'}
    )


def prepare_load_payload(files: List[bytes], names: Optional[List[str]] = None):
    if names:
        if len(names) != len(files):
            raise ValueError("La longueur de 'names' doit être égale à celle de 'files'.")
        payload = [{"name": name, "content": file} for name, file in zip(names, files)]
    else:
        payload = [{"content": file} for file in files]
    return payload


def call_load( prefix: str, files: list ):
    url = (get_env_var('ENDPOINT_URL_LOAD'))
    for file in files:
        payload = {
            "prefix": prefix,
            "files": files
        }
        response = requests.post(
            url=url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )


def prepare_predict_payload( uri_csv ):
    csv_content = download_uri_to_content(uri_csv)
    df = pd.read_csv(csv_content)

    payload = []
    for _, row in df.iterrows():
        payload.append(
            {
                "ref": str(row['filename']),
                "data": str(row['cleaned_text'])
            }
        )

    return payload


def call_predict( uri_csv: str ):
    endpoint_url = f"http://{get_env_var('PREDICT_DOCKER_SERVICE_PREDICT')}/{get_env_var('PREDICT_ROUTE_PREDICT')}"
    payload = prepare_predict_payload(uri_csv)
    response = requests.post(
        url=endpoint_url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    logging.info(response.text)
    prediction = dict(response.json()).get('data', 0)
    if prediction:
        return prediction
    else:
        raise Exception("Le chemin fourni à predict est invalide")


def store_json_prediction( prediction: str, uri_json_prediction: str ):
    pass


def store_csv_prediction( prediction: str, uri_csv_prediction: str ):
    pass


def treat( files ):
    batch_uuid = str(uuid4())

    path_original = f"{batch_uuid}/original_raw"
    files_original = prepare_load_payload(files)
    call_load(path_original, files_original)

    """
    call_extract(base_uri)

    call_transform(base_uri)

    uri_csv = f'{base_uri}cleaned/cleaned.csv'
    prediction = call_predict(uri_csv)

    uri_csv_prediction = f'{base_uri}/prediction/predictions.csv'
    store_csv_prediction(prediction, uri_csv_prediction)

    uri_json_prediction = f'{base_uri}/prediction/predictions.json'
    store_json_prediction(prediction, uri_json_prediction)

    return batch_uuid, prediction
    """
