import os
from app.extensions.storage.base_storage import BaseStorage
from app.services.exceptions.file_exception import FileNotExistsException


class LocalStorage(BaseStorage):
    def __init__(self, config):
        super().__init__(config)
        self.upload_folder = config.get('upload_folder')
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def save_file(self, filename, _file):
        store_file_path = os.path.join(self.upload_folder, filename)
        content = _file.read()
        with open(store_file_path, "wb") as f:
            f.write(content)
        return store_file_path, len(content)

    def save_file_part(self, filename, _file):
        # 实现文件分片上传的逻辑
        # Example: Append the new part to the existing file
        store_file_path = os.path.join(self.upload_folder, filename)
        with open(store_file_path, "ab") as f:
            f.write(_file.read())
        return store_file_path

    def read_file_content(self, file_object):
        store_file_path = file_object.store_file_path
        if not os.path.exists(store_file_path):
            raise FileNotExistsException()
        with open(store_file_path, "rb") as file:
            content = file.read()
        return content

    def download(self, file_object, target_filepath):
        store_file_path = file_object.store_file_path
        if not os.path.exists(store_file_path):
            raise FileNotExistsException()
        with open(store_file_path, "rb") as source_file:
            with open(target_filepath, "wb") as target_file:
                target_file.write(source_file.read())

    def exists_file(self, file_object):
        store_file_path = file_object.store_file_path
        return os.path.exists(store_file_path)

    def delete_file(self, file_object):
        store_file_path = file_object.store_file_path
        if os.path.exists(store_file_path):
            os.remove(store_file_path)
        else:
            raise FileNotExistsException()
