import requests
import pandas as pd
import numpy as np
import os
from typing import List
from src.data.check_structure import check_existing_file, check_existing_folder

ocr_endpoint = "http://localhost:8901/txt/blocks-words" # url de l'OCR 
data_path = "data/" # chemin du dossier data


def get_full_text(image: str) -> str:
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
            'filename', 'new_type', 'original_type', 'motif_rejet', 'true_cat',
            'inclusion_dataset', 'excluded_types', 'grouped_type', 'full_text', 'cleaned_text'
        ]
        processed_dataset = pd.DataFrame(columns=columns, dtype="object")
        processed_dataset.to_csv(path_to_dataset, index=False)
    return processed_dataset


def get_new_images_to_ocerize(raw_dataset: pd.DataFrame, processed_dataset: pd.DataFrame) -> List[str]:
    """Compare les deux fichiers et renvoi seulement les images qui ne sont pas déjà océrisées."""

    # TODO: supprimer les images qui sont dans processed_dataset.csv et ne sont plus dans dataset.csv
    
    filenames = np.setdiff1d(raw_dataset["filename"].values, processed_dataset["filename"].values)

    return raw_dataset[raw_dataset["filename"].isin(filenames)]

def save_text_to_file(text:str, path: str):
    """Enregistre le texte océrisé dans un fichier .txt"""
    with open(path, "w") as txt_file:
        txt_file.write(text)


def main():

    output_folderpath = "data/processed/"

    # Crate folder if needed
    if check_existing_folder(output_folderpath):
        os.makedirs(output_folderpath)

    path_to_dataset = f"{data_path}/processed/processed_dataset.csv" 
    raw_dataset = pd.read_csv(f"{data_path}dataset.csv")

    processed_dataset = get_processed_dataset(path_to_dataset)

    new_images = get_new_images_to_ocerize(raw_dataset, processed_dataset)

    for _, row in new_images.head(10).iterrows():                                               # TODO : Attention j'ai mis head(10) pour tester, à enlever
        full_text = get_full_text(f"{data_path}raw/final/{row.filename}")

        text_file_path = f"{data_path}/processed/{row.filename}.txt"
        save_text_to_file(full_text, text_file_path)
        new_images.loc[new_images['filename']==row.filename, 'full_text'] = text_file_path 
   
    processed_dataset = pd.concat([processed_dataset, new_images.head(10)],ignore_index=True)   # TODO : Attention j'ai mis head(10) pour tester, à enlever
    processed_dataset.to_csv(path_to_dataset, index=None)

if __name__ == "__main__":
    main()