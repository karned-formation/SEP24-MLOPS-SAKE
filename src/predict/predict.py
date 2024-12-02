from pathlib import Path
from typing import List
import os
from datetime import datetime
import requests
from typing import Optional
from src.custom_logger import logger
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from src.s4handler import S3Handler



def get_env_var(name):
    """Retrieve environment variables securely."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value

def get_csv_file_path(prediction_folder: str):
    """
    Construct the path to the cleaned CSV file based on a folder path.
    """
    return os.path.join(prediction_folder.rstrip('/'), 'cleaned', 'cleaned.csv')

def transform_with_tfidf(fitted_vectorizer: TfidfVectorizer, csv_file_path: str) -> pd.DataFrame:
    """
    Transform text data into TF-IDF features.
    """

    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file '{csv_file_path}' does not exist.")
    
    df = pd.read_csv(csv_file_path)
    if 'cleaned_text' not in df.columns:
        logger.error(f"The DataFrame does not contain a 'cleaned_text' column.")
        raise KeyError("'cleaned_text' column is missing from the CSV file.")
    
    return fitted_vectorizer.transform(df['cleaned_text'])
    df = pd.read_csv(csv_file_path)

      
def make_predictions(cleaned_csv_path, model, vectorized_data, display_predictions=False):
    """
    Generate predictions and save results as CSV and JSON.
    """
    
    logger.info("Début de la génération des prédictions.")

    # Effectuer les prédictions avec le modèle
    try:
        # Probabilités pour chaque classe
        probabilities = model.predict_proba(vectorized_data)
        # Ordre des classes
        class_order = model.classes_ 
        logger.info("probabilités récupérées avec succès.")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la probablité des classes : {e}")
        raise

    # Ajouter les prédictions au DataFrame
    logger.info("Création du Dataframe avec les probabilités.")
    cleaned_data = pd.read_csv(cleaned_csv_path)
    for class_ in class_order:
        cleaned_data[f'Prob_class_{class_}'] = probabilities[:, class_]
    
    cleaned_data = cleaned_data.drop(columns='cleaned_text') 
   
    # Afficher les prédictions si demandé
    if display_predictions:
        logger.info("Affichage des prédictions.")

    # Définir le chemin de sortie par défaut
    output_csv_path = Path(cleaned_csv_path).parent.parent / "prediction/predictions.csv"
    output_json_path = Path(cleaned_csv_path).parent.parent / "prediction/predictions.json"
    
    # Création des répertoires si nécessaire
    output_csv_path = Path(output_csv_path)
    try:
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Erreur lors de la création des répertoires de sortie : {e}")
        raise

    # Sauvegarder le DataFrame avec les prédictions en CSV
    try:
        cleaned_data.set_index('filename', inplace=True)
        cleaned_data.to_csv(output_csv_path)
        cleaned_data.to_json(output_json_path, orient='index')
        logger.info(f"Fichiers de prédictions générés avec succès : {output_csv_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des prédictions : {e}")
        raise

    logger.info("Génération des prédictions terminée.")
    return cleaned_data.to_json(orient='index')


if __name__ == "__main__":
    tfidf_vectorizer_path = 'models/vectorizers/tfidf_vectorizer.joblib' #TODO get_env_var("DATA_PREPROCESSING_TFIDF_VECTORIZER_PATH")
    model_path = 'models/train/ovrc.joblib'# TODO get_env_var("MODEL_TRAIN_MODEL_TRAIN_PATH")

    fitted_vectorizer =  joblib.load(tfidf_vectorizer_path)
    model = joblib.load(model_path)

    aws_access_key_id = get_env_var("AWS_ACCESS_KEY_ID")
    aws_bucket_name = get_env_var("AWS_BUCKET_NAME")
    aws_secret_access_key = get_env_var("AWS_SECRET_ACCESS_KEY")
    handler = S3Handler(aws_bucket_name)

    prediction_folder = 'prediction_1731849628.762522/'
    csv_file_path = get_csv_file_path(prediction_folder)
    csv_file_path = handler.download_file(csv_file_path)


    vectorized_data = transform_with_tfidf(fitted_vectorizer, csv_file_path)
    print(make_predictions(csv_file_path, model, vectorized_data))

    remote_path = local_directory = str(Path(csv_file_path).parent.parent / 'prediction')
    handler.upload_directory(remote_path=remote_path, local_directory_name=local_directory)