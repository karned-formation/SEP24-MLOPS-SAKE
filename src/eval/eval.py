import pandas as pd
import numpy as np
from imblearn.metrics import classification_report_imbalanced
import json
import os
import joblib 

model_path = '../../models/train/ovrc.joblib'
X_test_path = '../../data/processed/test/X_test.joblib'
y_test_path = '../../data/processed/test/y_test.joblib'
metrics_dir = '../../metrics/'

def load_variables(model_path, X_test_path, y_test_path):
    """Load the model, X_test, and y_test from specified file paths."""
    model = joblib.load(model_path)
    X_test = joblib.load(X_test_path)
    y_test = joblib.load(y_test_path)
    return model, X_test, y_test

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

def save_json_metrics(metrics, metrics_dir):
    """Save metrics as a JSON file at the specified file path."""
    file_path = os.path.join(metrics_dir, "scores.json")
    if metrics_dir and not os.path.exists(metrics_dir):
        os.makedirs(metrics_dir)
    with open(file_path, 'w') as json_file:
        json.dump(metrics, json_file)
    print(f"Metrics saved successfully to {file_path}.")

def save_confusion_matrix(confusion_matrix, metrics_dir):
    """Save the confusion matrix to a JSON file."""
    confusion_matrix_path = os.path.join(metrics_dir, "confusion_matrix.json")
    confusion_matrix.to_json(confusion_matrix_path)
    print(f"Confusion matrix saved successfully to {confusion_matrix_path}.")

def main(model_path, X_test_path, y_test_path, metrics_dir):
    """Run model prediction, calculate metrics, and save results."""
    model, X_test, y_test = load_variables(model_path, X_test_path, y_test_path)
    y_pred = model.predict(X_test)
    confusion_matrix = get_confusion_matrix(y_test, y_pred)
    metrics = get_metrics(model, X_test, y_test, y_pred)
    save_json_metrics(metrics, metrics_dir)
    save_confusion_matrix(confusion_matrix, metrics_dir)

# Execute main function
if __name__ == "__main__":
    main(model_path, X_test_path, y_test_path, metrics_dir)