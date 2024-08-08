import os

from app.extensions.storage.base_storage import BaseStorage
from app.types.file_object import FileObject

from minio import Minio
from minio.error import S3Error
from app.extensions.storage.base_storage import BaseStorage
from app.types.file_object import FileObject
from app.services.exceptions.file_exception import FileNotExistsException


class MinioStorage(BaseStorage):
    def __init__(self, config):
        super().__init__(config)
        self.client = Minio(
            config['endpoint'],
            access_key=config['access_key'],
            secret_key=config['secret_key'],
            secure=config.get('secure', True)
        )
        self.default_bucket = config.get('default_bucket')

    def save_file(self, filename, _file):
        try:
            file_path = f'{filename}'

            # Determine the size of the file
            _file.seek(0, os.SEEK_END)
            size = _file.tell()
            _file.seek(0)

            self.client.put_object(
                self.default_bucket,
                filename,
                _file,
                length=size,  # Pass the actual size of the file
                part_size=10 * 1024 * 1024  # 10MB parts
            )
            return file_path, size
        except S3Error as e:
            raise Exception(f"Failed to save file: {str(e)}")

    def save_file_part(self, filename, _file):
        # MinIO already supports multipart upload. You can use presigned URLs or MinIO SDK multipart APIs.
        pass

    def read_file_content(self, file_object: FileObject):
        try:
            response = self.client.get_object(self.default_bucket, file_object.store_file_path)
            print(response)
            content = response.read()
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            raise FileNotExistsException(f"Failed to read file content: {str(e)}")

    def download(self, file_object: FileObject, target_filepath):
        try:
            self.client.fget_object(self.default_bucket, file_object.store_file_path, target_filepath)
        except S3Error as e:
            raise FileNotExistsException(f"Failed to download file: {str(e)}")

    def exists_file(self, file_object: FileObject):
        try:
            self.client.stat_object(self.default_bucket, file_object.store_file_path)
            return True
        except S3Error:
            return False

    def delete_file(self, file_object: FileObject):
        try:
            self.client.remove_object(self.default_bucket, file_object.store_file_path)
        except S3Error as e:
            raise FileNotExistsException(f"Failed to delete file: {str(e)}")
