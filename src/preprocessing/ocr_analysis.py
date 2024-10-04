import pandas as pd
import numpy as np
import os
from typing import Tuple

import cv2

import re

from nltk.tokenize import word_tokenize

#from nltk.stem.snowball import FrenchStemmer, EnglishStemmer
#from PIL import Image
#from PIL import ImageFilter

class OCR:
    def __init__(self) -> None:
        return None

    #------------------------------------------------------------------------
    # Methods (refactored)
    #------------------------------------------------------------------------
    def ocr_extract_fastNlMeansDenoising_and_pytesseract__one_image (self, img_filename: str) -> str:
        """function to extract text features with the help of fastNlMeansDenoising and pytesseract
    
        Args:
            img_filename (str): image to read (including its path)
    
        Returns:
            str: text_denoised
        """
        print("img filename:", img_filename)
        img = cv2.imread(img_filename, cv2.IMREAD_GRAYSCALE)
        img = cv2.fastNlMeansDenoising(img, None, 20, 7, 21)
        assert(False) # ne pas exécuter ce code car la librairie pytesseract n'est pas utilisée
        # textdenoised = pytesseract.image_to_string(img)
        textdenoised = textdenoised.strip()
        return textdenoised

    #------------------------------------------------------------------------
    def ocr_extract_one_image_one_feature (self, img_filename: str) -> str:
        return self.ocr_extract_fastNlMeansDenoising_and_pytesseract__one_image (img_filename)
    
    #------------------------------------------------------------------------
    def ocr_extract_all_images_from_path_to_df(self, img_path: str, df_filenames: pd.DataFrame) -> pd.DataFrame:
        """function that will pass every image in ocr_opencv to extract features for a TFidfVectorization.
    
        Args:
            img_path (str): the path for the list of images to ocerise.
            df_filenames (pd.DataFrame): dataframe containing the list of 'filename' as index
    
        Returns:
            pd.DataFrame: return the dataframe passed in argument completed with extracted OCR
        """
        list_filenames= df_filenames.index.to_list()
        df_filenames.loc[:,'text'] = [self.ocr_extract_one_image_one_feature(img_path + filename) 
                                      for filename in list_filenames]
        return df_filenames

    #------------------------------------------------------------------------
    def load_existing_or_update_OCR_extraction(self,
                                               img_path: str, 
                                               df_filenames: pd.DataFrame, 
                                               OCR_file_loaded_from_or_saved_to:str
    ) -> pd.DataFrame:
        """
        Args:
            img_path (str): the path for the list of images to ocerise.
            df_filenames (pd.DataFrame): dataframe containing the dataset
                the list of 'filename' as index
                the column 'grouped_type' for the classes
            OCR_file_loaded_from_or_saved_to : the file with previously extracted features
    
        Returns:
            pd.DataFrame: return the dataframe passed in argument completed with extracted OCR
        """
        if not os.path.exists(OCR_file_loaded_from_or_saved_to):
            print (OCR_file_loaded_from_or_saved_to, "does NOT EXIST => Creation and extract OCR from all images")
            df_with_extracted_OCR = self.ocr_extract_all_images_from_path_to_df(img_path, df_filenames)
            df_with_extracted_OCR.to_csv(OCR_file_loaded_from_or_saved_to)
        else:
            # print (OCR_file_loaded_from_or_saved_to, "already EXIST \n=> extract OCR only for unknown images (do not redo for already known image)")
            # Read OCR extraction for known images
            df_with_extracted_OCR_known = pd.read_csv(OCR_file_loaded_from_or_saved_to, sep=',', index_col=0)
    
            # Perform the OCR extraction for unknown images
            df_filenames_unkwown_to_do = df_filenames.drop(df_with_extracted_OCR_known.index, axis = 0, errors='ignore') # au cas où des images sont supprimées
            df_with_extracted_OCR_unknown = self.ocr_extract_all_images_from_path_to_df(img_path, df_filenames_unkwown_to_do)
    
            df_with_extracted_OCR = pd.concat([df_with_extracted_OCR_known, df_with_extracted_OCR_unknown], axis = 0)
            df_with_extracted_OCR = df_with_extracted_OCR.loc[df_filenames.index] ## au cas où des images sont supprimées
            df_with_extracted_OCR.grouped_type = df_filenames.grouped_type ## pour réaligner les grouped_type qui peuvent avoir changer
            # do not change the original file : df_with_extracted_OCR.to_csv(OCR_file_loaded_from_or_saved_to)
            # print (OCR_file_loaded_from_or_saved_to, "UPDATED with new images (if any)")
        
        df_with_extracted_OCR.fillna("", inplace = True)
        return df_with_extracted_OCR

if __name__ == "__main__":
    pass