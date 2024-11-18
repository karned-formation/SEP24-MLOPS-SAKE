import os
import pytest
from unittest.mock import patch
import pandas as pd
import pytest
import tempfile
import os

from src.data.clean_all import get_env_var, load_processed_dataset


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