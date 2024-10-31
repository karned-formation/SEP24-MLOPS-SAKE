from src.config import CONFIG_FILE_PATH
from src.common_utils import read_yaml, create_directories
from src.custom_logger import logger
from src.entity import (DataIngestionConfig, 
                    DataCleaningConfig, 
                    DataPreprocessingConfig, 
                    ModelTrainingConfig, 
                    ModelEvaluationConfig, 
                    LabelEncodingConfig)


class ConfigurationManager:
    def __init__(
        self,
        config_filepath = CONFIG_FILE_PATH):
        self.config = read_yaml(config_filepath)

            
    def get_data_ingestion_config(self) -> DataIngestionConfig:
          config = self.config.data_ingestion

          create_directories([config.image_dir, config.ocr_text_dir])

          data_ingestion_config = DataIngestionConfig(
                ocr_endpoint = config.ocr_endpoint,
                image_dir = config.image_dir,
                raw_dataset_path = config.raw_dataset_path,
                processed_dataset_path = config.processed_dataset_path, 
                ocr_text_dir = config.ocr_text_dir
          )

          return data_ingestion_config
    

    def get_data_cleaning_config(self) -> DataCleaningConfig:
        config = self.config.data_cleaning

        create_directories([config.ocr_text_dir, config.cleaned_dir])

        data_cleaning_config = DataCleaningConfig(
            clean_endpoint = config.clean_endpoint,
            ocr_text_dir = config.ocr_text_dir,
            cleaned_dir = config.cleaned_dir,
            processed_dataset_path = config.processed_dataset_path,
            cleaned_dataset_path = config.cleaned_dataset_path
        )
        
        return data_cleaning_config
    
    def get_data_preprocessing_config(self) -> DataPreprocessingConfig:
        config = self.config.data_preprocessing

        data_preprocessing_config = DataPreprocessingConfig(
            cleaned_dataset_path = config.cleaned_dataset_path,
            tfidf_vectorizer_path = config.tfidf_vectorizer_path,
            X_train_path = config.X_train_path,
            X_test_path = config.X_test_path,
            y_train_path = config.y_train_path,
            y_test_path = config.y_test_path
        )

        return data_preprocessing_config

    def get_label_encoding_config(self) -> LabelEncodingConfig:
        config = self.config.label_encoder_mapping

        label_encoding_config = LabelEncodingConfig(
            facture = config.facture,
            id_pieces = config.id_pieces,
            resume = config.resume
        )

        return label_encoding_config