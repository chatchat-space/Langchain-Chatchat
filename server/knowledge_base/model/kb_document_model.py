
from langchain.docstore.document import Document


class DocumentWithVSId(Document):
    """
    矢量化后的文档id
    """
    id: str = None

