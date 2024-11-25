from pathlib import Path
from typing import List
import os
import requests
from typing import Optional
from src.custom_logger import logger
import pandas as pd
import joblib
import subprocess
from sklearn.feature_extraction.text import TfidfVectorizer



def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value

def lister_fichiers_images(chemin_dossier, recurse=True):
    extensions_images = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    dossier = Path(chemin_dossier)

    logger.info(f"Recherche des images dans le dossier : {chemin_dossier}")

    # Vérifier si le chemin existe
    if not dossier.exists():
        logger.error(f"Le chemin spécifié n'existe pas : {chemin_dossier}")
        raise FileNotFoundError(f"Le chemin spécifié n'existe pas : {chemin_dossier}")

    # Vérifier si le chemin est un dossier
    if not dossier.is_dir():
        logger.error(f"Le chemin spécifié n'est pas un dossier : {chemin_dossier}")
        raise NotADirectoryError(f"Le chemin spécifié n'est pas un dossier : {chemin_dossier}")

    try:
        fichiers_images = [
            fichier for fichier in (dossier.rglob('*') if recurse else dossier.iterdir())
            if fichier.is_file() and fichier.suffix.lower() in extensions_images
        ]
        logger.info(f"{len(fichiers_images)} fichier(s) image(s) trouvé(s) dans le dossier {chemin_dossier}")
        return fichiers_images
    except PermissionError as e:
        logger.exception(f"Permission refusée pour accéder au dossier : {chemin_dossier}")
        raise PermissionError(f"Permission refusée pour accéder au dossier : {chemin_dossier}") from e
    except Exception as e:
        logger.exception(f"Une erreur inattendue est survenue lors de la lecture du dossier : {chemin_dossier}")
        raise Exception(f"Une erreur inattendue est survenue : {e}") from e


