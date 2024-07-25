from abc import ABC

from chatchat.server.services.knowledge_base.file_manager.base import FileManager


class MinioFileManager(FileManager, ABC):
    ...
