import os
import subprocess
from unittest.mock import patch, mock_open, call
import pandas as pd
import pytest
import tempfile

from src.data.clean_all import get_env_var, load_processed_dataset, clean_text, read_file_content, make_dataset, \
    check_input_dir, process_dir, get_ocr_text_files, clean_ocr_files, save_cleaned_dataset_for_dir, read_app_mounts, \
    validate_host_uid_gid, update_permissions, set_permissions_of_host_volume_owner, encode_labels, \
    save_cleaned_dataset, clean_all


def test_get_env_var_defined():
    with patch.dict(os.environ, {'MY_VAR': 'value'}):
        assert get_env_var('MY_VAR') == 'value'


def test_get_env_var_not_defined():
    with patch.dict(os.environ, {}, clear = True):
        with pytest.raises(EnvironmentError):
            get_env_var('MY_VAR')


def test_get_env_var_empty():
    with patch.dict(os.environ, {'MY_VAR': ''}):
        with pytest.raises(EnvironmentError):
            get_env_var('MY_VAR')


def test_load_processed_dataset():
    data = {
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    }
    df = pd.DataFrame(data)

    with tempfile.NamedTemporaryFile(delete = False, suffix = '.csv') as tmp_file:
        df.to_csv(tmp_file.name, index = False)
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

    mock_post.assert_called_once_with(api_url, params = {'text': text}, headers = {'Content-Type': 'text/plain'})


@patch('src.data.clean_all.requests.post')
def test_clean_text_failure(mock_post):
    mock_response = mock_post.return_value
    mock_response.status_code = 404

    api_url = 'http://example.com/clean'
    text = 'Some text to clean'

    result = clean_text(api_url, text)

    assert result is None

    mock_post.assert_called_once_with(api_url, params = {'text': text}, headers = {'Content-Type': 'text/plain'})


@patch('builtins.open', new_callable = mock_open, read_data = 'File content')
def test_read_file_content_success(mock_file):
    filename = 'test_file.txt'
    result = read_file_content(filename)

    assert result == 'File content'

    mock_file.assert_called_once_with(filename, 'r', encoding = 'utf-8')


@patch('builtins.open', side_effect = FileNotFoundError)
def test_read_file_content_file_not_found(mock_file):
    filename = 'non_existent_file.txt'

    with pytest.raises(FileNotFoundError):
        read_file_content(filename)

    mock_file.assert_called_once_with(filename, 'r', encoding = 'utf-8')


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
    with patch('os.path.exists', return_value = True):
        ocr_text_dir = '/path/to/existing/dir'
        try:
            check_input_dir(ocr_text_dir)
        except Exception as e:
            pytest.fail(f"check_input_dir raised Exception unexpectedly: {e}")


def test_check_input_dir_not_exists():
    with patch('os.path.exists', return_value = False):
        ocr_text_dir = '/path/to/non_existing/dir'
        with pytest.raises(Exception):
            check_input_dir(ocr_text_dir)


def test_get_ocr_text_files():
    root = '/path/to/ocr_text_dir/category1'
    ocr_text_dir = '/path/to/ocr_text_dir'
    files = ['file1.txt', 'file2.txt', 'file3.jpg', 'file1.jpg', 'file2.png', 'file1.pdf']

    expected_result = [
        'category1/file1.txt',
        'category1/file2.txt'
    ]

    result = get_ocr_text_files(root, ocr_text_dir, files)

    assert result == expected_result


@patch('src.data.clean_all.read_file_content')
@patch('src.data.clean_all.clean_text')
def test_clean_ocr_files(mock_clean_text, mock_read_file_content):
    mock_read_file_content.side_effect = lambda path: f"Content of {os.path.basename(path)}"
    mock_clean_text.side_effect = lambda api_url, content: f"Cleaned {content}"

    api_url = "http://example.com/clean"
    ocr_text_dir = "/path/to/ocr_text_dir"
    ocr_text_files = ["file1.txt", "file2.txt"]

    expected_cleaned_texts = [
        "Cleaned Content of file1.txt",
        "Cleaned Content of file2.txt"
    ]
    result = clean_ocr_files(api_url, ocr_text_dir, ocr_text_files)

    assert result == expected_cleaned_texts

    mock_read_file_content.assert_has_calls([
        call(os.path.join(ocr_text_dir, "file1.txt")),
        call(os.path.join(ocr_text_dir, "file2.txt"))
    ])
    mock_clean_text.assert_has_calls([
        call(api_url, "Content of file1.txt"),
        call(api_url, "Content of file2.txt")
    ])


