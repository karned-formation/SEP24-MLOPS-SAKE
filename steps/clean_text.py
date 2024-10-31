import pandas as pd
import requests
import os
import sys
from typing import Optional, List, Dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.custom_logger import logger
from src.config_manager import ConfigurationManager
from src.entity import LabelEncodingConfig

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
            
def make_dataset(ocr_txts: List[str], cleaned_txts: List[str], mapper: Dict[str, int]) -> pd.DataFrame:
    return pd.DataFrame({
        'filename': [ocr_txt.replace('.txt', '') for ocr_txt in ocr_txts],
        'cleaned_text': cleaned_txts,
        'category': encode_labels(ocr_txts, mapper)
    })

def process_dir(ocr_text_dir: str, cleaned_datasets_dir: str, api_url: str,mapper: Dict[str, int]) -> None:
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
        dataset = make_dataset(ocr_images, cleaned_txts, mapper)
        class_folder = os.path.basename(os.path.dirname(ocr_images[0]))
        os.makedirs(f"{cleaned_datasets_dir}{class_folder}", exist_ok=True)

        dataset_path = f"{cleaned_datasets_dir}{class_folder}/cleaned_dataset.csv"
        dataset.to_csv(dataset_path, index=False)
        logger.info(f"Dataset saved to {dataset_path}")


def encode_labels(ocr_txts: List[str], mapper: Dict[str, int]) -> List[int]:
    labels = []
    for ocr_txt in ocr_txts:
        category = ocr_txt.split('/')[0]
        label = mapper.get(category, -1)  # Default to -1 if category not found
        labels.append(label)
    return labels

def save_cleaned_dataset(cleaned_dataset: pd.DataFrame, filepath: str) -> None:
    cleaned_dataset.to_csv(filepath, index=False)


def main():
    try:
        
        logger.info("Starting the cleaning process...")
        config_manager = ConfigurationManager()
        data_cleaning_config = config_manager.get_data_cleaning_config()
        label_encoding_config = config_manager.get_label_encoding_config()
        process_dir(data_cleaning_config.ocr_text_dir, data_cleaning_config.cleaned_datasets_dir, data_cleaning_config.clean_endpoint, label_encoding_config.__dict__)      
        logger.info("Cleaning process completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during the cleaning process: {str(e)}")
        raise e

if __name__ == '__main__':
    main()