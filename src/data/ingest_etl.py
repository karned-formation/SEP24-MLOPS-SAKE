from pathlib import Path
import requests
import os
import subprocess
from typing import List
from custom_logger import logger
from s3handler import S3Handler
from fastapi import HTTPException

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value

def get_full_text(image: str, ocr_endpoint: str) -> str:
    """Envoi une image à l'API d'océrisation et retourne le texte."""
    logger.info(f"Ocerizing {image}...")
    with open(image, "rb") as file:
        files = {"file": file}
        response = requests.post(ocr_endpoint, files=files)
        return response.text

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

def get_new_images_to_ocerize(raw_dataset_dir: Path, ocr_text_dir: Path) -> List[str]:
    """
    Compare les arborescences et renvoie seulement les images qui ne sont pas déjà océrisées.
    """
    raw_images = []
    for root, _, files in os.walk(raw_dataset_dir):
        logger.info(f"Ocerizing directory {root}")
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')):
                relative_path = os.path.relpath(os.path.join(root, file), raw_dataset_dir)
                raw_images.append(relative_path)

    ocr_images = []
    for root, _, files in os.walk(ocr_text_dir):
        logger.info(f"Checking: {root}")
        for file in files:
            if file.endswith('.txt'):
                relative_path = os.path.relpath(os.path.join(root, file), ocr_text_dir)
                ocr_images.append(relative_path.replace(".txt", ""))

    return [image for image in raw_images if image not in ocr_images]

def ensure_utf8_text(text):
    if isinstance(text, bytes):
        try:
            # Essaie de décoder en UTF-8
            return text.decode('utf-8')
        except UnicodeDecodeError:
            # Si échec, décode avec un autre encodage puis ré-encode en UTF-8
            return text.decode('latin-1', errors='replace').encode('utf-8').decode('utf-8')
    return text

def save_text_to_file(text:str, path: str):
    """Enregistre le texte océrisé dans un fichier .txt"""
    logger.info(f"Saving ocr text to {path}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Pour éviter l'erreur "can't decode..." à la lecture du fichier
    text = ensure_utf8_text(text=text)

    with open(path, "w", encoding='utf8') as txt_file:
        txt_file.write(text)

def ingest_train():
    """
    Fonction d'ingestion pour la pipeline DVC d'entrainement.
    """
    raw_dataset_dir = get_env_var("DATA_STRUCTURE_RAW_RAW_DATASET_DIR")
    ocr_text_dir = get_env_var("DATA_INGESTION_OCR_TEXT_DIR")
    ocr_endpoint = get_env_var("DATA_INGESTION_OCR_ENDPOINT")
    host_uid = get_env_var("HOST_UID")
    host_gid = get_env_var("HOST_GID")

    STAGE_NAME = "Stage: ingest_all"    
    try:        
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")
        
        # On récupère les images qui n'ont pas encore été océrisées
        images_to_ocerize = get_new_images_to_ocerize(raw_dataset_dir, ocr_text_dir)
        logger.info(f"{len(images_to_ocerize)} new image(s) to ocerize")

        # On océrise les images et on enregistre le texte dans un fichier .txt dans e répertoire correspondant à son répertoire d'origine
        for image in images_to_ocerize:
            full_text = get_full_text(f"{raw_dataset_dir}{image}", ocr_endpoint)
            text_file_path = f"{ocr_text_dir}{image}.txt"
            save_text_to_file(full_text, text_file_path)

        set_permissions_of_host_volume_owner(host_uid, host_gid)

        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")
    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e
    
def ingest_prediction(remote_directory_name: str):
    """ 
    Dans le dossier S3 fourni, on récupère les images de original_raw/, on les océrise et on place les résultats (fichiers textes) dans ocerized_raw/
    """
    try:       
        logger.info(f">>>>> OCERIZE / START <<<<<")

        bucket_name = get_env_var('AWS_BUCKET_NAME')
        ocr_endpoint = get_env_var("DATA_INGESTION_OCR_ENDPOINT")
        ocr_dir = get_env_var("PREDICT_OCR_DIR")
        original_dir = get_env_var("PREDICT_ORIGINAL_DIR")
        
        # Initialisation de la connexion au bucket              
        handler = S3Handler(bucket_name)
        
        # On vérifie que le dossier est bien créé et qu'il contient original_raw/
        if not handler.folder_exists(f"{remote_directory_name}{original_dir}"):
            raise HTTPException(status_code=404, detail="Le dossier fourni n'existe pas sur le bucket.")

        # On télécharge le dossier en local
        raw_images = handler.download_directory(remote_directory_name=f"{remote_directory_name}{original_dir}")
        logger.info(f"{len(raw_images)} image(s) to ocerize")

        # On océrise chaque image et on stocke le résultat dans ocerized_raw/
        for image in raw_images:
            full_text = get_full_text(image, ocr_endpoint)
            text_file_path = f"{remote_directory_name}{ocr_dir}{image.split('/')[-1]}.txt"
            save_text_to_file(full_text, text_file_path)

        # On upload le dossier ocerized_raw vers le bucket s3
        handler.upload_directory(f"{remote_directory_name}{ocr_dir}", f"{remote_directory_name}{ocr_dir}")
        logger.info(f">>>>> OCERIZE / END successfully <<<<<")

    except Exception as e:
        logger.error(f"OCERIZE / An error occurred : {str(e)}")
        raise e

if __name__ == '__main__':
    ingest_train()

    # Pour tester l'ingestion de prédiction, le bucket contient quelques données de test
    # ingest_prediction(remote_directory_name="prediction_1731849628.762522/")