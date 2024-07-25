from abc import ABC, abstractmethod
from typing import List

from fastapi import UploadFile


class FileManager(ABC):

    @abstractmethod
    def create_file(self, _file: UploadFile):
        pass

    @abstractmethod
    def read_file(self, file_id):
        pass

    @abstractmethod
    def write_file(self, file_id, content):
        pass

    @abstractmethod
    def delete_file(self, file_id):
        pass

    @abstractmethod
    def upload_file(self, files: List[UploadFile], file_metas: List[dict]):
        pass
