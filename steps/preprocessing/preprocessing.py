import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

dataset_dir = '/app/data/cleaned/'
dataset_path = '/app/data/cleaned/cleaned_dataset.csv' 
vectorizer_path = '/app/models/tfidf.joblib'

from typing import Tuple


def save_vectorizer(vectorizer, vectorizer_path: str) -> None:
    """
    Save a trained TF-IDF vectorizer to the specified path, 
    along with metadata about Python and Joblib versions.

    Args:
        vectorizer (TfidfVectorizer): The trained TF-IDF vectorizer to save.
        vectorizer_path (str): The file path where the vectorizer will be saved.
    """
    # Prepare metadata about the environment
    metadata = {
        'python_version': sys.version,
        'joblib_version': joblib.__version__
    }
    
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
    custom_mapping = {'apple': 2, 'banana': 5, 'cherry': 3}
    
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
