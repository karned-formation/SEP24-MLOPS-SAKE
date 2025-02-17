import pandas as pd
import numpy as np
import joblib
import sys
import os
import subprocess
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Tuple
from fastapi import HTTPException

# pour permettre de lancer le programme depuis l'intérieur du docker
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.custom_logger import logger
from src.s3handler import S3Handler

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value

def fusionner_csv(chemin_dossier, inclure_racine=False):
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

    # Inclure les fichiers CSV à la racine du dossier si demandé
    if inclure_racine:
        racine_csv = [f for f in os.listdir(chemin_dossier) if f.endswith('.csv')]
        if len(racine_csv) > 1:
            logger.error(f"Erreur : La racine contient plus d'un fichier CSV.")
            return None
        for fichier in racine_csv:
            chemin_fichier = os.path.join(chemin_dossier, fichier)
            if os.path.isfile(chemin_fichier):
                ajouter_csv(chemin_fichier)

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
        return fusion
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

def save_variables_in_directories(variables: dict) -> None:
    """
    Serialize and save multiple variables using Joblib.

    Args:
        variables (dict): A dictionary where keys are variable names, and values are
                          tuples containing (variable, directory_path).
    """
    # Iterate over the dictionary and save each variable in its respective directory
    for var_name, (var_value, file_path) in variables.items():
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)

        # Save the variable
        joblib.dump(var_value, file_path)
        logger.info(f"Variable '{var_name}' saved to {file_path}")


def split_dataset(clean_dir_path: str, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split the dataset into training and testing sets
    """
    # Load dataset
    df = fusionner_csv(clean_dir_path, inclure_racine=False)
    X = df.drop(['category'], axis=1)
    y = df['category']

    # Split dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    logger.info("Dataset split into training and testing sets.")
    return X_train, X_test, pd.Series(y_train), pd.Series(y_test)


def fit_tfidf_vectorizer(X_train: pd.DataFrame, max_features: int = 70000, ngram_range: Tuple[int, int] = (1, 11), max_df: float = 0.3) -> TfidfVectorizer:
    """
    Fit a TF-IDF vectorizer on the training data's 'cleaned_text' column.

    Args:
        X_train (pd.DataFrame): Training feature set containing a 'cleaned_text' column.
        max_features (int): Maximum number of features to include in the vectorizer.
        ngram_range (Tuple[int, int]): The range of n-grams to include.
        max_df (float): Maximum document frequency for the n-grams.

    Returns:
        TfidfVectorizer: The fitted TF-IDF vectorizer.
    """
    tfidf_vectorizer = TfidfVectorizer(analyzer='char_wb', max_features=max_features, ngram_range=ngram_range, max_df=max_df)
    tfidf_vectorizer.fit(X_train['cleaned_text'])
    logger.info("TF-IDF vectorizer fitted on training data.")
    return tfidf_vectorizer


def transform_with_tfidf(fitted_vectorizer: TfidfVectorizer, data: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the 'cleaned_text' column of the given DataFrame using a fitted TF-IDF vectorizer.

    Args:
        fitted_vectorizer (TfidfVectorizer): The fitted TF-IDF vectorizer.
        data (pd.DataFrame): The DataFrame containing a 'cleaned_text' column to be transformed.

    Returns:
        pd.DataFrame: Transformed data as a sparse matrix.
    """
    vectorized_data = fitted_vectorizer.transform(data['cleaned_text'])
    logger.info("Data transformed using TF-IDF vectorizer.")
    return vectorized_data


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



def main(prediction_folder_S3:str = None) -> None:
    """
    Main function to split the dataset, fit and apply TF-IDF vectorization, and save the results.
    """
    try:        

        STAGE_NAME = "Stage: Pre-Processing"    
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")

        if prediction_folder_S3:
            bucket_name = get_env_var('AWS_BUCKET_NAME')
            # Initialisation de la connexion au bucket              
            handler = S3Handler(bucket_name)

            clean_subdir_bucket = get_env_var("BUCKET_CLEANED_SUBDIR")
            clean_dir_path = f"{prediction_folder_S3}{clean_subdir_bucket}"
            if not handler.folder_exists(clean_dir_path):
                raise HTTPException (status_code = 404, 
                                    detail = f"Le dossier '{clean_dir_path}' n'existe pas sur le bucket.")

            # On télécharge le dossier en local (/!\ Potentiellement plusieurs fichiers)
            handler.download_directory(remote_directory_name = clean_dir_path)

            X_train_subdir = get_env_var("BUCKET_PREPROCESSED_TRAIN_SUBDIR")
            X_train_filename = get_env_var("DATA_PREPROCESSING_X_TRAIN_FILE")
            X_train_path = f"{prediction_folder_S3}{X_train_subdir}{X_train_filename}"

            X_test_subdir = get_env_var("BUCKET_PREPROCESSED_TEST_SUBDIR")
            X_test_filename = get_env_var("DATA_PREPROCESSING_X_TEST_FILE")
            X_test_path = f"{prediction_folder_S3}{X_test_subdir}{X_test_filename}"

            y_train_subdir = get_env_var("BUCKET_PREPROCESSED_TRAIN_SUBDIR")
            y_train_filename = get_env_var("DATA_PREPROCESSING_Y_TRAIN_FILE")
            y_train_path = f"{prediction_folder_S3}{y_train_subdir}{y_train_filename}"
            
            y_test_subdir = get_env_var("BUCKET_PREPROCESSED_TEST_SUBDIR")
            y_test_filename = get_env_var("DATA_PREPROCESSING_Y_TEST_FILE")
            y_test_path = f"{prediction_folder_S3}{y_test_subdir}{y_test_filename}"

            tfidf_vectorizer_subdir = get_env_var("BUCKET_VECTORIZER_SUBDIR")
            tfidf_vectorizer_filename = get_env_var("DATA_PREPROCESSING_VECTORIZER_FILE")
            tfidf_vectorizer_path = f"{prediction_folder_S3}{tfidf_vectorizer_subdir}{tfidf_vectorizer_filename}"
           
        else: # local Linux docker volumes are used
            clean_dir_path = get_env_var("DATA_CLEANING_CLEANED_DATASETS_DIR")

            X_train_path = get_env_var("DATA_PREPROCESSING_X_TRAIN_PATH")
            X_test_path = get_env_var("DATA_PREPROCESSING_X_TEST_PATH")
            y_train_path = get_env_var("DATA_PREPROCESSING_Y_TRAIN_PATH")
            y_test_path = get_env_var("DATA_PREPROCESSING_Y_TEST_PATH")

            tfidf_vectorizer_path = get_env_var("DATA_PREPROCESSING_TFIDF_VECTORIZER_PATH")

            host_uid = get_env_var("HOST_UID")
            host_gid = get_env_var("HOST_GID")

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

        if prediction_folder_S3:
            # upload des fichiers locaux générés vers le bucket s3
            handler.upload_file(X_train_path, X_train_path)
            handler.upload_file(y_train_path, y_train_path)
            handler.upload_file(X_test_path, X_test_path)
            handler.upload_file(y_test_path, y_test_path)
            handler.upload_file(tfidf_vectorizer_path, tfidf_vectorizer_path)
        else:
            # only apply if local Linux docker volumes are used !
            set_permissions_of_host_volume_owner(host_uid, host_gid)

        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")
        
    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e

if __name__ == "__main__":
    main("training_essai_EJA/")