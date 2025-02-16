import base64
from io import BytesIO, StringIO
from typing import Optional

import requests
from src.custom_logger import logger
import os
import joblib
import pandas as pd
import sys


def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value


def fusionner_csv(chemin_dossier):
    # Vérifie si le dossier existe
    if not os.path.isdir(chemin_dossier):
        logger.error(f"Le dossier {chemin_dossier} n'existe pas.")
        return None

    # Liste pour stocker les DataFrames de tous les fichiers CSV
    dataframes = []

    # Fonction pour lire un fichier CSV et l'ajouter à la liste
    def ajouter_csv(chemin_fichier):
        try:
            df = pd.read_csv(chemin_fichier)
            # Vérifie que le fichier CSV contient exactement 3 colonnes
            if df.shape[1] == 3:
                dataframes.append(df)
            else:
                logger.info(f"Avertissement : Le fichier {chemin_fichier} a {df.shape[1]} colonnes au lieu de 3. Il ne sera pas ajouté.")
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de {chemin_fichier} : {e}")

    # Parcourir les sous-dossiers pour trouver les fichiers CSV
    for sous_dossier, _, fichiers in os.walk(chemin_dossier):
        # Filtrer pour obtenir uniquement les fichiers CSV dans le sous-dossier en cours
        fichiers_csv = [f for f in fichiers if f.endswith('.csv')]
        
        # Vérifier s'il y a plus d'un fichier CSV dans le sous-dossier
        if len(fichiers_csv) > 1:
            logger.error(f"Erreur : Le sous-dossier '{sous_dossier}' contient plus d'un fichier CSV.")
            return None
        
        # Ajouter le fichier CSV s'il n'y en a qu'un seul
        for fichier in fichiers_csv:
            chemin_fichier = os.path.join(sous_dossier, fichier)
            ajouter_csv(chemin_fichier)

    # Fusionner tous les DataFrames trouvés
    if dataframes:
        fusion = pd.concat(dataframes, ignore_index=True)
        logger.info(fusion.shape)
        return fusion.to_json(orient='records', index=False)
    else:
        logger.error("Aucun fichier CSV valide trouvé.")
        return None
    
def save_vectorizer(vectorizer, tfidf_vectorizer_path: str) -> None:
    """
    Save a trained TF-IDF vectorizer to the specified path, 
    along with metadata about Python and Joblib versions.

    Args:
        vectorizer (TfidfVectorizer): The trained TF-IDF vectorizer to save.
        tfidf_vectorizer_path (str): The file path where the vectorizer will be saved.
    """
    # Ensure the directory exists
    directory = os.path.dirname(tfidf_vectorizer_path)
    os.makedirs(directory, exist_ok=True)

    # Prepare metadata about the environment
    metadata = {
        'python_version': sys.version,
        'joblib_version': joblib.__version__
    }
    logger.info(metadata)

    # Save vectorizer with metadata
    joblib.dump(vectorizer, tfidf_vectorizer_path)
    logger.info(f"Vectorizer saved to {tfidf_vectorizer_path} with metadata: {metadata}")


def call_preprocess(api_url: str, clean_csv: str) -> Optional[str]:
    headers = {'Content-Type': 'application/json'}
    json_payload = {"clean_csv": clean_csv}

    response = requests.post(api_url, json=json_payload, headers=headers)
    if response.status_code == 200:
        return response
    return None

def save_object_locally(encoded_str, path):
    buffer = BytesIO(base64.b64decode(encoded_str))
    j = joblib.dump(buffer, path)

def preprocess_train():
    cleaned_datasets_dir = get_env_var("DATA_CLEANING_CLEANED_DATASETS_DIR")
    preprocess_endpoint = get_env_var("DATA_PREPROCESSING_ENDPOINT_PREPROCESSING_TRAIN")
    X_train_path = get_env_var("DATA_PREPROCESSING_X_TRAIN_PATH")
    X_test_path = get_env_var("DATA_PREPROCESSING_X_TEST_PATH")
    y_train_path = get_env_var("DATA_PREPROCESSING_Y_TRAIN_PATH")
    y_test_path = get_env_var("DATA_PREPROCESSING_Y_TEST_PATH")
    tfidf_vectorizer_path = get_env_var("DATA_PREPROCESSING_TFIDF_VECTORIZER_PATH")

    STAGE_NAME = "Stage: preprocessing"
    try:
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")

        csvs = fusionner_csv(cleaned_datasets_dir)
        response = call_preprocess(preprocess_endpoint, csvs)
        json_response = response.json()  
        
        save_object_locally(json_response["X_train"], X_train_path)
        save_object_locally(json_response["y_train"], y_train_path)
        save_object_locally(json_response["X_test"], X_test_path)
        save_object_locally(json_response["y_test"], y_test_path)
        save_object_locally(json_response["tfidf_vectorizer"], tfidf_vectorizer_path)
        
        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")

    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e

if __name__ == "__main__":
    preprocess_train()