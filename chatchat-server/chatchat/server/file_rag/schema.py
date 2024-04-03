from __future__ import annotations

from typing import List

from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema.document import Document


class NodeMetadata(BaseModel):
    file_source: str = Field("", title="文件路径")
    file_name: str = Field("", title="文件名称")
    node_type: str = Field("")
    title: str = Field("", title="标题")
    summanry: str = Field("", title="总结/摘要")

    _doc_hash: str = ""
    _doc_id: str = ""
    _doc_ref_id: str = Field("", title="源文档ID")
    _parent_id: str = ""
    _prev_id: str = ""
    _next_id: str = ""

    _fields_to_embed: List[str] = ["title"]
    _fields_to_content: List[str] = ["title"]

    class Config:
        extra = "allow"


class TextNode(Document):
    metadata: NodeMetadata = Field(default_factory=NodeMetadata)
    type: str = "TextNode"

    @property
    def doc_id(self) -> str:
        return self.metadata._doc_id
    
    @property
    def doc_ref_id(self) -> str:
        return self.metadata._doc_ref_id
    
    @doc_ref_id.setter
    def doc_ref_id(self, id: str):
        self.metadata._doc_ref_id = id

    @property
    def parent_id(self) -> str:
        return self.metadata._parent_id

    @parent_id.setter
    def parent_id(self, id):
        self.metadata._parent_id = id

    @property
    def prev_id(self) -> str:
        return self.metadata._prev_id
    
    @prev_id.setter
    def prev_id(self, id: str):
        self.metadata._prev_id = id

    @property
    def next_id(self) -> str:
        return self.metadata._next_id

    @next_id.setter
    def next_id(self, id: str):
        self.metadata._next_id = id
    
    @property
    def fields_to_embed(self) -> List[str]:
        return self.metadata._fields_to_embed
    
    @fields_to_embed.setter
    def fields_to_embed(self, val: List[str]):
        self.metadata._fields_to_embed = val.copy()
    
    @property
    def fields_to_content(self) -> List[str]:
        return self.metadata._fields_to_content
    
    @fields_to_content.setter
    def fields_to_content(self, val: List[str]):
        self.metadata._fields_to_content = val.copy()

    def get_content(self) -> str:
        meta = {v.get("title", k) for k,v in self.metadata.schema()["properties"]}
        return (
            "\n".join([f"{k}: {v}" for k,v in meta.items() if k in self.fields_to_content]),
            "\n",
            self.page_content or "",
        )

    def get_embed_content(self) -> str:
        meta = {v.get("title", k) for k,v in self.metadata.schema()["properties"]}
        return (
            "\n".join([f"{k}: {v}" for k,v in meta.items() if k in self.fields_to_embed]),
            "\n",
            self.page_content or "",
        )
