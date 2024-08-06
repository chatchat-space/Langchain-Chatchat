import os

from app.extensions.storage.base_storage import BaseStorage
from app.services.exceptions.file_exception import FileNotExistsException


class LocalStorage(BaseStorage):
    def __init__(self, config):
        super().__init__(config)
        self.upload_folder = config.get('upload_folder')

    def save_file(self, filename, _file):
        store_file_path = f'{self.upload_folder}/{filename}'
        content = _file.read()
        with open(store_file_path, "wb") as f:
            f.write(content)
        return store_file_path, len(content)

    def save_file_part(self, filename, _file):
        # 实现文件分片上传的逻辑
        pass

    def read_file_content(self, file_object):
        store_file_path = file_object.store_file_path
        if not os.path.exists(store_file_path):
            raise FileNotExistsException()
        with open(store_file_path, "rb") as file:
            content = file.read()
        return content

    def download(self, filename, target_filepath):
        pass

    def exists_file(self, filename):
        pass

    def delete_file(self, filename):
        pass
