from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DataIngestionConfig:
    ocr_endpoint: str
    image_dir: Path
    raw_dataset_path: Path
    processed_dataset_path: Path
    ocr_text_dir: Path

@dataclass(frozen=True)
class DataCleaningConfig:
    clean_endpoint: str
    ocr_text_dir: Path
    cleaned_dir: Path
    processed_dataset_path: Path
    cleaned_dataset_path: Path

@dataclass(frozen=True)
class DataPreprocessingConfig:
    cleaned_dataset_path: Path
    tfidf_vectorizer_path: Path
    X_train_path: Path
    X_test_path: Path
    y_train_path: Path
    y_test_path: Path

@dataclass(frozen=True)
class ModelTrainingConfig:
    X_train_path: Path
    y_train_path: Path
    model_path: Path

@dataclass(frozen=True)
class ModelEvaluationConfig:
    X_test_path: Path
    y_test_path: Path
    model_path: Path
    evaluation_results_path: Path

@dataclass(frozen=True)
class LabelEncodingConfig:
    facture: int
    id_pieces: int
    resume: int
