import os
import pandas as pd
import numpy as np
from typing import Tuple

def get_original_and_reduced_datasets(original_file:str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load a CSV file, return two DataFrames: the original and a cleaned version.

    Args:
        original_file (str): The path to the original CSV data file.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:
            - df_original: The original DataFrame loaded from the CSV file.
            - df_adjusted: The DataFrame filtered to include only valid images and relevant columns for modeling.
    
    The adjusted DataFrame:
    - Includes only rows where 'inclusion_dataset' is True.
    - Removes unnecessary columns like 'new_type', 'original_type', 'motif_rejet', etc.
    - Displays the distribution of the 'grouped_type' column and the cleaned dataset.
    """
    df_original = pd.read_csv(original_file, encoding='ISO-8859-1', sep=",", index_col = 0)
    df_adjusted = df_original[(df_original['inclusion_dataset'] == True)] # keep only the valid images

    # Merge the similar categories from "new_type" into one "grouped_type"
    # it is now already done in the original file
    #df_adjusted.loc[df_adjusted.new_type.isin(["news_article", "scientific_publication"]), "grouped_type"] = "article"
    #df_adjusted.loc[df_adjusted.new_type.isin(["invoice", "justif_domicile"]), "grouped_type"] = "facture"
    #df_adjusted.loc[df_adjusted.new_type.isin(["email", "letter"]), "grouped_type"] = "correspondance"

    # Remove the column which are not useful for the model
    df_adjusted = df_adjusted.drop(['new_type', 'original_type', 'motif_rejet', 'true_cat', 'inclusion_dataset', 'excluded_types'], axis=1)
    
    print("__________________________")
    print("df_adjusted: reduced_and_clean_dataset:")
    display(df_adjusted.grouped_type.value_counts())
    display(df_adjusted)
    
    return df_original, df_adjusted

if __name__ == "__main__":

    # this is aimed to be copy-pasted into a notebook

    base_path = 'C:/Users/Eddie/DataScientest/oct23_cds_classification_document_donnees/Dataset/01_classification_docs/'
    image_path = base_path + 'final/'
    ocr_path = base_path + 'ocr/'
    csv_path = 'C:/Users/Eddie/DataScientest/SEP24-MLOPS-SAKE/references/'

    df_original, df_working = get_original_and_reduced_datasets(csv_path + 'dataset.csv')
