import io
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
    return response.json()


def call_transform( payload):
    url = get_env_var('ENDPOINT_URL_TRANSFORM')
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        url=url,
        json=payload,
        headers=headers
    )
    return response.json()


def call_load(payload):
    url = get_env_var('ENDPOINT_URL_LOAD')
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        url=url,
        json=payload,
        headers=headers
    )
    return response.json()


def call_predict( payload ):
    url = get_env_var('ENDPOINT_URL_PREDICT')
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        url=url,
        json=payload,
        headers=headers
    )
    return response.json()


from typing import List, Optional

def prepare_payload_original(files: List[dict], names: Optional[List[str]] = None):
    payload = []

    if names:
        if len(names) != len(files):
            raise ValueError("La longueur de 'names' doit être égale à celle de 'files'.")
        for file, name in zip(files, names):
            payload.append({
                "name": name,
                "original_name": file.get("name", name),
                "content": file["content"]
            })
    else:
        for file in files:
            payload.append({
                "name": file.get("name", "unknown_file"),
                "original_name": file.get("name", "unknown_file"),
                "content": file["content"]
            })
    
    return payload



def prepare_extract_payload( files_original: list, files_infos: list ) -> list:
    logging.info(f"Préparation du payload pour l'extraction de texte")
    logging.info(files_original)
    logging.info(files_infos)
    result = []
    for p, f in zip(files_original, files_infos):
        merged = {**p, **f}
        merged.pop('full_path', None)
        merged.pop('name', None)
        merged['name'] = merged.pop('filename')
        result.append(merged)
    return result


def prepare_payload_ocr(files: list) -> list:
    payload = [{"name": file['name'], "content": file['text']} for file in files]
    return payload


def prepare_payload_cleaned(files_infos: list, ocr_files: list) -> list:
    result = []
    for p, f in zip(files_infos, ocr_files):
        merged = {**p, **f}
        merged.pop('full_path', None)
        merged.pop('name', None)
        merged['name'] = merged.pop('filename')
        result.append(merged)
    return result


def construct_dataset( original_files_infos: list, cleaned_files: list ) -> list:
    dataset = []
    for p, f in zip(original_files_infos, cleaned_files):
        merged = {**p, **f}
        merged.pop('full_path', None)
        merged.pop('name', None)
        merged['name'] = merged.pop('filename')
        dataset.append(merged)
    return dataset


def push_original_files_to_bucket( batch_uuid: str, files: list ):
    path_original = f"{batch_uuid}/original_raw"
    files_original = prepare_payload_original(files)
    payload = {
        "prefix": path_original,
        "files": files_original
    }
    return call_load(payload)


def push_ocr_files_to_bucket( batch_uuid: str, files: list ):
    path = f"{batch_uuid}/ocr_raw"
    files = prepare_payload_ocr(files)
    payload = {
        "prefix": path,
        "files": files
    }
    return call_load(payload)


def push_cleaned_files_to_bucket( batch_uuid: str, files: list ):
    path = f"{batch_uuid}/cleaned"
    files = prepare_payload_ocr(files)
    payload = {
        "prefix": path,
        "files": files
    }
    return call_load(payload)


def push_cleaned_dataset_to_bucket( batch_uuid: str, dataset: list ):
    path = f"{batch_uuid}/cleaned"
    df = pd.DataFrame(dataset)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, sep=";")
    csv_str = csv_buffer.getvalue()
    csv_buffer.close()
    files = [{"name": "cleaned.csv", "content": csv_str}]
    payload = {
        "prefix": path,
        "files": files
    }
    return call_load(payload)


def push_prediction_to_bucket( batch_uuid: str, prediction: list ):
    path = f"{batch_uuid}/prediction"
    prediction = json.dumps(prediction)
    files = [{"name": "prediction.json", "content": prediction}]
    payload = {
        "prefix": path,
        "files": files
    }
    return call_load(payload)


def extract_texts( files: list, files_infos: list ) -> list:
    files_original = prepare_payload_original(files)
    files_to_extract = prepare_extract_payload(files_original, files_infos)
    return call_extract(files_to_extract)


def clean_texts( files_infos: list, ocr_files: list ) -> list:
    payload = prepare_payload_cleaned(files_infos, ocr_files)
    return call_transform(payload)


def treat(batch_uuid: str, files: list ):
    logging.info(f"Traitement du batch {batch_uuid}")
    logging.info(f"Nombre de fichiers : {len(files)}")
    logging.info(files)

    original_files_infos = push_original_files_to_bucket(batch_uuid, files)
    ocr_files = extract_texts(files, original_files_infos)
    cleaned_files = clean_texts(original_files_infos, ocr_files)
    dataset = construct_dataset(original_files_infos, cleaned_files)
    prediction = call_predict(dataset)

    push_ocr_files_to_bucket(batch_uuid, ocr_files)
    push_cleaned_files_to_bucket(batch_uuid, cleaned_files)
    push_cleaned_dataset_to_bucket(batch_uuid, dataset)
    push_prediction_to_bucket(batch_uuid, prediction)

    return prediction['model_hash'], prediction['predictions']