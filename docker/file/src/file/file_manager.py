from uuid import uuid4

from src.s3handler import S3Handler, guess_extension, guess_mime_type
from src.utils.env import get_env_var


def push_to_bucket(files: list, prefix: str):
    handler = S3Handler(get_env_var("AWS_BUCKET_NAME"))

    for file in files:
        if not file.name:
            name = str(uuid4())
            mime_type = guess_mime_type(file.content)
            extension = guess_extension(mime_type)
            file.name = f"{name}{extension}"
        path = f"{prefix}/{file.name}" if prefix else file.name
        handler.upload_object_from_content(file.content, path)