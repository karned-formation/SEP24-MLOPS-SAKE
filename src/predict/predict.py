import pandas as pd
import joblib
import os

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

from src.custom_logger import logger
from src.s3handler import S3Handler



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
    cleaned_dir = get_env_var("BUCKET_CLEANED_SUBDIR")
    return os.path.join(prediction_folder.rstrip('/'), cleaned_dir, 'cleaned.csv')

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
    prediction_dir = get_env_var("BUCKET_PREDICTIONS_SUBDIR")
    output_csv_path = Path(cleaned_csv_path).parent.parent / prediction_dir / "predictions.csv"
    output_json_path = Path(cleaned_csv_path).parent.parent / prediction_dir / "predictions.json"
    # output_csv_path = Path(cleaned_csv_path).parent.parent / "prediction/predictions.csv"
    # output_json_path = Path(cleaned_csv_path).parent.parent / "prediction/predictions.json"
    
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

def load_vectorizer_and_model():
    """Load the TF-IDF vectorizer and prediction model."""
    logger.info("Loading vectorizer and model ENV variables.")
    vectorizer_path = get_env_var("DATA_PREPROCESSING_TFIDF_VECTORIZER_PATH")
    model_path = get_env_var("MODEL_TRAIN_MODEL_TRAIN_PATH")
    print(vectorizer_path, model_path)
    logger.info("Loading vectorizer and model.")
    vectorizer = joblib.load(vectorizer_path)
    model = joblib.load(model_path)
    logger.info("Vectorizer and model loaded successfully.")
    return vectorizer, model


def initialize_s3_handler():
    """Initialize the S3 handler with environment variables."""
    aws_access_key_id = get_env_var("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_env_var("AWS_SECRET_ACCESS_KEY")
    aws_bucket_name = get_env_var("AWS_BUCKET_NAME")
    logger.info("S3 handler initialized.")
    return S3Handler(aws_bucket_name)

def create_parent_dir(file_path: str):
    logger.info(f"Creating parent folder for: {file_path}")
    parent_dir = Path(file_path).parent
    Path(parent_dir).mkdir(parents=True, exist_ok=True)  
    return str(parent_dir / Path(file_path).name )


def prepare_prediction_folder(prediction_folder: str, s3_handler: S3Handler):
    """Prepare the prediction folder and download the cleaned CSV file."""
    logger.info(f"Preparing prediction folder: {prediction_folder}")
    remote_csv_file_path = get_csv_file_path(prediction_folder)
    local_csv_file_path = create_parent_dir(remote_csv_file_path)
    csv_file_path = s3_handler.download_file(remote_csv_file_path, local_csv_file_path)
    logger.info(f"Cleaned CSV downloaded: {remote_csv_file_path}")
    return csv_file_path

def process_predictions(
    csv_file_path: str, vectorizer: TfidfVectorizer, model, s3_handler: S3Handler
):
    """Process predictions and upload results."""
    # Transform data
    logger.info("Starting TF-IDF transformation.")
    vectorized_data = transform_with_tfidf(vectorizer, csv_file_path)
    
    # Generate predictions
    logger.info("Generating predictions.")
    predictions_json = make_predictions(csv_file_path, model, vectorized_data)
    logger.info("Predictions generated successfully.")
    
    # Upload prediction results
    prediction_folder = Path(csv_file_path).parent.parent / get_env_var("BUCKET_PREDICTIONS_SUBDIR")
    logger.info(f"Uploading predictions to S3: {prediction_folder}")
    s3_handler.upload_directory(
        remote_path=str(prediction_folder), local_directory_name=str(prediction_folder)
    )
    logger.info("Predictions uploaded successfully.")
    
    return predictions_json

def main(prediction_folder: str):
    """Main function to handle the prediction process."""
    try:
        logger.info("Starting the prediction process.")
        # Load vectorizer and model
        vectorizer, model = load_vectorizer_and_model()
        
        # Initialize S3 handler
        s3_handler = initialize_s3_handler()
        
        # Prepare prediction folder
        csv_file_path = prepare_prediction_folder(prediction_folder, s3_handler)
        
        # Process predictions
        predictions_json = process_predictions(csv_file_path, vectorizer, model, s3_handler)
        
        logger.info("Prediction process completed successfully.")
        return predictions_json
        
    except Exception as e:
        logger.error(f"An error occurred during the prediction process: {e}")
        raise

if __name__ == "__main__":
    print(main('prediction_1731849628.762522/'))