import os
import subprocess
import pandas as pd
import joblib
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Tuple
from custom_logger import logger

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value


def load_data(data_dir: str) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Loads the training data from the data folder.

    Parameters:
        data_dir (str): The directory path containing X_train.csv and y_train.csv files.

    Returns:
        Tuple[pd.DataFrame, pd.Series]: The feature data (X_train) as a DataFrame and labels (y_train) as a Series.
    """
    try:
        X_train = joblib.load(os.path.join(data_dir, 'X_train.joblib'))
        y_train = joblib.load(os.path.join(data_dir, 'y_train.joblib'))
        return X_train, y_train
    except Exception as e:
        raise FileNotFoundError(f"Error loading data files from {data_dir}: {e}")

def create_model() -> OneVsRestClassifier:
    """
    Creates a OneVsRest logistic regression model.

    Returns:
        OneVsRestClassifier: The configured logistic regression model.
    """
    logistic_regression = LogisticRegression(
        class_weight='balanced', n_jobs=-1, C=100, multi_class='auto'
    )
    return OneVsRestClassifier(estimator=logistic_regression, n_jobs=-1)

def train_model(model: OneVsRestClassifier, X_train: pd.DataFrame, y_train: pd.Series) -> OneVsRestClassifier:
    """
    Transforms the text data using TF-IDF and trains the given model.

    Parameters:
        model (OneVsRestClassifier): The model to be trained.
        X_train (pd.Dataframe): The training data features.
        y_train (pd.Series): The training data labels.

    Returns:
        OneVsRestClassifier: The trained model.
    """
    model.fit(X_train, y_train)
    return model

def save_model(model, model_path: str):
    """
    Saves the trained model to a file. Creates the directory path if it doesn't exist.

    Parameters:
        model: The trained model to be saved.
        model_path (str): The file path where the model will be saved.

    Raises:
        IOError: If there is an issue saving the model.
    """
    # Create directory path if it doesn't exist
    directory = os.path.dirname(model_path)
    os.makedirs(directory, exist_ok=True)
    
    # Save the model to the specified path
    try:
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        raise IOError(f"Error saving model: {e}")

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

def main():
    """
    Main function to load data, create model, train it, and save it.
    """

    STAGE_NAME = "Stage: Train"    
    try:        
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")

        data_dir = get_env_var("DATA_PREPROCESSING_TRAIN_DATA_DIR")
        model_path = get_env_var("MODEL_TRAIN_MODEL_TRAIN_PATH")

        host_uid = get_env_var("HOST_UID")
        host_gid = get_env_var("HOST_GID")

        # Check if the input exists
        if not os.path.exists(data_dir):
            logger.error(f"Train Dataset not found: {data_dir}")
            raise Exception("Dataset not found")

        # Load data
        X_train, y_train = load_data(data_dir)
        logger.info("Data loaded successfully.")

        # Create model
        model = create_model()
        logger.info("Model created.")

        # Train model
        model = train_model(model, X_train, y_train)
        logger.info("Model trained.")

        # Save model
        save_model(model, model_path)
        logger.info("Model saved successfully.")

        set_permissions_of_host_volume_owner(host_uid, host_gid)

        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")
    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e

# Execute main function
if __name__ == "__main__":

    main()