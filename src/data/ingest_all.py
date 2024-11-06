from pathlib import Path
import requests
import os
import subprocess
from typing import List
import sys
from custom_logger import logger


def get_full_text(image: str, ocr_endpoint: str) -> str:
    """Envoi une image à l'API d'océrisation et retourne le texte."""
    logger.info(f"Ocerizing {image}...")
    with open(image, "rb") as file:
        files = {"file": file}
        response = requests.post(ocr_endpoint, files=files)
        return response.text

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



def save_text_to_file(text:str, path: str):
    """Enregistre le texte océrisé dans un fichier .txt"""
    logger.info(f"Saving ocr text to {path}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding='utf8') as txt_file:
        txt_file.write(text)


def ingest_all(ocr_endpoint: str, raw_dataset_dir: str, ocr_text_dir: str):
    try:
        logger.info("Starting the ingest process...")
        
        # On récupère les images qui n'ont pas encore été océrisées
        images_to_ocerize = get_new_images_to_ocerize(raw_dataset_dir, ocr_text_dir)
        logger.info(f"{len(images_to_ocerize)} new image(s) to ocerize")

        # On océrise les images et on enregistre le texte dans un fichier .txt dans e répertoire correspondant à son répertoire d'origine
        for image in images_to_ocerize:
            full_text = get_full_text(f"{raw_dataset_dir}{image}", ocr_endpoint)
            text_file_path = f"{ocr_text_dir}{image}.txt"
            save_text_to_file(full_text, text_file_path)
       
        logger.info("Ingest process completed.")
    except Exception as e:
        logger.error(f"An error occured during the ingest process: {e}")
        raise e

    # pour mettre en place les permissions du propriétaire hôte des volumes (pour la création de dossier ou de fichiers)
    host_uid = os.getenv("UID")
    host_gid = os.getenv("GID")
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
    raw_dataset_dir = os.getenv("DATA_STRUCTURE_RAW_RAW_DATASET_DIR")
    ocr_text_dir = os.getenv("DATA_INGESTION_OCR_TEXT_DIR")
    ocr_endpoint = os.getenv("DATA_INGESTION_OCR_ENDPOINT")

    ingest_all(ocr_endpoint, raw_dataset_dir, ocr_text_dir)