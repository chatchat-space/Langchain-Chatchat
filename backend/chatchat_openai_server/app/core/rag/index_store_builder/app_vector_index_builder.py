from typing import Optional, Union

from app.core.rag.index_store_builder.base_index_builder import BaseIndexBuilder
from app.types.index_store_file_object import IndexStoreFileObject


class AppVectorIndexBuilder(BaseIndexBuilder):

    # vs_db:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def save(self, documents: list[IndexStoreFileObject], **kwargs):
        pass

    def clean(self, node_ids: Optional[Union[list[str], list[int]]], **kwargs):
        pass
