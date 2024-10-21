#%%
import pandas as pd
import joblib 
from imblearn.metrics import classification_report_imbalanced

tfidf_path = '../../data/vectorizers/tfidf.joblib'
model_path = '../../data/models/ovrc.joblib'
X_test_path = '../../data/processed/test/X_test.joblib'
y_test_path = '../../data/processed/test/y_test.joblib'
X_train_path = '../../data/processed/train/X_train.joblib'
y_train_path = '../../data/processed/train/y_train.joblib'

#%%
def load_variables():
     tfidf = joblib.load(tfidf_path)
     model = joblib.load(model_path)
     X_test = joblib.load(X_test_path)
     X_train = joblib.load(X_train_path)
     y_train = joblib.load(y_train_path)
     y_test = joblib.load(y_test_path)
     return tfidf, model, X_test, y_test, X_train, y_train

def transform_dataset(X_test):
     return tfidf.transform(X_test['cleaned_text'])

def predict(X_test):
     y_pred = model.predict(X_test)
     return y_pred

def get_accuracy():
     return model.score(X_test, y_test)

def get_confusion_matrix(y_test, y_pred):
     return pd.crosstab (y_test, y_pred, rownames=['Classe réelle'], colnames=['Classe Prédite'])

def get_classification_report_imbalanced(y_test, y_pred):
    report_classif_imbalanced = classification_report_imbalanced(y_test, y_pred, zero_division=0, output_dict=True)
    df = pd.DataFrame(report_classif_imbalanced).transpose()
    df = df.reset_index()
    return df

#%%
tfidf, model, X_test, y_test, X_train, y_train = load_variables()
X_test = transform_dataset(X_test)
y_pred = predict(X_test)
accuracy = get_accuracy()
confusion_matrix = get_confusion_matrix(y_test, y_pred)
report = get_classification_report_imbalanced(y_test, y_pred)
print(type(report))
#%%
tfidf, model, X_test, y_test = load_variables()
X_test = transform_dataset(X_test)
y_pred = predict(X_test)
accuracy = get_accuracy()
confusion_matrix = get_confusion_matrix(y_test, y_pred)
report = get_classification_report_imbalanced(y_test, y_pred)



#%%
import os
os.getcwd()



# %%
