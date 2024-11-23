import unittest
from unittest.mock import patch, mock_open, MagicMock
from src import s3handler
import os
from datetime import datetime

class TestS3(unittest.TestCase):

    def test_create_sub_folder(self):
        bucket_name = os.environ.get('AWS_BUCKET_NAME')
        handler = s3handler.S3Handler(bucket_name)
        timestamp = datetime.timestamp(datetime.now())
        s3_uri = handler.create_folder(f"prediction_{timestamp}")
        assert s3_uri == f's3://datascientest-mlops-classif/prediction_{timestamp}/'

    # upload file

if __name__ == "__main__":
    unittest.main()