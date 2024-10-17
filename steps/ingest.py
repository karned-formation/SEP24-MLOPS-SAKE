import requests
import pandas as pd
import numpy as np
import os
from typing import List
from time import sleep
from custom_logger import logger
from src.config_manager import ConfigurationManager


def get_full_text(image: str, ocr_endpoint: str) -> str:
    """Envoi une image à l'API d'océrisation et retourne le texte."""
    with open(image, "rb") as file:
        files = {"file": file}
        response = requests.post(ocr_endpoint, files=files)
        return response.text


def get_processed_dataset(path_to_dataset: str) -> pd.DataFrame:
    """Récupère ou crée le dataset contenant le texte océrisé"""
    
    if os.path.isfile(path_to_dataset):
        processed_dataset = pd.read_csv(path_to_dataset)
    else:
        columns = [
            'filename', 'grouped_type', 'full_text', 'cleaned_text'
        ]
        processed_dataset = pd.DataFrame(columns=columns, dtype="object")
        processed_dataset.to_csv(path_to_dataset, index=False)
    return processed_dataset


def get_new_images_to_ocerize(raw_dataset: pd.DataFrame, processed_dataset: pd.DataFrame) -> List[str]:
    """Compare les deux fichiers et renvoi seulement les images qui ne sont pas déjà océrisées."""
    
    filenames = np.setdiff1d(raw_dataset["filename"].values, processed_dataset["filename"].values)

    return raw_dataset[raw_dataset["filename"].isin(filenames)]

def save_text_to_file(text:str, path: str):
    """Enregistre le texte océrisé dans un fichier .txt"""
    with open(path, "w") as txt_file:
        txt_file.write(text)


def main():
    try:
        logger.info("Starting the ingest process.")
        config_manager = ConfigurationManager()
        data_ingestion_config = config_manager.get_data_ingestion_config()

        # On récupère le dataset contenant les images brutes
        raw_dataset = pd.read_csv(data_ingestion_config.raw_dataset_path)

        # On récupère le dataset contenant le texte océrisé
        processed_dataset = get_processed_dataset(data_ingestion_config.processed_dataset_path)

        # On supprime les images qui ne sont plus dans le dataset
        processed_dataset = processed_dataset[processed_dataset['filename'].isin(raw_dataset['filename'])]

        # On liste les images qui n'ont pas encore été océrisées
        new_images = get_new_images_to_ocerize(raw_dataset, processed_dataset)

            # Pour chaque image, on récupère le texte et on l'enregistre dans un fichier .txt
        for _, row in new_images.head(10).iterrows():                                              # TODO : remove head(10)
            full_text = get_full_text(f"{data_ingestion_config.image_dir}{row.filename}", data_ingestion_config.ocr_endpoint)

            text_file_path = f"{data_ingestion_config.processed_dir}{row.filename}.txt"
            save_text_to_file(full_text, text_file_path)
            new_images.loc[new_images['filename']==row.filename, 'full_text'] = text_file_path 
    
        # On ajoute les nouvelles images océrisées au dataset   
        processed_dataset = pd.concat([processed_dataset, new_images.head(10)],ignore_index=True)  # TODO : remove head(10)
        processed_dataset.to_csv(data_ingestion_config.processed_dataset_path, index=None)
        logger.info("Ingest process completed.")
    except Exception as e:
        logger.error(f"An error occured during the ingest process: {e}")
        raise e

if __name__ == "__main__":
    main()