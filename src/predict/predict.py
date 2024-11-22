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


def lister_fichiers_images(chemin_dossier):
    extensions_images = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    dossier = Path(chemin_dossier)

    logger.info(f"Démarrage de la liste des fichiers images dans le dossier : {chemin_dossier}")

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
            fichier for fichier in dossier.iterdir()
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
    """Envoi une image à l'API d'océrisation et retourne le texte."""
    logger.info(f"Ocerizing {image}...")
    with open(image, "rb") as file:
        files = {"file": file}
        response = requests.post(ocr_endpoint, files=files)
        return response.text

def save_text_to_file(text: str, path: Path):
    """Enregistre le texte océrisé dans un fichier .txt"""
    print(f"Enregistrement du texte OCR dans le fichier : {path}")
    logger.info(f"Enregistrement du texte OCR dans le fichier : {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf8')

def lister_fichiers_txt(chemin_dossier):
    """
    Liste tous les fichiers .txt dans un dossier donné.
 
    """
    extensions_txt = ['.txt']
    dossier = Path(chemin_dossier)

    # Vérifier si le chemin existe
    if not dossier.exists():
        raise FileNotFoundError(f"Le chemin spécifié n'existe pas : {chemin_dossier}")

    # Vérifier si le chemin est un dossier
    if not dossier.is_dir():
        raise NotADirectoryError(f"Le chemin spécifié n'est pas un dossier : {chemin_dossier}")

    try:
        fichiers_txt = [
            fichier for fichier in dossier.rglob("*")
            if fichier.is_file() and fichier.suffix.lower() in extensions_txt
        ]
        return fichiers_txt
    except PermissionError as e:
        raise PermissionError(f"Permission refusée pour accéder au dossier : {chemin_dossier}") from e
    except Exception as e:
        raise Exception(f"Une erreur inattendue est survenue : {e}") from e


def clean_text(api_url: str, text: str) -> Optional[str]:
    headers = {'Content-Type': 'text/plain'}
    params = {
        "text": text
    }

    response = requests.post(api_url, params=params, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


def clean_ocr_files(api_url: str, ocr_text_files: list) -> list:
    cleaned_texts = []
    for file in ocr_text_files:
        file_content = file.read_text(encoding='utf-8')  # Lecture du contenu du fichier
        cleaned_text = clean_text(api_url, file_content)
        cleaned_texts.append(cleaned_text)
    return cleaned_texts


def generate_cleaned_dataset(ocr_text_files, cleaned_texts, output_csv_path=None):
    """
    Génère un fichier CSV contenant les textes nettoyés et les informations associées.

    """
    # Vérifier si les listes d'entrée sont cohérentes
    if len(ocr_text_files) != len(cleaned_texts):
        raise ValueError("Le nombre de fichiers OCR et de textes nettoyés ne correspond pas.")
    
    # Création du DataFrame
    dataset = pd.DataFrame({
        'filename': [file.name for file in ocr_text_files],  # Nom sans extension
        'cleaned_text': cleaned_texts  # Texte nettoyé
    })
    
    # Définir le chemin de sortie par défaut si non fourni
    if output_csv_path is None:
        output_csv_path = ocr_text_files[0].parent / "cleaned_dataset.csv"
    
    # Création des répertoires si nécessaire
    output_csv_path = Path(output_csv_path)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarde en CSV
    dataset.to_csv(output_csv_path, index=False)
    print(f"Fichier CSV généré : {output_csv_path}")
    return dataset


def transform_with_tfidf(fitted_vectorizer: TfidfVectorizer, data: pd.DataFrame, return_as_dataframe=False) -> pd.DataFrame:
    """
    Transform the 'cleaned_text' column of the given DataFrame using a fitted TF-IDF vectorizer.

    """
    # Vérification de la colonne
    if 'cleaned_text' not in data.columns:
        raise KeyError("The DataFrame does not contain a 'cleaned_text' column.")
    
    # Transformation avec TF-IDF
    vectorized_data = fitted_vectorizer.transform(data['cleaned_text'])
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


    # Charger le CSV avec les textes nettoyés
    cleaned_data = pd.read_csv(cleaned_csv_path+'/cleaned_dataset.csv')

    # Vérifier si les données vectorisées et les textes nettoyés ont la même longueur
    if vectorized_data.shape[0] != len(cleaned_data):
        raise ValueError("Le nombre de données vectorisées ne correspond pas au nombre de textes nettoyés dans le CSV.")

    # Effectuer les prédictions avec le modèle
    predictions = model.predict(vectorized_data)

    # Ajouter les prédictions au DataFrame
    cleaned_data['prediction'] = predictions
    cleaned_data = cleaned_data[['filename', 'prediction']]

    # Afficher les prédictions si demandé
    if display_predictions:
        print(cleaned_data[['filename', 'prediction']])

    # Définir le chemin de sortie par défaut si non fourni
    if output_csv_path is None:
        output_csv_path = Path(cleaned_csv_path) / "predictions.csv"

    # Création des répertoires si nécessaire
    output_csv_path = Path(output_csv_path)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    # Sauvegarder le DataFrame avec les prédictions en CSV
    cleaned_data.to_csv(output_csv_path, index=False)
    print(f"Fichier CSV des prédictions généré : {output_csv_path}")

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

        X_train_path = get_env_var("DATA_PREPROCESSING_X_TRAIN_PATH")
        X_test_path = get_env_var("DATA_PREPROCESSING_X_TEST_PATH")
        y_train_path = get_env_var("DATA_PREPROCESSING_Y_TRAIN_PATH")
        y_test_path = get_env_var("DATA_PREPROCESSING_Y_TEST_PATH")

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
     
    images_to_predict_path = 'data/images_to_predict' # TODO
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
        # full_text = get_full_text(image, ocr_endpoint)
        # text_file_path = image.with_suffix('.txt')
        # save_text_to_file(full_text, text_file_path)
        # print("text saved")
        pass
    
    # Text Cleaning
    ocr_text_files = lister_fichiers_txt(images_to_predict_path)
    cleaned_texts = clean_ocr_files(clean_endpoint, ocr_text_files)
    cleaned_df = generate_cleaned_dataset(images, cleaned_texts, output_csv_path=None)

    #Vectorization
    vectorized_data = transform_with_tfidf(fitted_vectorizer, cleaned_df)
    
    #Predition
    make_predictions(images_to_predict_path, model, vectorized_data, display_predictions=False) 
