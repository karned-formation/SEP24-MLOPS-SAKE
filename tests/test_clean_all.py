from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import pytest
import tempfile
import os

from src.data.clean_all import get_env_var, load_processed_dataset, clean_text, read_file_content, make_dataset, \
    check_input_dir, process_dir


def test_get_env_var_defined():
    with patch.dict(os.environ, {'MY_VAR': 'value'}):
        assert get_env_var('MY_VAR') == 'value'

def test_get_env_var_not_defined():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(EnvironmentError) as excinfo:
            get_env_var('MY_VAR')
        assert str(excinfo.value) == "La variable d'environnement 'MY_VAR' n'est pas définie ou est vide."

def test_get_env_var_empty():
    with patch.dict(os.environ, {'MY_VAR': ''}):
        with pytest.raises(EnvironmentError) as excinfo:
            get_env_var('MY_VAR')
        assert str(excinfo.value) == "La variable d'environnement 'MY_VAR' n'est pas définie ou est vide."

def test_load_processed_dataset():
    data = {
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    }
    df = pd.DataFrame(data)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        df.to_csv(tmp_file.name, index=False)
        tmp_file_path = tmp_file.name

    try:
        loaded_df = load_processed_dataset(tmp_file_path)
        pd.testing.assert_frame_equal(loaded_df, df)
    finally:
        os.remove(tmp_file_path)

def test_load_processed_dataset_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_processed_dataset('non_existent_file.csv')

@patch('src.data.clean_all.requests.post')
def test_clean_text_success(mock_post):
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.text = 'Cleaned text'

    api_url = 'http://example.com/clean'
    text = 'Some text to clean'

    result = clean_text(api_url, text)

    assert result == 'Cleaned text'

    mock_post.assert_called_once_with(api_url, params={'text': text}, headers={'Content-Type': 'text/plain'})

@patch('src.data.clean_all.requests.post')
def test_clean_text_failure(mock_post):
    mock_response = mock_post.return_value
    mock_response.status_code = 404

    api_url = 'http://example.com/clean'
    text = 'Some text to clean'

    result = clean_text(api_url, text)

    assert result is None

    mock_post.assert_called_once_with(api_url, params={'text': text}, headers={'Content-Type': 'text/plain'})

@patch('builtins.open', new_callable=mock_open, read_data='File content')
def test_read_file_content_success(mock_file):
    filename = 'test_file.txt'
    result = read_file_content(filename)

    assert result == 'File content'

    mock_file.assert_called_once_with(filename, 'r', encoding='utf-8')

@patch('builtins.open', side_effect=FileNotFoundError)
def test_read_file_content_file_not_found(mock_file):
    filename = 'non_existent_file.txt'

    with pytest.raises(FileNotFoundError):
        read_file_content(filename)

    mock_file.assert_called_once_with(filename, 'r', encoding='utf-8')

def test_make_dataset():
    ocr_txts = [
        'category1/file1.txt',
        'category2/file2.txt',
        'category1/file3.txt'
    ]
    cleaned_txts = [
        'Cleaned text 1',
        'Cleaned text 2',
        'Cleaned text 3'
    ]

    expected_df = pd.DataFrame({
        'filename': ['category1/file1', 'category2/file2', 'category1/file3'],
        'cleaned_text': ['Cleaned text 1', 'Cleaned text 2', 'Cleaned text 3'],
        'category': ['category1', 'category2', 'category1']
    })

    result_df = make_dataset(ocr_txts, cleaned_txts)

    pd.testing.assert_frame_equal(result_df, expected_df)

def test_make_dataset_empty():
    ocr_txts = []
    cleaned_txts = []

    expected_df = pd.DataFrame({
        'filename': [],
        'cleaned_text': [],
        'category': []
    })

    result_df = make_dataset(ocr_txts, cleaned_txts)

    pd.testing.assert_frame_equal(result_df, expected_df)

def test_check_input_dir_exists():
    with patch('os.path.exists', return_value=True):
        ocr_text_dir = '/path/to/existing/dir'
        try:
            check_input_dir(ocr_text_dir)
        except Exception as e:
            pytest.fail(f"check_input_dir raised Exception unexpectedly: {e}")

def test_check_input_dir_not_exists():
    with patch('os.path.exists', return_value=False):
        ocr_text_dir = '/path/to/non_existing/dir'
        with pytest.raises(Exception, match="OCR text directory not found"):
            check_input_dir(ocr_text_dir)