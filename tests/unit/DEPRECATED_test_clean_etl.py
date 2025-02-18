from steps.clean_text import read_file_content, process_dataset, save_cleaned_dataset, load_processed_dataset
import pandas as pd
import os
import unittest
from typing import Any, Dict
from unittest.mock import patch
    
class TestCleanText(unittest.TestCase):

    def test_load_processed_dataset(self) -> None:
        data: Dict[str, Any] = {'text': ["this is a test", "another test with punctuation"]}
        df = pd.DataFrame(data)
        df.to_csv('cleaned_dataset.csv', index=False)
        loaded_df = load_processed_dataset('cleaned_dataset.csv')
        pd.testing.assert_frame_equal(loaded_df, df)
        os.remove('cleaned_dataset.csv')

    def test_read_file_content(self) -> None:
        with patch('builtins.open', unittest.mock.mock_open(read_data='test data')) as mock_file:
            content = read_file_content('test.txt')
            self.assertEqual(content, 'test data')
    
    def test_process_dataset(self) -> None:
        with open("temp_ocerized.txt", "w") as f:
            f.write("""- - V - Française A
                    Nationalisé
                    M 4 - - a - -
                    le. - Néle)
                    A <<<< - << <<<<< - V - -
                    - à - - - IQU - Nom BC DIDENTITE B TIONALE
                    4 1,82 - - Sexe a titulaine Taille - Signature
                    Prénomiss""")

        df = pd.DataFrame({'full_text': ['temp_ocerized.txt'], 'grouped_type': ['id_pieces'], 'filename': ['test.jpg']})
        cleaned_df = process_dataset(df, 'http://localhost:8903/clean')
        self.assertEqual(cleaned_df['cleaned_text'][0], 'français nationaliser néle iqu nom bc didentite tional 1,82 sexe titulain taille signature prénomis')
        os.remove('temp_ocerized.txt')

    def test_save_cleaned_dataset(self) -> None:
        data: Dict[str, Any] = {'text': ["this is a test", "another test with punctuation"]}
        df = pd.DataFrame(data)
        save_cleaned_dataset(df, 'cleaned_dataset.csv')
        loaded_df = pd.read_csv('cleaned_dataset.csv')
        pd.testing.assert_frame_equal(loaded_df, df)
        os.remove('cleaned_dataset.csv')

if __name__ == '__main__':
    unittest.main()
