import unittest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import numpy as np
from steps.ingest import get_full_text, get_processed_dataset, get_new_images_to_ocerize, save_text_to_file

ocr_endpoint = "http://localhost:8901/txt/blocks-words" # url de l'OCR

class TestIngest(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="mocked text")
    @patch("requests.post")
    def test_get_full_text(self, mock_post, mock_file):
        mock_post.return_value.text = "mocked text"
        result = get_full_text("dummy_image.jpg", ocr_endpoint)
        self.assertEqual(result, "mocked text")
        mock_post.assert_called_once()
        mock_file.assert_called_once_with("dummy_image.jpg", "rb")

    @patch("os.path.isfile")
    @patch("pandas.read_csv")
    @patch("pandas.DataFrame.to_csv")
    def test_get_processed_dataset_existing_file(self, mock_to_csv, mock_read_csv, mock_isfile):
        mock_isfile.return_value = True
        mock_read_csv.return_value = pd.DataFrame({"filename": ["file1.jpg"]})
        result = get_processed_dataset("dummy_path.csv")
        self.assertEqual(result["filename"].iloc[0], "file1.jpg")
        mock_read_csv.assert_called_once_with("dummy_path.csv")
        mock_to_csv.assert_not_called()

    @patch("os.path.isfile")
    @patch("pandas.DataFrame.to_csv")
    def test_get_processed_dataset_new_file(self, mock_to_csv, mock_isfile):
        mock_isfile.return_value = False
        result = get_processed_dataset("dummy_path.csv")
        self.assertTrue("filename" in result.columns)
        self.assertTrue("grouped_type" in result.columns)
        self.assertTrue("full_text" in result.columns)
        self.assertTrue("cleaned_text" in result.columns)
        mock_to_csv.assert_called_once_with("dummy_path.csv", index=False)

    def test_get_new_images_to_ocerize(self):
        raw_dataset = pd.DataFrame({"filename": ["file1.jpg", "file2.jpg", "file3.jpg"]})
        processed_dataset = pd.DataFrame({"filename": ["file1.jpg"]})
        result = get_new_images_to_ocerize(raw_dataset, processed_dataset)
        self.assertEqual(len(result), 2)
        self.assertIn("file2.jpg", result["filename"].values)
        self.assertIn("file3.jpg", result["filename"].values)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_text_to_file(self, mock_file):
        save_text_to_file("mocked text", "dummy_path.txt")
        mock_file.assert_called_once_with("dummy_path.txt", "w")
        mock_file().write.assert_called_once_with("mocked text")

if __name__ == "__main__":
    unittest.main()