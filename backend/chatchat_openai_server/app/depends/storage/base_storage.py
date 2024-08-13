from abc import abstractmethod

from app._types.file_object import FileObject


class BaseStorage:

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def save_file(self, filename, _file):
        raise NotImplementedError

    @abstractmethod
    def save_file_part(self, filename, _file):
        raise NotImplementedError

    @abstractmethod
    def read_file_content(self, file_object: FileObject):
        raise NotImplementedError

    @abstractmethod
    def download(self, filename, target_filepath):
        raise NotImplementedError

    @abstractmethod
    def exists_file(self, filename):
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, filename):
        raise NotImplementedError
