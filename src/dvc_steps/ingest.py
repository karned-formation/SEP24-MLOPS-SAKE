import base64
import requests
from typing import List, Optional
from src.custom_logger import logger
from pathlib import Path
from src.utils.env import get_env_var
import os

def get_new_images_to_ocerize( raw_dataset_dir: Path, ocr_text_dir: Path ):
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

    ocrs_to_delete = [image for image in ocr_images if image not in raw_images]
    images_to_ocerize = [image for image in raw_images if image not in ocr_images]
    return ocrs_to_delete, images_to_ocerize


def ingest_train():
    """
    Fonction d'ingestion pour la pipeline DVC d'entrainement.
    """
    raw_dataset_dir = get_env_var("DATA_STRUCTURE_RAW_RAW_DATASET_DIR")
    ocr_text_dir = get_env_var("DATA_INGESTION_OCR_TEXT_DIR")
    ocr_endpoint = get_env_var("ENDPOINT_URL_EXTRACT")

    STAGE_NAME = "Stage: ingest_all"
    try:
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")

        # On récupère les images qui n'ont pas encore été océrisées
        ocrs_to_delete, new_images = get_new_images_to_ocerize(raw_dataset_dir, ocr_text_dir)
        logger.info(f"{len(new_images)} new image(s) to ocerize")
        
        delete_old_ocr(ocrs_to_delete, ocr_text_dir)

        # On océrise les images et on enregistre le texte dans un fichier .txt dans e répertoire correspondant à son
        # répertoire d'origine
        if(len(new_images)>0):
            to_ocr = []
            for image in new_images:
                with open(f"{raw_dataset_dir}{image}", "rb") as file:
                    to_ocr.append({
                        "name":image,
                        "content": base64.b64encode(file.read()).decode('utf-8')
                    })
            response = get_full_text(to_ocr, ocr_endpoint)
            for text in response.json():
                text_file_path = f"{ocr_text_dir}{text['name']}"
                save_text_to_file(text['text'], text_file_path)

        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")
    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e


def get_full_text( images: List, ocr_endpoint: str ):
    """Envoi une image à l'API d'océrisation et retourne le texte."""
    logger.info(f"Ocerizing...")
    headers = {'Content-Type': 'application/json'}
    response = requests.post(ocr_endpoint, json=images, headers=headers)
    return response
    

def delete_old_ocr( ocr_to_delete: List[str], ocr_path: str ) -> None:
    for file_path in ocr_to_delete:
        # Ensure the path has .txt extension
        txt_path = f"{ocr_path}{file_path}.txt"

        try:
            if os.path.exists(txt_path):
                os.remove(txt_path)
                logger.info(f"{txt_path}: removed.")

        except PermissionError as e:
            logger.error(f"{txt_path}: Permission denied")
        except OSError as e:
            logger.error(f"{txt_path}: {str(e)}")


def ensure_utf8_text( text ):
    if isinstance(text, bytes):
        try:
            # Essaie de décoder en UTF-8
            return text.decode('utf-8')
        except UnicodeDecodeError:
            # Si échec, décode avec un autre encodage puis ré-encode en UTF-8
            return text.decode('latin-1', errors='replace').encode('utf-8').decode('utf-8')
    return text


def save_text_to_file( text: str, path: str ):
    """Enregistre le texte océrisé dans un fichier .txt"""
    logger.info(f"Saving ocr text to {path}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Pour éviter l'erreur "can't decode..." à la lecture du fichier
    text = ensure_utf8_text(text=text)

    with open(path, "w", encoding='utf8') as txt_file:
        txt_file.write(text)

if __name__ == "__main__":
    ingest_train()