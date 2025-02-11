import os
from io import BytesIO
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import boto3
import magic
from botocore.exceptions import ClientError

from src.custom_logger import logger


def initialize_s3_handler():
    aws_bucket_name = os.environ.get("AWS_BUCKET_NAME")
    return S3Handler(aws_bucket_name)


def guess_extension(mime_type: str) -> Optional[str]:
    extensions = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/webp": ".webp",
        "image/tiff": ".tiff",
        "application/pdf": ".pdf"
    }
    return extensions.get(mime_type, ".bin")


def guess_mime_type(file_data: bytes) -> Optional[str]:
    return magic.Magic(mime=True).from_buffer(file_data)

def parse_s3_uri(uri: str) -> Tuple[str, str]:
    parsed = urlparse(uri)
    bucket_name = parsed.netloc
    prefix = parsed.path.lstrip('/')
    return bucket_name, prefix


def store_objects( objects_to_store: list ):
    handler = initialize_s3_handler()

    for obj in objects_to_store:
        handler.upload_object(
            obj['file_content'], obj['file_name'], obj['file_mime_type']
        )

    return handler

def download_uri_to_content( uri: str ) -> BytesIO:
    bucket_name, key = parse_s3_uri(uri)
    handler = S3Handler(bucket_name)
    return handler.download_object_to_content(key)

class S3Handler:
    def __init__( self, bucket_name: str ):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'eu-north-1')
        )
        self.bucket_name = bucket_name

    def create_folder( self, folder_name: str ) -> Optional[str]:
        """
        Crée un nouveau sous-dossier dans le bucket S3.
        
        Args:
            folder_name: Nom du dossier à créer (peut inclure des sous-chemins)
            
        Returns:
            str: URI S3 du dossier créé ou None si erreur
        """
        try:
            # S3 n'a pas vraiment de dossiers, on crée un objet vide avec un / à la fin
            folder_path = folder_name.rstrip('/') + '/'
            self.s3_client.put_object(
                Bucket=self.bucket_name, Key=folder_path
            )
            return f"s3://{self.bucket_name}/{folder_path}"
        except ClientError as e:
            print("error")
            logger.error(f"Erreur lors de la création du dossier: {e}")
            return None

    def upload_file( self, file_path: str, s3_key: str ) -> bool:
        """Upload un fichier vers S3"""
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            return True
        except ClientError as e:
            logger.error(f"Erreur lors de l'upload: {e}")
            return False

    def download_directory( self, remote_directory_name ):
        """Télécharge l'intégralité d'un dossier du bucket sur la machine local"""
        local_path = Path("./")
        local_path.mkdir(parents=True, exist_ok=True)

        downloaded_files = {}
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=remote_directory_name
        )
        for obj in response.get('Contents', []):
            key = obj['Key']

            # Handle potential file-like objects and keys with nested paths
            full_local_path = local_path / key

            # Ensure the directory exists
            full_local_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file, handling potential errors
            try:
                # Only attempt to download if it looks like a file (not ending with '/')
                if not key.endswith('/'):
                    self.s3_client.download_file(self.bucket_name, key, str(full_local_path))
                    downloaded_files[key] = str(full_local_path)
                    logger.info(f"Downloaded: {key}")
            except ClientError as e:
                logger.info(f"Error downloading {key}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error with {key}: {e}")

        return downloaded_files

    def upload_directory( self, remote_path, local_directory_name ):
        """Téléverse l'intégralité d'un dossier local vers le bucket distant"""
        # Normalize paths
        local_directory_name = os.path.normpath(local_directory_name)
        remote_path = remote_path.strip('/')

        uploaded_files = []

        try:
            # Check if local directory exists
            if not os.path.exists(local_directory_name):
                raise ValueError(f"Directory not found: {local_directory_name}")

            # Walk through local directory
            for root, _, files in os.walk(local_directory_name):
                for filename in files:
                    # Get local file path
                    local_path = os.path.join(root, filename)

                    # Calculate relative path
                    relative_path = os.path.relpath(local_path, local_directory_name)

                    # Create S3 key
                    if remote_path:
                        s3_key = f"{remote_path}/{relative_path}".replace('\\', '/')
                    else:
                        s3_key = relative_path.replace('\\', '/')

                    try:
                        # Upload file
                        self.s3_client.upload_file(
                            Filename=local_path, Bucket=self.bucket_name, Key=s3_key
                        )
                        uploaded_files.append(s3_key)
                        logger.info(f"Uploaded: {local_path} -> {s3_key}")

                    except Exception as e:
                        logger.error(f"Error uploading {local_path}: {e}")

        except Exception as e:
            logger.error(f"Error during upload process: {e}")

        return uploaded_files

    def folder_exists( self, folder_path: str ) -> bool:
        """
        Vérifie si un dossier existe dans le bucket.
        
        Args:
            folder_path: Chemin du dossier à vérifier
            
        Returns:
            bool: True si le dossier existe, False sinon
        """
        folder_path = folder_path.rstrip('/') + '/'
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=folder_path, MaxKeys=1
            )
            return 'Contents' in response
        except ClientError:
            return False

    def file_exists( self, file_path: str, prefix: str = '' ) -> bool:
        """
        Vérifie si un fichier existe dans le bucket.

        """
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        files = [r['Key'] for r in response.get('Contents', [])]
        return file_path in files

    def download_file( self, file_path: str, local_file_path: str, prefix: str = '' ):
        """Télécharge un fichier depuis la bucket S3 vers la machine locale"""
        if self.file_exists(file_path, prefix):
            self.s3_client.download_file(self.bucket_name, file_path, str(local_file_path))
            return str(local_file_path)
        else:
            return None

    def upload_object( self, file_data, key, mime_type ):
        self.s3_client.upload_fileobj(
            BytesIO(file_data), self.bucket_name, key, ExtraArgs={'ContentType': mime_type}
        )

    def get_bucket_uri(self):
        return f"s3://{self.bucket_name}/"

    def list_objects( self, prefix: str ) -> List[str]:
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        return [content['Key'] for content in response.get('Contents', [])]

    def download_object_to_content( self, key: str ) -> BytesIO:
        buffer = BytesIO()
        self.s3_client.download_fileobj(self.bucket_name, key, buffer)
        buffer.seek(0)
        return buffer

    def upload_object_from_content( self, file_content: BytesIO, key: str ):
        file_content.seek(0)
        self.s3_client.upload_fileobj(file_content, self.bucket_name, key)
