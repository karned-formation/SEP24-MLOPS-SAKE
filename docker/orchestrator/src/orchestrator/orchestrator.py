import json
import logging
from uuid import uuid4
import pandas as pd
import requests
from typing import List, Optional
from src.utils.env import get_env_var


def call_extract( payload ):
    url = get_env_var('ENDPOINT_URL_EXTRACT')
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        url=url,
        json=payload,
        headers=headers
    )
    return response.text


def call_transform( uri ):
    url = get_env_var('ENDPOINT_URL_TRANSFORM')
    response = requests.post(
        url=url,
        params={"uri": f'{uri}/'}
    )


def call_load( prefix: str, files: list ):
    url = get_env_var('ENDPOINT_URL_LOAD')
    payload = {
        "prefix": prefix,
        "files": files
    }
    response = requests.post(
        url=url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    return response.json()


def call_predict( uri_csv: str ):
    url = f"http://{get_env_var('PREDICT_DOCKER_SERVICE_PREDICT')}/{get_env_var('PREDICT_ROUTE_PREDICT')}"
    payload = prepare_predict_payload(uri_csv)
    response = requests.post(
        url=url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    logging.info(response.text)
    prediction = dict(response.json()).get('data', 0)
    if prediction:
        return prediction
    else:
        raise Exception("Le chemin fourni à predict est invalide")


def prepare_load_payload_original(files: List[bytes], names: Optional[List[str]] = None):
    if names:
        if len(names) != len(files):
            raise ValueError("La longueur de 'names' doit être égale à celle de 'files'.")
        payload = [{"name": name, "content": file} for name, file in zip(names, files)]
    else:
        payload = [{"content": file} for file in files]
    return payload


def prepare_extract_payload( files_original: list, files_infos: list ) -> list:
    result = []
    for p, f in zip(files_original, files_infos):
        merged = {**p, **f}
        merged.pop('full_path', None)
        merged.pop('name', None)
        merged['name'] = merged.pop('filename')
        result.append(merged)
    return result


def prepare_load_payload_ocerized(files: str) -> list:
    files = json.loads(files)
    payload = [{"name": file['name'], "content": file['text']} for file in files]
    return payload


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


def push_original_files_to_bucket( batch_uuid: str, files: list ):
    path_original = f"{batch_uuid}/original_raw"
    files_original = prepare_load_payload_original(files)
    return call_load(path_original, files_original)


def push_ocerized_files_to_bucket( batch_uuid: str, files: str ):
    path = f"{batch_uuid}/ocerized_raw"
    files = prepare_load_payload_ocerized(files)
    return call_load(path, files)


def extract_texts( files: list, files_infos: list ) -> str:
    files_original = prepare_load_payload_original(files)
    files_to_extract = prepare_extract_payload(files_original, files_infos)
    return call_extract(files_to_extract)


def treat( files: list ):
    batch_uuid = str(uuid4())
    batch_uuid = 'test1'

    files_infos = push_original_files_to_bucket(batch_uuid, files)

    ocerized_files = extract_texts(files, files_infos)
    files_infos = push_ocerized_files_to_bucket(batch_uuid, ocerized_files)

    cleaned_files = clean_texts(files, files_infos)
    """
    call_transform(base_uri)

    uri_csv = f'{base_uri}cleaned/cleaned.csv'
    prediction = call_predict(uri_csv)

    uri_csv_prediction = f'{base_uri}/prediction/predictions.csv'
    store_csv_prediction(prediction, uri_csv_prediction)

    uri_json_prediction = f'{base_uri}/prediction/predictions.json'
    store_json_prediction(prediction, uri_json_prediction)
    """
    prediction = {"WIP": "WIP"}
    return batch_uuid, prediction

