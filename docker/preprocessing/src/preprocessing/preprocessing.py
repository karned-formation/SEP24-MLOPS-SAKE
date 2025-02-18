import base64
from io import BytesIO
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Tuple
from src.custom_logger import logger

def split_dataset_train(clean_csv: str, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split the dataset into training and testing sets
    """
    # Load dataset
    df = pd.read_json(clean_csv)
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



def generate_objects(clean_csv: str):
    X_train, X_test, y_train, y_test = split_dataset_train(clean_csv)

    tfidf_vectorizer =  fit_tfidf_vectorizer(X_train)
    
    X_train = transform_with_tfidf(tfidf_vectorizer, X_train)
    X_test = transform_with_tfidf(tfidf_vectorizer, X_test)
    
    X_train_bytes = serialize_object(X_train)
    y_train_bytes = serialize_object(y_train)
    X_test_bytes = serialize_object(X_test)
    y_test_bytes = serialize_object(y_test)
    tfidf_vectorizer_bytes = serialize_object(tfidf_vectorizer)
    
    return X_train_bytes, y_train_bytes,X_test_bytes,y_test_bytes, tfidf_vectorizer_bytes

def serialize_object(obj):
    buffer = BytesIO()
    joblib.dump(obj, buffer)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')  # Encode as Base64 string for pydantic
