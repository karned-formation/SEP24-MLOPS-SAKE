import os
import subprocess
from io import BytesIO, StringIO
from typing import Dict, List, Optional

import pandas as pd
import requests

from src.custom_logger import logger
from src.s3handler import S3Handler, parse_s3_uri


def get_env_var( name ):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value


def load_processed_dataset( filepath: str ) -> pd.DataFrame:
    return pd.read_csv(filepath)


def clean_text( api_url: str, text: str ) -> Optional[str]:
    headers = {'Content-Type': 'text/plain'}
    params = {
        "text": text
    }

    response = requests.post(api_url, params=params, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


def read_file_content( filename: str ) -> str:
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def make_dataset( ocr_txts: List[str], cleaned_txts: List[str] ) -> pd.DataFrame:
    return pd.DataFrame(
        {
            'filename': [ocr_txt.replace('.txt', '') for ocr_txt in ocr_txts], 'cleaned_text': cleaned_txts,
            'category': [ocr_txt.split('/')[0] for ocr_txt in ocr_txts]
        }
    )


def check_input_dir( ocr_text_dir ):
    if not os.path.exists(ocr_text_dir):
        raise Exception("OCR text directory not found")


def get_ocr_text_files( root: str, ocr_text_dir: str, files: list ) -> list:
    return [os.path.relpath(os.path.join(root, file), ocr_text_dir) for file in files if file.endswith('.txt')]


def clean_ocr_files( api_url: str, ocr_text_dir: str, ocr_text_files: list ) -> list:
    cleaned_texts = []
    for file in ocr_text_files:
        file_content = read_file_content(os.path.join(ocr_text_dir, file))
        cleaned_text = clean_text(api_url, file_content)
        cleaned_texts.append(cleaned_text)
    return cleaned_texts


def save_cleaned_dataset_for_dir(
        root: str, ocr_text_files: list, cleaned_texts: list, cleaned_datasets_dir: str
) -> None:
    logger.info(f"Creating cleaned dataset for directory: {root}")
    dataset = make_dataset(ocr_text_files, cleaned_texts)
    class_folder = os.path.basename(os.path.dirname(ocr_text_files[0]))
    output_path = os.path.join(cleaned_datasets_dir, class_folder, "cleaned_dataset.csv")
    save_cleaned_dataset(dataset, output_path)


def read_app_mounts():
    app_mounts = []
    try:
        with open('/proc/mounts', 'r') as mounts_file:
            app_mounts = [line.split()[1] for line in mounts_file if line.split()[1].startswith("/app/")]
    except Exception as e:
        logger.error(f"Erreur lors de la lecture des points de montage : {e}")
    return app_mounts


def validate_host_uid_gid( host_uid, host_gid ):
    if not host_uid or not host_gid:
        logger.error("UID ou GID de l'hôte non définis.")
        raise Exception("UID ou GID de l'hôte non définis.")


def update_permissions( mount_point, host_uid, host_gid ):
    try:
        subprocess.run(["chown", "-R", f"{host_uid}:{host_gid}", mount_point], check=True)
        logger.info(f"Permissions mises à jour pour {mount_point} avec UID={host_uid} et GID={host_gid}.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la modification des permissions de {mount_point} : {e}")


def set_permissions_of_host_volume_owner( host_uid, host_gid ):
    validate_host_uid_gid(host_uid, host_gid)
    app_mounts = read_app_mounts()
    for mount_point in app_mounts:
        update_permissions(mount_point, host_uid, host_gid)


def process_dir(
        ocr_text_dir: str, cleaned_datasets_dir: str, api_url: str, host_uid, host_gid
) -> None:
    check_input_dir(ocr_text_dir)

    for root, _, files in os.walk(ocr_text_dir):
        logger.info(f"Processing directory: {root}")

        ocr_text_files = get_ocr_text_files(root, ocr_text_dir, files)
        if not ocr_text_files:
            logger.info(f"No text files found in {root}. Skipping...")
            continue

        cleaned_texts = clean_ocr_files(api_url, ocr_text_dir, ocr_text_files)
        save_cleaned_dataset_for_dir(root, ocr_text_files, cleaned_texts, cleaned_datasets_dir)

    set_permissions_of_host_volume_owner(host_uid, host_gid)


def encode_labels( ocr_txts: List[str], mapper: Dict[str, int] ) -> List[int]:
    labels = []
    for ocr_txt in ocr_txts:
        category = ocr_txt.split('/')[0]
        label = mapper.get(category, -1)  # Default to -1 if category not found
        labels.append(label)
    return labels


def save_cleaned_dataset( cleaned_dataset: pd.DataFrame, filepath: str ) -> None:
    logger.info(f"Saving current class to {filepath}...")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    cleaned_dataset.to_csv(filepath, index=False)


def clean_train():
    ocr_text_dir = get_env_var("DATA_INGESTION_OCR_TEXT_DIR")
    clean_endpoint = get_env_var("DATA_CLEANING_CLEAN_ENDPOINT")
    cleaned_datasets_dir = get_env_var("DATA_CLEANING_CLEANED_DATASETS_DIR")
    host_uid = get_env_var("HOST_UID")
    host_gid = get_env_var("HOST_GID")

    STAGE_NAME = "Stage: clean_all"
    try:
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")
        process_dir(ocr_text_dir, cleaned_datasets_dir, clean_endpoint, host_uid, host_gid)
        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")
    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e


def make_dataset_prediction( ocr_txts: List[str], cleaned_txts: List[str] ) -> pd.DataFrame:
    return pd.DataFrame(
        {
            'filename': [ocr_txt.replace('.txt', '') for ocr_txt in ocr_txts], 'cleaned_text': cleaned_txts
        }
    )


def clean_prediction( uri: str ):
    """ 
    Dans le dossier S3 fourni, on récupère les textes de ocr_raw/, on les océrise et on place le résultat (fichier
    csv) dans cleaned/
    """
    try:
        logger.info(f">>>>> CLEAN PREDICTION/ START <<<<<")

        clean_endpoint = get_env_var("DATA_CLEANING_CLEAN_ENDPOINT")
        ocr_dir = get_env_var("BUCKET_OCR_SUBDIR")
        cleaned_dir = get_env_var("BUCKET_CLEANED_SUBDIR")

        bucket_name, base_prefix = parse_s3_uri(uri)
        handler = S3Handler(bucket_name)
        prefix = f"{base_prefix}{ocr_dir}"

        object_keys = handler.list_objects(prefix)
        if not object_keys:
            raise Exception(f"Le dossier fourni n'existe pas sur le bucket. ({prefix})")

        logger.info(f"{len(object_keys)} image(s) to clean")
        ocr_texts = []
        cleaned_txts = []

        for key in object_keys:
            ocr_texts.append(uri + key)
            file_content = handler.download_object_to_content(key)
            file_content = file_content.getvalue().decode('utf-8')

            cleaned_text = clean_text(clean_endpoint, file_content)
            cleaned_txts.append(cleaned_text)

        dataset = make_dataset_prediction(ocr_texts, cleaned_txts)
        csv_buffer = StringIO()
        dataset.to_csv(csv_buffer, index=False)

        csv_file_content = BytesIO(csv_buffer.getvalue().encode('utf-8'))
        text_key = f"{base_prefix}{cleaned_dir}/cleaned.csv"
        handler.upload_object_from_content(csv_file_content, text_key)

        logger.info(f">>>>> CLEAN PREDICTION / END successfully <<<<<")

    except Exception as e:
        logger.error(f"CLEAN PREDICTION / An error occurred : {str(e)}")
        raise e


if __name__ == '__main__':
    clean_train()  # Pour tester, le bucket contient quelques données de test  # clean_prediction(
    # remote_directory_name="prediction_1731849628.762522/")
