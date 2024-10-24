import pandas as pd
import requests
import os
from typing import Optional
from custom_logger import logger
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
            
def process_dataset(processed_dataset: pd.DataFrame, api_url: str) -> pd.DataFrame:
    filenames = []
    cleaned_texts = []
    categories = []

    for index, row in processed_dataset.iterrows():
        file_content = read_file_content(row['full_text'])
        cleaned_text = clean_text(api_url, file_content)
        filenames.append(row['filename'])
        cleaned_texts.append(cleaned_text)
        categories.append(row['grouped_type'])

    return pd.DataFrame({
        'filename': filenames,
        'cleaned_text': cleaned_texts,
        'category': categories
    })

def encode_labels(clean_dataset: pd.DataFrame, mapper: LabelEncodingConfig) -> pd.DataFrame:
    clean_dataset['category'] = clean_dataset['category'].map(mapper.__dict__)
    return clean_dataset


def save_cleaned_dataset(cleaned_dataset: pd.DataFrame, filepath: str) -> None:
    cleaned_dataset.to_csv(filepath, index=False)


def main():
    """
    Main function to clean the processed dataset and save the cleaned dataset.
    This function performs the following steps:
    1. Creates the output folder if it does not exist.
    2. Loads the processed dataset from a specified path.
    3. Sends the processed dataset to an API for cleaning.
    4. Saves the cleaned dataset to a specified path.
    
    Variables:
    - config_manager: ConfigurationManager object to get the data cleaning configuration.
    
    Functions:
    - check_existing_folder(folderpath): Checks if the folder exists.
    - load_processed_dataset(filepath): Loads the processed dataset from the given file path.
    - process_dataset(dataset, api_url): Sends the dataset to the API for cleaning and returns the cleaned dataset.
    - save_cleaned_dataset(dataset, filepath): Saves the cleaned dataset to the given file path.
    """
    try:
        logger.info("Starting the cleaning process...")
        config_manager = ConfigurationManager()
        data_cleaning_config = config_manager.get_data_cleaning_config()
        label_encoding_config = config_manager.get_label_encoding_config()

        processed_dataset = load_processed_dataset(data_cleaning_config.processed_dataset_path)
        cleaned_dataset = process_dataset(processed_dataset, data_cleaning_config.clean_endpoint)
        cleaned_dataset = encode_labels(cleaned_dataset, label_encoding_config)

        save_cleaned_dataset(cleaned_dataset, data_cleaning_config.cleaned_dataset_path)
        logger.info("Cleaning process completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during the cleaning process: {str(e)}")

if __name__ == '__main__':
    main()