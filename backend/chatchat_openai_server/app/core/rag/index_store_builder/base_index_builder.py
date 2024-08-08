from abc import abstractmethod
from typing import Optional, Union

from app.core.rag._types.base_document import BaseDocument


class BaseIndexBuilder:
    def __init__(self, index_builder_config):
        self.index_builder_config = index_builder_config

    @abstractmethod
    def save_process(self, documents: list[BaseDocument], **kwargs):
        ...

    @abstractmethod
    def clean(self, node_ids: Optional[Union[list[str], list[int]]], **kwargs):
        ...
