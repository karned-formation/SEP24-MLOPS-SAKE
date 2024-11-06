import os
import subprocess
import pandas as pd
import joblib
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Tuple
from custom_logger import logger

# Paths
train_data_path = "/app/data/processed/train/"
model_path = "/app/models/train/ovrc.joblib"


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
        print(f"Model saved to {model_path}")
    except Exception as e:
        raise IOError(f"Error saving model: {e}")

def main(data_dir: str, model_path: str):
    """
    Main function to load data, create model, train it, and save it.
    """
    # Load data
    X_train, y_train = load_data(data_dir)
    print("Data loaded successfully.")

    # Create model
    model = create_model()
    print("Model created.")

    # Train model
    model = train_model(model, X_train, y_train)
    print("Model trained.")

    # Save model
    save_model(model, model_path)
    print("Model saved successfully.")

    # pour mettre en place les permissions du propriétaire hôte des volumes (pour la création de dossier ou de fichiers)
    host_uid = os.getenv("UID")
    host_gid = os.getenv("GID")
    if host_uid and host_gid: # si les valeurs sont bien récupérées
        with open('/proc/mounts', 'r') as mounts_file:
            app_mounts = [line.split()[1] for line in mounts_file if line.split()[1].startswith("/app/")]

        for mount_point in app_mounts:
            try:
                subprocess.run(["chown", "-R", f"{host_uid}:{host_gid}", mount_point], check=True)
                logger.info(f"Permissions mises à jour pour {mount_point} avec UID={host_uid} et GID={host_gid}.")
            except subprocess.CalledProcessError as e:
                logger.info(f"Erreur lors de la modification des permissions de {mount_point} : {e}")
    else:
        logger.info("UID ou GID de l'hôte non définis.")

# Execute main function
if __name__ == "__main__":
    data_dir = 'data/processed/train'
    model_path = 'models/train/ovrc.joblib'
    main(data_dir, model_path)