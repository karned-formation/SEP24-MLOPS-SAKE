import base64
from io import BytesIO
import pandas as pd
import joblib
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression

from src.custom_logger import logger

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



def main(X_train, y_train):
    """
    Main function to load data, create model, train it, and save it.
    """

    STAGE_NAME = "Stage: Train"    
    try:        
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")

        # Create model
        model = create_model()
        logger.info("Model created.")

        # Train model
        model = train_model(model, deserialize_object(X_train), deserialize_object(y_train))
        logger.info("Model trained.")
        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")

        return serialize_object(model)

    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e

def deserialize_object(encoded_str) -> pd.DataFrame:
    buffer = BytesIO(base64.b64decode(encoded_str))
    return joblib.load(buffer)

def serialize_object(obj):
    buffer = BytesIO()
    joblib.dump(obj, buffer)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')  # Encode as Base64 string for pydantic

