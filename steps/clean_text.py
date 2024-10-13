import pandas as pd
import requests
from src.data.check_structure import check_existing_folder
import os

def load_processed_dataset(filepath):
    return pd.read_csv(filepath)

def clean_text(api_url, text):
    headers = {'Content-Type': 'text/plain'}
    
    params = {
        "text": text
    }

    response = requests.post(api_url, params=params, headers=headers)
    print(response.text)
    if response.status_code == 200:
        return response.text
    return ''

def read_file_content(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                return file.read()
            
def process_dataset(processed_dataset, api_url):
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

def save_cleaned_dataset(cleaned_dataset, filepath):
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
    - output_folderpath (str): Path to the folder where the cleaned dataset will be saved.
    - processed_dataset_path (str): Path to the processed dataset file.
    - cleaned_dataset_path (str): Path to save the cleaned dataset file.
    - api_url (str): URL of the API used for cleaning the dataset.
    
    Functions:
    - check_existing_folder(folderpath): Checks if the folder exists.
    - load_processed_dataset(filepath): Loads the processed dataset from the given file path.
    - process_dataset(dataset, api_url): Sends the dataset to the API for cleaning and returns the cleaned dataset.
    - save_cleaned_dataset(dataset, filepath): Saves the cleaned dataset to the given file path.
    """
    
    output_folderpath = "data/cleaned/"

    # Crate folder if needed
    if check_existing_folder(output_folderpath):
        os.makedirs(output_folderpath)

    processed_dataset_path = 'data/processed/processed_dataset.csv'
    cleaned_dataset_path = 'data/cleaned/cleaned_dataset.csv'
    api_url = 'http://localhost:8903/clean'

    processed_dataset = load_processed_dataset(processed_dataset_path)
    cleaned_dataset = process_dataset(processed_dataset, api_url)
    save_cleaned_dataset(cleaned_dataset, cleaned_dataset_path)

if __name__ == '__main__':
    main()