#%%
import pandas as pd
import numpy as np
from imblearn.metrics import classification_report_imbalanced
import json
import os
import joblib 

model_path = '../../data/models/ovrc.joblib'
X_test_path = '../../data/processed/test/X_test.joblib'
y_test_path = '../../data/processed/test/y_test.joblib'
metrics_path = '../../metrics/scores.json'
confusion_matrix_path = '../../metrics/confusion_matrix.json'

def load_variables():
     model = joblib.load(model_path)
     X_test = joblib.load(X_test_path)
     y_test = joblib.load(y_test_path)
     return model, X_test, y_test

def get_accuracy(model, X_test, y_test):
     return model.score(X_test, y_test)

def get_confusion_matrix(y_test, y_pred):
     return pd.crosstab (y_test, y_pred, rownames=['Classe réelle'], colnames=['Classe Prédite'])

def convert_numpy_types(obj):
    """
    Recursively converts NumPy data types (e.g., np.float64, np.int64) to native Python types 
    (e.g., float, int) within a given data structure (dict, list, or other).
    """
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

def get_metrics(y_test, y_pred):
    report = classification_report_imbalanced(y_test, y_pred, output_dict=True)
    report['accuracy'] = get_accuracy(model, X_test, y_test)
    report = convert_numpy_types(report)
    json_report = json.dumps(report, indent=4)
    print(json_report)
    return json_report

def save_json_metrics(metrics, file_path):
    # Crée le répertoire s'il n'existe pas
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    # Sauvegarde les métriques au format JSON
    with open(file_path, 'w') as json_file:
        json.dump(metrics, json_file, indent=4, ensure_ascii=False)
    print(f"Metrics saved successfully to {file_path}.")

def save_confusion_matrix(confusion_matrix, confusion_matrix_path):
    confusion_matrix.to_json(confusion_matrix_path)
    print(f"Confusion matrix saved successfully to {confusion_matrix_path}.")

#%%
model, X_test, y_test = load_variables()
y_pred = model.predict(X_test)
confusion_matrix = get_confusion_matrix(y_test, y_pred)
metrics = get_metrics(y_test, y_pred)
save_json_metrics(metrics, metrics_path)
save_confusion_matrix(confusion_matrix, confusion_matrix_path)

# %%
