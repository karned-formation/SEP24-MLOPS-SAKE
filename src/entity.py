from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DataStructureRawConfig:
    raw_dataset_path: Path
    image_dir: Path
    raw_dataset_dir: Path

@dataclass(frozen=True)
class DataIngestionConfig:
    ocr_endpoint: str
    raw_dataset_dir: Path
    ocr_text_dir: Path

@dataclass(frozen=True)
class DataCleaningConfig:
    clean_endpoint: str
    ocr_text_dir: Path
    cleaned_datasets_dir: Path

@dataclass(frozen=True)
class DataPreprocessingConfig:
    cleaned_datasets_dir: Path
    tfidf_vectorizer_path: Path
    train_data_dir: Path
    test_data_dir: Path

@dataclass(frozen=True)
class ModelTrainingConfig:
    train_data_dir: Path
    model_path: Path

@dataclass(frozen=True)
class ModelEvaluationConfig:
    test_data_dir: Path
    model_path: Path
    evaluation_results_dir: Path

@dataclass(frozen=True)
class LabelEncodingConfig:
    facture: int
    id_pieces: int
    resume: int
