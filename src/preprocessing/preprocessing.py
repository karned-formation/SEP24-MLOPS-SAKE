import pandas as pd
import numpy as np
import joblib
import sys
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Tuple


# Paths
X_train_path = "/app/data/processed/train/X_train.joblib"
X_test_path = "/app/data/processed/test/X_test.joblib"
y_train_path = "/app/data/processed/train/y_train.joblib"
y_test_path = "/app/data/processed/test/y_test.joblib"
tfidf_vectorizer_path = "/app/models/vectorizers/tfidf_vectorizer.joblib"


import os
import pandas as pd

def fusionner_csv(chemin_dossier, inclure_racine=False):
    # Vérifie si le dossier existe
    if not os.path.isdir(chemin_dossier):
        print(f"Le dossier {chemin_dossier} n'existe pas.")
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
                print(f"Avertissement : Le fichier {chemin_fichier} a {df.shape[1]} colonnes au lieu de 3. Il ne sera pas ajouté.")
        except Exception as e:
            print(f"Erreur lors de la lecture de {chemin_fichier} : {e}")

    # Inclure les fichiers CSV à la racine du dossier si demandé
    if inclure_racine:
        racine_csv = [f for f in os.listdir(chemin_dossier) if f.endswith('.csv')]
        if len(racine_csv) > 1:
            print(f"Erreur : La racine contient plus d'un fichier CSV.")
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
            print(f"Erreur : Le sous-dossier '{sous_dossier}' contient plus d'un fichier CSV.")
            return None
        
        # Ajouter le fichier CSV s'il n'y en a qu'un seul
        for fichier in fichiers_csv:
            chemin_fichier = os.path.join(sous_dossier, fichier)
            ajouter_csv(chemin_fichier)

    # Fusionner tous les DataFrames trouvés
    if dataframes:
        fusion = pd.concat(dataframes, ignore_index=True)
        print(fusion.shape)
        return fusion
    else:
        print("Aucun fichier CSV valide trouvé.")
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
    print(metadata)

    # Save vectorizer with metadata
    joblib.dump({'vectorizer': vectorizer, 'metadata': metadata}, tfidf_vectorizer_path)
    print(f"Vectorizer saved to {tfidf_vectorizer_path} with metadata: {metadata}")

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
        print(f"Variable '{var_name}' saved to {file_path}")


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
    print("Dataset split into training and testing sets.")
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
    print("TF-IDF vectorizer fitted on training data.")
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
    print("Data transformed using TF-IDF vectorizer.")
    return vectorized_data


def main(clean_dir_path: str) -> None:
    """
    Main function to split the dataset, fit and apply TF-IDF vectorization, and save the results.
    """
    # Split the dataset into train and test sets
    X_train, X_test, y_train, y_test = split_dataset(clean_dir_path)
    print(y_test.shape, type(y_test))
    print(y_train.shape, type(y_train))

    
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

if __name__ == "__main__":
    clean_dir_path = "data/cleaned_per_classes"
    X_train_path = "data/processed/train/X_train.joblib"
    X_test_path = "data/processed/test/X_test.joblib"
    y_train_path = "data/processed/train/y_train.joblib"
    y_test_path = "data/processed/test/y_test.joblib"
    tfidf_vectorizer_path = "models/vectorizers/tfidf_vectorizer.joblib"
    main(clean_dir_path)