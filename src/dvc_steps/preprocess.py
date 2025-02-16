from src.custom_logger import logger
import os
import joblib

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value


def main() -> None:
    try:
        STAGE_NAME = "Stage: Pre-Processing"    
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")
        clean_dir_path = get_env_var("DATA_CLEANING_CLEANED_DATASETS_DIR")

        X_train_path = get_env_var("DATA_PREPROCESSING_X_TRAIN_PATH")
        X_test_path = get_env_var("DATA_PREPROCESSING_X_TEST_PATH")
        y_train_path = get_env_var("DATA_PREPROCESSING_Y_TRAIN_PATH")
        y_test_path = get_env_var("DATA_PREPROCESSING_Y_TEST_PATH")

        tfidf_vectorizer_path = get_env_var("DATA_PREPROCESSING_TFIDF_VECTORIZER_PATH")
        
        
        # Split the dataset into train and test sets
        X_train, X_test, y_train, y_test = split_dataset(clean_dir_path)
        logger.info(f"y_test shape : {y_test.shape}")
        logger.info(f"y_train shape : {y_train.shape}")
        
        # Fit TF-IDF vectorizer on the training data
        fitted_vectorizer = fit_tfidf_vectorizer(X_train)
        
        # Transform both train and test sets
        X_train_vectorized = transform_with_tfidf(fitted_vectorizer, X_train)
        X_test_vectorized = transform_with_tfidf(fitted_vectorizer, X_test)

        # Prepare variables to save, specifying the directory for each
        variables_to_save = {
            'X_train': (X_train_vectorized, X_train_path),
            'X_test': (X_test_vectorized, X_test_path),
            'y_train': (y_train, y_train_path),
            'y_test': (y_test, y_test_path),
            'tfid_vectorizer': (fitted_vectorizer, tfidf_vectorizer_path)
        }

        # Save the transformed data and labels using Joblib
        save_variables_in_directories(variables_to_save)

        # Save the fitted TF-IDF vectorizer
        save_vectorizer(fitted_vectorizer, tfidf_vectorizer_path)

        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")
            
    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e
    
def save_vectorizer(vectorizer, tfidf_vectorizer_path: str) -> None:
    """
    Save a trained TF-IDF vectorizer to the specified path, 
    along with metadata about Python and Joblib versions.

    Args:
        vectorizer (TfidfVectorizer): The trained TF-IDF vectorizer to save.
        tfidf_vectorizer_path (str): The file path where the vectorizer will be saved.
    """
    # Ensure the directory exists
    directory = os.path.dirname(tfidf_vectorizer_path)
    os.makedirs(directory, exist_ok=True)

    # Prepare metadata about the environment
    metadata = {
        'python_version': sys.version,
        'joblib_version': joblib.__version__
    }
    logger.info(metadata)

    # Save vectorizer with metadata
    joblib.dump(vectorizer, tfidf_vectorizer_path)
    logger.info(f"Vectorizer saved to {tfidf_vectorizer_path} with metadata: {metadata}")

def save_variables_in_directories(variables: dict) -> None:
    """
    Serialize and save multiple variables using Joblib.

    Args:
        variables (dict): A dictionary where keys are variable names, and values are
                          tuples containing (variable, directory_path).
    """
    # Iterate over the dictionary and save each variable in its respective directory
    for var_name, (var_value, file_path) in variables.items():
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)

        # Save the variable
        joblib.dump(var_value, file_path)
        logger.info(f"Variable '{var_name}' saved to {file_path}")