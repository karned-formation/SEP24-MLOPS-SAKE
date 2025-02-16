import os
import subprocess
from io import BytesIO, StringIO
from typing import Dict, List, Optional
import pandas as pd
import requests

from src.custom_logger import logger
from src.utils.env import get_env_var


def clean_train():
    ocr_text_dir = get_env_var("DATA_INGESTION_OCR_TEXT_DIR")
    clean_endpoint = get_env_var("DATA_CLEANING_CLEAN_ENDPOINT")
    cleaned_datasets_dir = get_env_var("DATA_CLEANING_CLEANED_DATASETS_DIR")

    STAGE_NAME = "Stage: clean_all"
    try:
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")
        process_dir(ocr_text_dir, cleaned_datasets_dir, clean_endpoint)
        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")
    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e
    
def clean_text(api_url: str, text: str) -> Optional[str]:
    headers = {'Content-Type': 'application/json'}
    json_payload = {"text": text}

    response = requests.post(api_url, json=json_payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return response.text
    return None


def process_dir(
        ocr_text_dir: str, cleaned_datasets_dir: str, api_url: str
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

def read_file_content( filename: str ) -> str:
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()
    
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

def save_cleaned_dataset( cleaned_dataset: pd.DataFrame, filepath: str ) -> None:
    logger.info(f"Saving current class to {filepath}...")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    cleaned_dataset.to_csv(filepath, index=False)

def make_dataset( ocr_txts: List[str], cleaned_txts: List[str] ) -> pd.DataFrame:
    return pd.DataFrame(
        {
            'filename': [ocr_txt.replace('.txt', '') for ocr_txt in ocr_txts], 'cleaned_text': cleaned_txts,
            'category': [ocr_txt.split('/')[0] for ocr_txt in ocr_txts]
        }
    )

def get_ocr_text_files( root: str, ocr_text_dir: str, files: list ) -> list:
    return [os.path.relpath(os.path.join(root, file), ocr_text_dir) for file in files if file.endswith('.txt')]

def check_input_dir( ocr_text_dir ):
    if not os.path.exists(ocr_text_dir):
        raise Exception("OCR text directory not found")
    

if __name__ == "__main__":
    clean_train()