from typing import Optional, Union

from app._types.vector_store_file_object import VectorStoreFileObject
from app.core.rag.index_store_builder.base_index_builder import BaseIndexBuilder


class AppVectorIndexBuilder(BaseIndexBuilder):

    # vs_db:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def save(self, documents: list[VectorStoreFileObject], **kwargs):
        pass

    def clean(self, node_ids: Optional[Union[list[str], list[int]]], **kwargs):
        pass
