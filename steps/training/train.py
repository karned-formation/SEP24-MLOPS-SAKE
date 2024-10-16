import pandas as pd
import joblib
from sklearn.calibration import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

dataset_path = '/app/data/dataset.csv' 
model_path = '/app/models/ovrc.joblib'

def split(dataset_path: str):
    df = pd.read_csv(dataset_path)
    X = df.drop(['type'], axis = 1)
    y = df['type']
    labelEncoder = LabelEncoder()
    y = labelEncoder.fit_transform(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42, stratify = y)
    return X_train, y_train

def tfidfVectorizer_transform(X_train):
    tfidfVectorizer_transformer =  TfidfVectorizer(
    analyzer = 'char_wb', 
    max_features = 70000, # former: 100000
    ngram_range = (1,11), # former: (1,15) 
    max_df = .3 # former: .5
    )
    X_train = tfidfVectorizer_transformer.fit_transform(X_train['text'])
    return X_train

def create_model():
    model_LogisticRegression = LogisticRegression(class_weight='balanced', n_jobs=-1, 
                            C=100,
                            multi_class= 'auto'
                            )
    model = OneVsRestClassifier(estimator = model_LogisticRegression, n_jobs=-1)
    return model

def save_model(model, model_path):
    joblib.dump(model, model_path)


def train(dataset_path: str, model_path: str):
    X_train, y_train = split(dataset_path)
    X_train = tfidfVectorizer_transform(X_train)
    model = create_model()
    model.fit(X_train, y_train)
    save_model(model, model_path)      