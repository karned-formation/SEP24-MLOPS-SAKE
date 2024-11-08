import pandas as pd
import os
import logging
from pathlib import Path
import sys
import shutil
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.config_manager import ConfigurationManager
from src.custom_logger import logger
from src.check_structure import check_existing_folder, check_existing_file

def structure_raw_data(input_raw_dataset_path, 
                       input_image_dir, 
                       output_raw_dataset_dir,
                       label_mapper):
    logger.info(f"Input - raw DataSet Path (filename with classes) = {input_raw_dataset_path}")
    logger.info(f"Input - Image Dir (contains images) = {input_image_dir}")
    logger.info(f"Output - Raw DataSet Dir (images with one folder per class) = {output_raw_dataset_dir}")

    if not os.path.exists(input_raw_dataset_path):
        logger.error(f"Erreur: {input_raw_dataset_path} n'existe pas ")
        # à revoir
        raise Exception

    if not os.path.isdir(input_image_dir):
        logger.error(f"Erreur: {input_image_dir} n'existe pas ")
        # à revoir
        raise Exception

    if check_existing_folder(output_raw_dataset_dir):
        os.makedirs(output_raw_dataset_dir)

    df = pd.read_csv(input_raw_dataset_path)

    # Création des sous-dossiers et copie des fichiers
    for _, row in df.iterrows():
        filename = row['filename']
        grouped_type = str(label_mapper.get(row['grouped_type'], row['grouped_type'])) # Récupération du code de la classe associée (ou la classe elle-même si non trouvée)
        
        destination_dir = os.path.join(output_raw_dataset_dir, grouped_type)
        os.makedirs(destination_dir, exist_ok=True)  # Création du sous-dossier si inexistant
        
        source_file = os.path.join(input_image_dir, filename)
        destination_file = os.path.join(destination_dir, filename)
    
        if os.path.exists(source_file):
            shutil.copy2(source_file, destination_file)
            #print(f"Copié {filename} dans {destination_dir}")
        else:
            print(f"Le fichier {filename} n'existe pas dans {input_image_dir}")


def main():
    STAGE_NAME = "Stage: Structure_raw"    
    try:        
        logger.info(f">>>>> {STAGE_NAME} / START <<<<<")

        #TODO: il faudrait utiliser les variables d'environnement à la place du config manager
        config_manager = ConfigurationManager()
        data_structure_raw = config_manager.get_data_structure_raw()

        #TODO: il faudrait utiliser les variables d'environnement à la place du config manager
        input_raw_dataset_path = data_structure_raw.raw_dataset_path
        input_image_dir = data_structure_raw.image_dir
        output_raw_dataset_dir = data_structure_raw.raw_dataset_dir

        #TODO: il faudrait utiliser les variables d'environnement à la place du config manager
        label_mapper = config_manager.get_label_encoding_config().__dict__
        print(label_mapper)
        structure_raw_data(input_raw_dataset_path, 
                        input_image_dir, 
                        output_raw_dataset_dir,
                        label_mapper)

        logger.info(f">>>>> {STAGE_NAME} / END successfully <<<<<")
    except Exception as e:
        logger.error(f"{STAGE_NAME} / An error occurred : {str(e)}")
        raise e

if __name__ == '__main__':
    main()