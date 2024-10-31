from pathlib import Path
import requests
import pandas as pd
import numpy as np
import os
from typing import List
from time import sleep
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.custom_logger import logger
from src.config_manager import ConfigurationManager

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
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')):
                relative_path = os.path.relpath(os.path.join(root, file), raw_dataset_dir)
                raw_images.append(relative_path)

    ocr_images = []
    for root, _, files in os.walk(ocr_text_dir):

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


def main():
    try:
        logger.info("Starting the ingest process...")
        config_manager = ConfigurationManager()
        data_ingestion_config = config_manager.get_data_ingestion_config()

        # On récupère les chemins des répertoires
        raw_dataset_dir = data_ingestion_config.raw_dataset_dir
        ocr_text_dir = data_ingestion_config.ocr_text_dir

        # On récupère les images qui n'ont pas encore été océrisées
        images_to_ocerize = get_new_images_to_ocerize(raw_dataset_dir, ocr_text_dir)
        logger.info(f"{len(images_to_ocerize)} new image(s) to ocerize")

        # On océrise les images et on enregistre le texte dans un fichier .txt dans e répertoire correspondant à son répertoire d'origine
        for image in images_to_ocerize:
            full_text = get_full_text(f"{raw_dataset_dir}{image}", data_ingestion_config.ocr_endpoint)
            text_file_path = f"{ocr_text_dir}{image}.txt"
            save_text_to_file(full_text, text_file_path)
       
        logger.info("Ingest process completed.")
    except Exception as e:
        logger.error(f"An error occured during the ingest process: {e}")
        raise e

if __name__ == "__main__":
    main()