import joblib
from config import MODEL_PATH, VECTORIZER_PATH
from src.custom_logger import logger


def predict( data: str ):
    """Main function to handle the prediction process."""
    try:
        logger.info("Starting the prediction process.")
        vectorizer = joblib.load(VECTORIZER_PATH)['vectorizer']
        model = joblib.load(MODEL_PATH)
        data_vectorized = vectorizer.transform([data])
        probabilities = model.predict_proba(data_vectorized)
        logger.info("Prediction process completed successfully.")
        return probabilities

    except Exception as e:
        logger.error(f"An error occurred during the prediction process: {e}")
        raise
