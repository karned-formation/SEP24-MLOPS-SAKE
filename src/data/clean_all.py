import pandas as pd
import requests
import os
import subprocess
from typing import Optional, List, Dict
from src.custom_logger import logger

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value

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

def check_input_dir(ocr_text_dir):
    if not os.path.exists(ocr_text_dir):
        raise Exception("OCR text directory not found")

def process_dir(ocr_text_dir: str, cleaned_datasets_dir: str, api_url: str,
                host_uid, host_gid) -> None:
    check_input_dir(ocr_text_dir)
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
    set_permissions_of_host_volume_owner(host_uid, host_gid)

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

def clean_all():

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

if __name__ == '__main__':
    clean_all()