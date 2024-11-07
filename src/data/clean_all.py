import pandas as pd
import requests
import os
import subprocess
from typing import Optional, List, Dict
from custom_logger import logger


def load_processed_dataset(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

def clean_text(api_url: str, text: str) -> Optional[str]:
    headers = {'Content-Type': 'text/plain'}
    params = {
        "text": text
    }

    response = requests.post(api_url, params=params, headers=headers)
    if response.status_code == 200:
        return response.text
    return None

def read_file_content(filename: str) -> str:
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()
            
def make_dataset(ocr_txts: List[str], cleaned_txts: List[str]) -> pd.DataFrame:
    return pd.DataFrame({
        'filename': [ocr_txt.replace('.txt', '') for ocr_txt in ocr_txts],
        'cleaned_text': cleaned_txts,
        'category': [ocr_txt.split('/')[0] for ocr_txt in ocr_txts]
    })

def process_dir(ocr_text_dir: str, cleaned_datasets_dir: str, api_url: str) -> None:
    for root, _, files in os.walk(ocr_text_dir):
        logger.info(f"Cleaning directory {root}")
        ocr_images = []
        for file in files:
            if file.endswith('.txt'):
                relative_path = os.path.relpath(os.path.join(root, file), ocr_text_dir)
                ocr_images.append(relative_path)
       
        if(len(ocr_images) == 0): # Skip if no txt files found
            continue

        cleaned_txts =[]
        for image in ocr_images:
            file_content = read_file_content(os.path.join(ocr_text_dir, image))
            cleaned_text = clean_text(api_url, file_content)
            cleaned_txts.append(cleaned_text)

        logger.info(f"Creating cleaned dataset for {root}")
        dataset = make_dataset(ocr_images, cleaned_txts)
        class_folder = os.path.basename(os.path.dirname(ocr_images[0]))
        save_cleaned_dataset(dataset, f"{cleaned_datasets_dir}{class_folder}/cleaned_dataset.csv")


def encode_labels(ocr_txts: List[str], mapper: Dict[str, int]) -> List[int]:
    labels = []
    for ocr_txt in ocr_txts:
        category = ocr_txt.split('/')[0]
        label = mapper.get(category, -1)  # Default to -1 if category not found
        labels.append(label)
    return labels

def save_cleaned_dataset(cleaned_dataset: pd.DataFrame, filepath: str) -> None:
    """Enregistre la classe en cours dans un fichier .csv"""
    logger.info(f"Saving current class to {filepath}...")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    cleaned_dataset.to_csv(filepath, index=False)


def clean_all(clean_endpoint: str, ocr_text_dir: str, cleaned_datasets_dir: str) -> None:

    try:        
        logger.info("Starting the cleaning process...")
        process_dir(ocr_text_dir, cleaned_datasets_dir, clean_endpoint)      
        logger.info("Cleaning process completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during the cleaning process: {str(e)}")
        raise e

    # pour mettre en place les permissions du propriétaire hôte des volumes (pour la création de dossier ou de fichiers)
    host_uid = os.getenv("HOST_UID")
    host_gid = os.getenv("HOST_GID")
    if host_uid and host_gid: # si les valeurs sont bien récupérées
        with open('/proc/mounts', 'r') as mounts_file:
            app_mounts = [line.split()[1] for line in mounts_file if line.split()[1].startswith("/app/")]

        for mount_point in app_mounts:
            try:
                subprocess.run(["chown", "-R", f"{host_uid}:{host_gid}", mount_point], check=True)
                logger.info(f"Permissions mises à jour pour {mount_point} avec UID={host_uid} et GID={host_gid}.")
            except subprocess.CalledProcessError as e:
                logger.info(f"Erreur lors de la modification des permissions de {mount_point} : {e}")
    else:
        logger.info("UID ou GID de l'hôte non définis.")


if __name__ == '__main__':
    ocr_text_dir = os.getenv("DATA_INGESTION_OCR_TEXT_DIR")
    clean_endpoint = os.getenv("DATA_CLEANING_CLEAN_ENDPOINT")
    cleaned_datasets_dir = os.getenv("DATA_CLEANING_CLEANED_DATASETS_DIR")

    clean_all(clean_endpoint, ocr_text_dir, cleaned_datasets_dir)