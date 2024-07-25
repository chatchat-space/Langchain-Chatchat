from abc import ABC
from typing import List

from fastapi import UploadFile

from chatchat.server.services.knowledge_base.file_manager.base import FileManager


class LocalFileManager(FileManager, ABC):
    def create_file(self, _file: UploadFile):
        pass

    def write_file(self, file_id,content):
        pass

    def read_file(self, file_id):
        pass

    def delete_file(self, file_id):
        pass

    def upload_file(self, files: List[UploadFile], file_metas):
        pass
