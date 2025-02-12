import base64
from io import BytesIO
from uuid import uuid4
from src.s3handler import S3Handler, guess_extension, guess_mime_type
from src.utils.env import get_env_var


def push_to_bucket(files: list, prefix: str):
    handler = S3Handler(get_env_var("AWS_BUCKET_NAME"))

    infos = []
    for file in files:
        try:
            content = base64.b64decode(file.content)
        except Exception as e:
           content = file.content.encode('utf-8')

        if not file.name:
            name = str(uuid4())
            mime_type = guess_mime_type(content)
            extension = guess_extension(mime_type)
            file.name = f"{name}{extension}"
        path = f"{prefix}/{file.name}" if prefix else file.name
        infos.append({"full_path": path, "filename": file.name})

        content = BytesIO(content)
        handler.upload_object_from_content(content, path)

    return infos