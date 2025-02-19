import base64
from io import BytesIO
import pandas as pd
import numpy as np
from imblearn.metrics import classification_report_imbalanced
import joblib 
import traceback
from src.custom_logger import logger

def get_accuracy(model, X_test, y_test):
    """Calculate and return model accuracy on the test data."""
    return model.score(X_test, y_test)

def get_confusion_matrix(y_test, y_pred):
    """Generate a confusion matrix from true and predicted labels."""
    return pd.crosstab(y_test, y_pred, rownames=['True Class'], colnames=['Predicted Class'])

def convert_numpy_types(obj):
    """Convert NumPy types in an object to native Python types recursively."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, np.float64) or isinstance(obj, np.float32):
        return float(obj)
    elif isinstance(obj, np.int64) or isinstance(obj, np.int32):
        return int(obj)
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

def get_metrics(model, X_test, y_test, y_pred):
    """Compute classification metrics, convert types, and return as JSON."""
    report = classification_report_imbalanced(y_test, y_pred, output_dict=True)
    report['accuracy'] = get_accuracy(model, X_test, y_test)
    report = convert_numpy_types(report)
    return report


def evaluate(model, X_test, y_test):
    """Evaluate the model and save the metrics."""    
    logger.info("Evaluating the model...")
    y_pred = model.predict(X_test)   
    scores = get_metrics(model, X_test, y_test, y_pred)
    confusion_matrix = get_confusion_matrix(y_test, y_pred).to_dict()
    logger.info("Model evaluation complete. Accuracy: {:.2f}%".format(scores['accuracy']*100))
    return scores, confusion_matrix

def deserialize_object(encoded_str) -> pd.DataFrame:
    buffer = BytesIO(base64.b64decode(encoded_str))
    return joblib.load(buffer)

def main(X_test, y_test, model):
    """Run model prediction, calculate metrics, and save results."""  

    STAGE_NAME = "Stage: EVAL"   
    try:
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")       
        scores, confusion_matrix = evaluate(deserialize_object(model), deserialize_object(X_test), deserialize_object(y_test))
        logger.info(f">>>>> {STAGE_NAME} / END <<<<<")

        print(scores)
        print(confusion_matrix)
        return scores, confusion_matrix
    except Exception as e:
        logger.error(f"Erreur lors de l'évaluation du modèle : {traceback.format_exc()}")
        raise e
