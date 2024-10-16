import pandas as pd
import numpy as np
import joblib
import sys
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Tuple


dataset_dir = '/app/data/cleaned/'
dataset_path = '/app/data/cleaned/cleaned_dataset.csv' 
vectorizer_path = '/app/models/tfidf.joblib'

def save_vectorizer(vectorizer, vectorizer_path: str) -> None:
    """
    Save a trained TF-IDF vectorizer to the specified path, 
    along with metadata about Python and Joblib versions.

    Args:
        vectorizer (TfidfVectorizer): The trained TF-IDF vectorizer to save.
        vectorizer_path (str): The file path where the vectorizer will be saved.
    """
    # Ensure the directory exists
    directory = os.path.dirname(vectorizer_path)
    os.makedirs(directory, exist_ok=True)

    # Prepare metadata about the environment
    metadata = {
        'python_version': sys.version,
        'joblib_version': joblib.__version__
    }
    print(metadata)

    # Save vectorizer with metadata
    joblib.dump({'vectorizer': vectorizer, 'metadata': metadata}, vectorizer_path)
    print(f"Vectorizer saved to {vectorizer_path} with metadata: {metadata}")


def custom_label_encoder(labels, action="encode"):
    """
    Encode or decode labels using a predefined custom mapping. 
    Accepts lists, numpy arrays, or pandas Series as input.

    Args:
        labels (list, np.ndarray, pd.Series): Labels to encode or decode.
        action (str): "encode" to transform labels to encoded values, 
                      "decode" to transform encoded values back to labels.

    Returns:
        list: Encoded or decoded labels as a list.

    Raises:
        ValueError: If any labels are not in the mapping or if an invalid action is provided.
    """
    # Define the custom mapping inside the function
    custom_mapping = {'facture': 0, 'id_pieces': 1, 'resume': 2}
    
    # Convert input to a list for consistency in processing
    if isinstance(labels, (np.ndarray, pd.Series)):
        labels = labels.tolist()

    if action == "encode":
        # Ensure all labels are in the provided mapping
        missing_labels = [label for label in labels if label not in custom_mapping]
        if missing_labels:
            raise ValueError(f"Labels {missing_labels} are not in the provided mapping.")
        # Encode the labels using the mapping
        return [custom_mapping[label] for label in labels]
    
    elif action == "decode":
        # Create inverse mapping for decoding
        inverse_mapping = {v: k for k, v in custom_mapping.items()}
        # Ensure all encoded values are in the inverse mapping
        missing_labels = [label for label in labels if label not in inverse_mapping]
        if missing_labels:
            raise ValueError(f"Encoded values {missing_labels} are not in the inverse mapping.")
        # Decode the labels using the inverse mapping
        return [inverse_mapping[label] for label in labels]
    
    else:
        raise ValueError("Invalid action. Use 'encode' or 'decode'.")


def split_dataset(dataset_path: str, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split the dataset into training and testing sets, and encode the labels using a custom encoder.

    Args:
        dataset_path (str): Path to the dataset CSV file.
        test_size (float): Proportion of the dataset to include in the test split.
        random_state (int): Random state for reproducibility.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]: Training and testing splits for features (X) and labels (y).
    """
    # Load dataset
    df = pd.read_csv(dataset_path)
    X = df.drop(['category'], axis=1)
    y = df['category']

    # Encode labels using the custom label encoder
    y_encoded = custom_label_encoder(y, action="encode")

    # Split dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded)
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


def main(dataset_path: str, dataset_dir: str, vectorizer_path: str) -> None:
    """
    Main function to split the dataset, fit and apply TF-IDF vectorization, and save the results.

    Args:
        dataset_path (str): Path to the input dataset CSV file.
        dataset_dir (str): Directory where the split datasets will be saved.
        vectorizer_path (str): Path to save the fitted TF-IDF vectorizer.
    """
    # Split the dataset into train and test sets
    X_train, X_test, y_train, y_test = split_dataset(dataset_path)
    
    # Fit TF-IDF vectorizer on the training data
    fitted_vectorizer = fit_tfidf_vectorizer(X_train)
    
    # Transform both train and test sets
    X_train_vectorized = transform_with_tfidf(fitted_vectorizer, X_train)
    X_test_vectorized = transform_with_tfidf(fitted_vectorizer, X_test)

    # Save the transformed data and labels to CSV files
    pd.DataFrame(X_train_vectorized.toarray()).to_csv(f"{dataset_dir}/train/X_train.csv", index=False)
    pd.DataFrame(X_test_vectorized.toarray()).to_csv(f"{dataset_dir}/test/X_test.csv", index=False)
    pd.Series(y_train).to_csv(f"{dataset_dir}/train/y_train.csv", index=False)
    pd.Series(y_test).to_csv(f"{dataset_dir}/test/y_test.csv", index=False)
    print(f"Transformed data and labels saved to {dataset_dir}.")

    # Save the fitted TF-IDF vectorizer
    save_vectorizer(fitted_vectorizer, vectorizer_path)

if __name__ == "__main__":
    main(dataset_path='cleaned.csv', dataset_dir='.', vectorizer_path='./tfidf.joblib')