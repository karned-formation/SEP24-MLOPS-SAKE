import pytest
from src.utils.env import get_env_var

def test_retrieves_existing_env_var(monkeypatch):
    monkeypatch.setenv('EXISTING_VAR', 'value')
    assert get_env_var('EXISTING_VAR') == 'value'

def test_raises_error_for_nonexistent_env_var(monkeypatch):
    monkeypatch.delenv('NONEXISTENT_VAR', raising=False)
    with pytest.raises(EnvironmentError):
        get_env_var('NONEXISTENT_VAR')

def test_raises_error_for_empty_env_var(monkeypatch):
    monkeypatch.setenv('EMPTY_VAR', '')
    with pytest.raises(EnvironmentError):
        get_env_var('EMPTY_VAR')