@patch('src.data.clean_all.save_cleaned_dataset')
@patch('src.data.clean_all.make_dataset')
def test_save_cleaned_dataset_for_dir(mock_make_dataset, mock_save_cleaned_dataset):
    root = "/path/to/ocr_text_dir/class1"
    ocr_text_files = [
        "/path/to/ocr_text_dir/class1/file1.txt",
        "/path/to/ocr_text_dir/class1/file2.txt"
    ]
    cleaned_texts = ["Cleaned text 1", "Cleaned text 2"]
    cleaned_datasets_dir = "/path/to/cleaned_datasets"

    mock_make_dataset.return_value = "mock_dataset"

    expected_class_folder = "class1"
    expected_output_path = os.path.join(cleaned_datasets_dir, expected_class_folder, "cleaned_dataset.csv")

    save_cleaned_dataset_for_dir(root, ocr_text_files, cleaned_texts, cleaned_datasets_dir)

    mock_make_dataset.assert_called_once_with(ocr_text_files, cleaned_texts)
    mock_save_cleaned_dataset.assert_called_once_with("mock_dataset", expected_output_path)


@patch("builtins.open", new_callable = mock_open, read_data = (
        "/dev/sda1 /app/data ext4 rw,relatime 0 0\n"
        "/dev/sda2 /home ext4 rw,relatime 0 0\n"
        "/dev/sda3 /app/config ext4 rw,relatime 0 0\n"
))
def test_read_app_mounts(mock_file):
    result = read_app_mounts()

    expected = ["/app/data", "/app/config"]

    assert result == expected
    mock_file.assert_called_once_with('/proc/mounts', 'r')


@patch("builtins.open", new_callable = mock_open)
def test_read_app_mounts_with_exception(mock_file):
    mock_file.side_effect = IOError("Fichier introuvable")

    result = read_app_mounts()

    assert result == []
    mock_file.assert_called_once_with('/proc/mounts', 'r')


def test_validate_host_uid_gid_success():
    try:
        validate_host_uid_gid(1000, 1000)
    except Exception:
        pytest.fail("validate_host_uid_gid a levé une exception alors qu'il ne devait pas.")


def test_validate_host_uid_gid_failure():
    with pytest.raises(Exception):
        validate_host_uid_gid(None, 1000)

    with pytest.raises(Exception):
        validate_host_uid_gid(1000, None)


@patch("src.data.clean_all.subprocess.run")
def test_update_permissions_success(mock_subprocess_run):
    mock_subprocess_run.return_value = None
    mount_point = "/app/data"
    host_uid = 1000
    host_gid = 1000
    update_permissions(mount_point, host_uid, host_gid)
    mock_subprocess_run.assert_called_once_with(
        ["chown", "-R", f"{host_uid}:{host_gid}", mount_point],
        check = True
    )


@patch("src.data.clean_all.subprocess.run")
def test_update_permissions_failure(mock_subprocess_run):
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode = 1, cmd = "chown -R 1000:1000 /app/data"
    )
    mount_point = "/app/data"
    host_uid = 1000
    host_gid = 1000
    update_permissions(mount_point, host_uid, host_gid)
    mock_subprocess_run.assert_called_once_with(
        ["chown", "-R", f"{host_uid}:{host_gid}", mount_point],
        check = True
    )


@patch("src.data.clean_all.validate_host_uid_gid")
@patch("src.data.clean_all.read_app_mounts")
@patch("src.data.clean_all.update_permissions")
def test_set_permissions_of_host_volume_owner(mock_update_permissions, mock_read_app_mounts,
                                              mock_validate_host_uid_gid):
    mock_validate_host_uid_gid.return_value = None
    mock_read_app_mounts.return_value = ["/app/data", "/app/config"]

    host_uid = 1000
    host_gid = 1000
    set_permissions_of_host_volume_owner(host_uid, host_gid)

    mock_validate_host_uid_gid.assert_called_once_with(host_uid, host_gid)
    mock_read_app_mounts.assert_called_once()
    mock_update_permissions.assert_any_call("/app/data", host_uid, host_gid)
    mock_update_permissions.assert_any_call("/app/config", host_uid, host_gid)