def get_full_text(image: str, ocr_endpoint: str) -> str:
    """
    Envoie une image à l'API d'OCR et retourne le texte.

    """
    logger.info(f"Commencing OCR process for image: {image}")
    
    try:
        # Log the API endpoint
        logger.debug(f"Using OCR endpoint: {ocr_endpoint}")
        
        # Open the file and send it to the OCR API
        with open(image, "rb") as file:
            files = {"file": file}
            logger.info(f"Sending image {image} to OCR endpoint...")
            
            response = requests.post(ocr_endpoint, files=files)
            logger.info(f"Received response with status code: {response.status_code}")
            
            # Log response details in case of an issue
            if response.status_code != 200:
                logger.warning(f"OCR API returned a non-200 status code: {response.status_code}")
                logger.debug(f"Response content: {response.text}")
                response.raise_for_status()
            
            logger.info("OCR process completed successfully.")
            return response.text
    
    except FileNotFoundError:
        logger.error(f"Image file not found: {image}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during the OCR API request: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

def save_text_to_file(text: str, path: Path):
    """Enregistre le texte océrisé dans un fichier .txt"""
    logger.info(f"Enregistrement du texte OCR dans le fichier : {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf8')

def lister_fichiers_txt(chemin_dossier, recurse=True):
    """
    Liste tous les fichiers .txt dans un dossier donné.
 
    """
    logger.info(f"Recherche des textes dans le dossier : {chemin_dossier}")
    extensions_txt = ['.txt']
    dossier = Path(chemin_dossier)

    # Vérifier si le chemin existe
    if not dossier.exists():
        logger.error(f"Le chemin spécifié n'existe pas : {chemin_dossier}")
        raise FileNotFoundError(f"Le chemin spécifié n'existe pas : {chemin_dossier}")

    # Vérifier si le chemin est un dossier
    if not dossier.is_dir():
        logger.error(f"Le chemin spécifié n'est pas un dossier : {chemin_dossier}")
        raise NotADirectoryError(f"Le chemin spécifié n'est pas un dossier : {chemin_dossier}")

    try:
        logger.debug("Recherche récursive des fichiers .txt...")
        fichiers_txt = [
            fichier for fichier in (dossier.rglob("*") if recurse else dossier.iterdir())
            if fichier.is_file() and fichier.suffix.lower() in extensions_txt
        ]
        logger.info(f"{len(fichiers_txt)} fichier(s) texte(s) trouvé(s) dans le dossier {chemin_dossier}")
        return fichiers_txt

    except PermissionError as e:
        logger.error(f"Permission refusée pour accéder au dossier : {chemin_dossier}")
        raise PermissionError(f"Permission refusée pour accéder au dossier : {chemin_dossier}") from e

    except Exception as e:
        logger.error(f"Une erreur inattendue est survenue lors de la recherche : {e}")
        raise Exception(f"Une erreur inattendue est survenue : {e}") from e

def clean_text(api_url: str, text: str) -> Optional[str]:
    headers = {'Content-Type': 'text/plain'}
    params = {
        "text": text
    }

    logger.debug(f"Request headers: {headers}")
    logger.info(f"Sending request to API: {api_url}")
    logger.debug(f"Request params: {params}")

    response = requests.post(api_url, params=params, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


def clean_ocr_files(api_url: str, images: list) -> list:

    df = pd.DataFrame({
        'txt_path': [img.with_suffix(".txt") for img in images],
        'img_path': images
        })
    
    clean_text_column = []

    for file in df['txt_path']:
        logger.info(f"Cleaning  file: {file}")
        file_content = file.read_text(encoding='utf-8')  # Lecture du contenu du fichier
        cleaned_text = clean_text(api_url, file_content)
        clean_text_column.append(cleaned_text)
    
    df['cleaned_text'] = clean_text_column
    return df


def generate_cleaned_dataset(df, images_to_predict_path, output_csv_path=None):
    """
    Génère un fichier CSV contenant les textes nettoyés et les informations associées.

    """
    logger.info("Démarrage de la génération du dataset nettoyé.")
    # Vérifier si les listes d'entrée sont cohérentes
    if df['txt_path'].count() != df['cleaned_text'].count():
        logger.error("Le nombre de fichiers OCR et de textes nettoyés ne correspond pas.")
        raise ValueError("Le nombre de fichiers OCR et de textes nettoyés ne correspond pas.")
    

    # Définir le chemin de sortie par défaut si non fourni
    if output_csv_path is None:
        output_csv_path = Path(df['img_path'][0]).parent / "cleaned_dataset.csv"
    
    # Création des répertoires si nécessaire
    output_csv_path = Path(output_csv_path)
    try:
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Erreur lors de la création du répertoire de sortie : {e}")
        raise

    
    # Sauvegarde en CSV
    df = df.drop(columns='txt_path')
    df = df.sort_values(by='img_path')
    try:
        df.to_csv(output_csv_path, index=False)
        logger.info(f"Fichier CSV généré avec succès : {output_csv_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier CSV : {e}")
        raise
    return df


def transform_with_tfidf(fitted_vectorizer: TfidfVectorizer, df: pd.DataFrame, return_as_dataframe=False) -> pd.DataFrame:
    """
    Transform the 'cleaned_text' column of the given DataFrame using a fitted TF-IDF vectorizer.

    """
    # Vérification de la colonne
    if 'cleaned_text' not in df.columns:
        logger.error(f"The DataFrame does not contain a 'cleaned_text' column.")
        raise KeyError("The DataFrame does not contain a 'cleaned_text' column.")
    
    # Transformation avec TF-IDF
    vectorized_data = fitted_vectorizer.transform(df['cleaned_text'])
    logger.info(f"Data transformed using TF-IDF vectorizer. Shape: {vectorized_data.shape}")
    
    # Retour en DataFrame si demandé
    if return_as_dataframe:
        return pd.DataFrame(
            vectorized_data.toarray(),
            columns=fitted_vectorizer.get_feature_names_out(),
            index=data.index  # Conserve les index du DataFrame original
        )
    
    return vectorized_data

def make_predictions(cleaned_csv_path, model, vectorized_data, output_csv_path=None, display_predictions=False):
    """
    Génère un fichier CSV contenant les prédictions pour chaque texte nettoyé.
    """
    
    logger.info("Début de la génération des prédictions.")
    logger.debug(f"Chemin du fichier cleaned_dataset.csv : {cleaned_csv_path}/cleaned_dataset.csv")

    try:
        # Charger le CSV avec les textes nettoyés
        logger.info("Chargement des données nettoyées depuis le fichier CSV.")
        cleaned_data = pd.read_csv(cleaned_csv_path + '/cleaned_dataset.csv')
    except FileNotFoundError:
        logger.error(f"Le fichier cleaned_dataset.csv est introuvable dans le dossier : {cleaned_csv_path}")
        raise
    except Exception as e:
        logger.error(f"Erreur lors du chargement du fichier CSV : {e}")
        raise

    # Vérifier si les données vectorisées et les textes nettoyés ont la même longueur
    if vectorized_data.shape[0] != len(cleaned_data):
        logger.error("Le nombre de données vectorisées ne correspond pas au nombre de textes nettoyés.")
        raise ValueError("Le nombre de données vectorisées ne correspond pas au nombre de textes nettoyés dans le CSV.")
    
    logger.info("Validation de la correspondance entre les données vectorisées et les textes nettoyés réussie.")

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
    logger.info("Ajout des probabilités au DataFrame.")
    for class_ in class_order:
        cleaned_data[f'Prob_class_{class_}'] = probabilities[:, class_]
    
    cleaned_data.to_csv(f'{cleaned_csv_path}/a.CSV') # TODO
    cleaned_data = cleaned_data.drop(columns='cleaned_text') 
   
    # Afficher les prédictions si demandé
    if display_predictions:
        logger.info("Affichage des prédictions.")
        print(cleaned_data[['filename', 'prediction']])

    # Définir le chemin de sortie par défaut si non fourni
    if output_csv_path is None:
        output_csv_path = Path(cleaned_csv_path) / "predictions.csv"
        output_json_path = Path(cleaned_csv_path) / "predictions.json"
    
    # Création des répertoires si nécessaire
    output_csv_path = Path(output_csv_path)
    try:
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Erreur lors de la création des répertoires de sortie : {e}")
        raise

    # Sauvegarder le DataFrame avec les prédictions en CSV
    try:
        cleaned_data.set_index('img_path', drop=True, inplace=True)
        cleaned_data.to_csv(output_csv_path)
        cleaned_data.to_json(output_json_path, orient='index')
        logger.info(f"Fichier CSV des prédictions généré avec succès : {output_csv_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des prédictions : {e}")
        raise

    logger.info("Génération des prédictions terminée.")
    return cleaned_data

def set_permissions_of_host_volume_owner(host_uid, host_gid):
    """ pour mettre en place les permissions du propriétaire hôte des volumes 
        - sur chacun des volumes montés dans "/app/"
        - pour tous les dossiers et fichiers dans ces volumes
    """
    if host_uid and host_gid: # si les valeurs sont bien récupérées
        with open('/proc/mounts', 'r') as mounts_file:
            app_mounts = [line.split()[1] for line in mounts_file if line.split()[1].startswith("/app/")]

        for mount_point in app_mounts:
            try:
                subprocess.run(["chown", "-R", f"{host_uid}:{host_gid}", mount_point], check=True)
                logger.info(f"Permissions mises à jour pour {mount_point} avec UID={host_uid} et GID={host_gid}.")
            except subprocess.CalledProcessError as e:
                logger.error(f"Erreur lors de la modification des permissions de {mount_point} : {e}")
    else:
        logger.error("UID ou GID de l'hôte non définis.")



def main() -> None:
    """
    Main function to split the dataset, fit and apply TF-IDF vectorization, and save the results.
    """

    STAGE_NAME = "Stage: Pre-Processing"    
    try:        
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")

        clean_dir_path = get_env_var("DATA_CLEANING_CLEANED_DATASETS_DIR")
        tfidf_vectorizer_path = get_env_var("DATA_PREPROCESSING_TFIDF_VECTORIZER_PATH")

        host_uid = get_env_var("HOST_UID")
        host_gid = get_env_var("HOST_GID")

        # Check if the input exists
        if not os.path.exists(clean_dir_path):
            logger.error(f"Dataset not found: {clean_dir_path}")
            raise Exception("Dataset not found")

        # Split the dataset into train and test sets
        X_train, X_test, y_train, y_test = split_dataset(clean_dir_path)
        logger.info(f"y_test shape : {y_test.shape}")
        logger.info(f"y_train shape : {y_train.shape}")
        
        # Fit TF-IDF vectorizer on the training data
        fitted_vectorizer = fit_tfidf_vectorizer(X_train)
        
        # Transform both train and test sets
        X_train_vectorized = transform_with_tfidf(fitted_vectorizer, X_train)
        X_test_vectorized = transform_with_tfidf(fitted_vectorizer, X_test)

        # Prepare variables to save, specifying the directory for each
        variables_to_save = {
            'X_train': (X_train_vectorized, X_train_path),
            'X_test': (X_test_vectorized, X_test_path),
            'y_train': (y_train, y_train_path),
            'y_test': (y_test, y_test_path),
            'tfid_vectorizer': (fitted_vectorizer, tfidf_vectorizer_path)
        }

        # Save the transformed data and labels using Joblib
        save_variables_in_directories(variables_to_save)

        # Save the fitted TF-IDF vectorizer
        save_vectorizer(fitted_vectorizer, tfidf_vectorizer_path)

        set_permissions_of_host_volume_owner(host_uid, host_gid)

        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")
    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e

if __name__ == "__main__":
    # main()
     
    images_to_predict_path = 'data/images_to_predict/1002' # TODO
    tfidf_vectorizer_path = 'models/vectorizers/tfidf_vectorizer.joblib' #TODO get_env_var("DATA_PREPROCESSING_TFIDF_VECTORIZER_PATH")
    model_path = get_env_var("MODEL_TRAIN_MODEL_TRAIN_PATH")

    clean_endpoint = 'http://localhost:8903/clean' # TODO get_env_var("DATA_CLEANING_CLEAN_ENDPOINT") 
    ocr_endpoint = 'http://localhost:8901/txt/blocks-words' # TODO URL not working while get_env_var("DATA_INGESTION_OCR_ENDPOINT")
    
    fitted_vectorizer =  joblib.load(tfidf_vectorizer_path)
    model = joblib.load(model_path)


    host_uid = get_env_var("HOST_UID")
    host_gid = get_env_var("HOST_GID")



    # OCR
    images = lister_fichiers_images(images_to_predict_path)
    for image in images:
        if (image.with_suffix(".txt").exists()):
            continue
        full_text = get_full_text(image, ocr_endpoint)
        text_file_path = image.with_suffix('.txt')
        save_text_to_file(full_text, text_file_path)

   
    # Text Cleaning
    # ocr_text_files = lister_fichiers_txt(images_to_predict_path) TODO
    df = clean_ocr_files(clean_endpoint, images) # TODO: Check function
    df = generate_cleaned_dataset(df, images_to_predict_path)
  
    #Vectorization
    vectorized_data = transform_with_tfidf(fitted_vectorizer, df)
    
    #Predition
    make_predictions(images_to_predict_path, model, vectorized_data, display_predictions=False)