@patch("src.data.clean_all.check_input_dir")
@patch("src.data.clean_all.get_ocr_text_files")
@patch("src.data.clean_all.clean_ocr_files")
@patch("src.data.clean_all.save_cleaned_dataset_for_dir")
@patch("src.data.clean_all.set_permissions_of_host_volume_owner")
@patch("os.walk")
def test_process_dir(mock_os_walk, mock_set_permissions, mock_save_cleaned, mock_clean_ocr_files,
                     mock_get_ocr_text_files, mock_check_input_dir):
    mock_os_walk.return_value = [
        ("/path/to/ocr_text/root", [], ["file1.txt", "file2.txt"]),
    ]
    mock_check_input_dir.return_value = None
    mock_get_ocr_text_files.return_value = ["file1.txt", "file2.txt"]
    mock_clean_ocr_files.return_value = ["cleaned_text1", "cleaned_text2"]
    mock_save_cleaned.return_value = None
    mock_set_permissions.return_value = None

    ocr_text_dir = "/path/to/ocr_text"
    cleaned_datasets_dir = "/path/to/cleaned_datasets"
    api_url = "http://api.url"
    host_uid = 1000
    host_gid = 1000

    process_dir(ocr_text_dir, cleaned_datasets_dir, api_url, host_uid, host_gid)

    mock_check_input_dir.assert_called_once_with(ocr_text_dir)
    mock_get_ocr_text_files.assert_called_once_with("/path/to/ocr_text/root", ocr_text_dir, ["file1.txt", "file2.txt"])
    mock_clean_ocr_files.assert_called_once_with(api_url, ocr_text_dir, ["file1.txt", "file2.txt"])
    mock_save_cleaned.assert_called_once_with("/path/to/ocr_text/root", ["file1.txt", "file2.txt"],
                                              ["cleaned_text1", "cleaned_text2"], cleaned_datasets_dir)
    mock_set_permissions.assert_called_once_with(host_uid, host_gid)


def test_encode_labels():
    mock_mapper = {"category1": 0, "category2": 1}

    ocr_txts = ["category1/file1.txt", "category2/file2.txt", "category3/file3.txt"]

    result = encode_labels(ocr_txts, mock_mapper)

    assert result == [0, 1, -1]


@patch("src.data.clean_all.os.makedirs")
@patch("src.data.clean_all.pd.DataFrame.to_csv")
@patch("src.data.clean_all.logger")
def test_save_cleaned_dataset(mock_logger, mock_to_csv, mock_makedirs):
    mock_to_csv.return_value = None
    mock_makedirs.return_value = None

    cleaned_dataset = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    filepath = "/path/to/output/cleaned_dataset.csv"

    save_cleaned_dataset(cleaned_dataset, filepath)

    mock_logger.info.assert_called_once_with(f"Saving current class to {filepath}...")
    mock_makedirs.assert_called_once_with("/path/to/output", exist_ok = True)
    mock_to_csv.assert_called_once_with(filepath, index = False)


@patch("src.data.clean_all.get_env_var")
@patch("src.data.clean_all.process_dir")
def test_clean_all(mock_process_dir, mock_get_env_var):
    mock_get_env_var.side_effect = lambda key: {
        "DATA_INGESTION_OCR_TEXT_DIR": "/path/to/ocr_text",
        "DATA_CLEANING_CLEAN_ENDPOINT": "http://api.url",
        "DATA_CLEANING_CLEANED_DATASETS_DIR": "/path/to/cleaned_datasets",
        "HOST_UID": "1000",
        "HOST_GID": "1000"
    }[key]
    mock_process_dir.return_value = None

    clean_all()

    mock_process_dir.assert_called_once_with("/path/to/ocr_text", "/path/to/cleaned_datasets", "http://api.url", "1000",
                                             "1000")
