from __future__ import annotations

import enum
from typing import Dict, List, Tuple, Optional, Callable, Any, Literal

from langchain.schema.document import Document
from langchain.vectorstores.base import VectorStore, VectorStoreRetriever
from langchain_core.embeddings import Embeddings
from sqlalchemy import text as sql_text

from chatchat.configs import logger, log_verbose
from chatchat.server.knowledge_base.utils import get_loader, make_text_splitter
from chatchat.server.utils import get_ChatOpenAI, get_Embeddings
from chatchat.server.file_rag.schema import TextNode
from chatchat.server.file_rag.vector_stores.myfaiss import LocalFaissCache, MemoFaissCache, FaissStore


class VectorStoreIndex(VectorStore):
    '''
    wrappr of vector store with helper methods such as crud etc.
    '''
    SUPPORT_VS_TYPES = ["Chroma", "ElasticsearchStore", "FAISS", "Milvus",
                        "PGVector", "Zilliz"]

    def __init__(
        self,
        vector_store: VectorStore,
    ) -> None:
        self.vector_store = vector_store
        if not self.vs_type:
            raise RuntimeError(f"provided vector store {vector_store} is not supported."
                               " only {self.SUPPORT_VS_TYPES} supported.")

    # override abstract methods, redirect to self.vector_store's methods

    def add_texts(self, texts: enum.Iterable[str], metadatas: List[Dict] | None = None, **kwargs: Any) -> List[str]:
        return self.vector_store.add_texts(texts, metadatas, **kwargs)
    
    @property
    def embeddings(self) -> Embeddings:
        return self.vector_store.embeddings
    
    def delete(self, ids: List[str] | None = None, **kwargs: Any) -> bool | None:
        return self.vector_store.delete(ids, **kwargs)
    
    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        return self.vector_store.similarity_search(query, k, **kwargs)
    
    def _select_relevance_score_fn(self) -> Callable[[float], float]:
        return self.vector_store._select_relevance_score_fn()
    
    def similarity_search_with_score(self, *args: Any, **kwargs: Any) -> List[Tuple[Document | float]]:
        return self.vector_store.similarity_search_with_score(*args, **kwargs)
    
    def similarity_search_by_vector(self, embedding: List[float], k: int = 4, **kwargs: Any) -> List[Document]:
        return self.vector_store.similarity_search_by_vector(embedding, k, **kwargs)
    
    def max_marginal_relevance_search(self, query: str, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, **kwargs: Any) -> List[Document]:
        return self.vector_store.max_marginal_relevance_search(query, k, fetch_k, lambda_mult, **kwargs)
    
    def max_marginal_relevance_search_by_vector(self, embedding: List[float], k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, **kwargs: Any) -> List[Document]:
        return self.vector_store.max_marginal_relevance_search_by_vector(embedding, k, fetch_k, lambda_mult, **kwargs)
    
    @classmethod
    def from_texts(cls, texts: List[str], embedding: Embeddings, metadatas: List[Dict] | None = None, **kwargs: Any) -> VectorStoreIndex:
        raise NotImplementedError(f"{cls} should not be instanted directly by from_* mehtods.")

    # some helper methods

    @property
    def vs_type(self) -> str:
        '''
        check vectorstore type automatically by cls name
        '''
        for cls in self.vector_store.__class__.mro():
            if cls.__name__ in self.SUPPORT_VS_TYPES:
                return cls.__name__

    def upsert(self, documents: List[Tuple[Document, str]]) -> None:
        '''
        update existed documents, do insert if not exist.
        '''
        for doc, id in documents:
            try:
                if id:
                    self.delete([id])
            except Exception as e:
                logger.error(f"failed to delete documents with id: {id} in {self.vector_store}.", exc_info=True)
            finally:
                if id:
                    ids = [id]
                else:
                    ids = None
                self.add_documents([doc], ids=ids)

    def get_by_ids(self, ids: List[str]) -> List[Document]:
        result = []
        vs_type = self.vs_type
        vs = self.vector_store

        if vs_type == "Chroma":
            get_result = vs._collection.get(ids=ids)
            if get_result['documents']:
                _metadatas = get_result['metadatas'] if get_result['metadatas'] else [{}] * len(get_result['documents'])
                for page_content, metadata in zip(get_result['documents'], _metadatas):
                    result.append(Document(**{'page_content': page_content, 'metadata': metadata}))
        elif vs_type == "ElasticsearchStore":
            for doc_id in ids:
                try:
                    response = vs.client.get(index=self.index_name, id=doc_id)
                    source = response["_source"]
                    # Assuming your document has "text" and "metadata" fields
                    text = source.get("context", "")
                    metadata = source.get("metadata", {})
                    result.append(Document(page_content=text, metadata=metadata))
                except Exception as e:
                    logger.error(f"Error retrieving document from Elasticsearch! {e}")
        elif vs_type == "FAISS":
            result = [vs.docstore._dict.get(id) for id in ids]
        elif vs_type in ["Milvus", "Zilliz"]:
            pk_field = vs._primary_field
            text_field = vs._text_field
            vector_field = vs._vector_field
            data_list = vs.col.query(expr=f'{pk_field} in {[int(_id) for _id in ids]}', output_fields=["*"])
            for data in data_list:
                text = data.pop(text_field, "")
                data.pop(vector_field, None)
                result.append(Document(page_content=text, metadata=data))
        elif vs_type == "PGVector":
            from sqlalchemy.orm import Session
            with Session(vs._bind) as session:
                stmt = sql_text("SELECT document, cmetadata FROM langchain_pg_embedding WHERE custom_id = ANY(:ids)")
                result = [Document(page_content=row[0], metadata=row[1]) for row in
                        session.execute(stmt, {'ids': ids}).fetchall()]
        else:
            raise RuntimeError(f"unsupported vector store: {vs}")

        return result


if __name__ == "__main__":
    from langchain_community.vectorstores.pgvector import PGVector

    from chatchat.configs.kb_config import kbs_config
    from chatchat.server.utils import get_Embeddings

    # test memory faiss
    vs = MemoFaissCache("temp", get_Embeddings())
    vs.add_texts(["test text"])
    print(vs.similarity_search("test"))

    vs2 = MemoFaissCache("temp", get_Embeddings())
    print(vs.similarity_search("test"))

    # test local vector store
    vs = PGVector(kbs_config["pg"]["connection_uri"], get_Embeddings(), collection_name="test")
    index = VectorStoreIndex(vs)

    # test sinilarity search
    print(index.similarity_search("chatchat"))

    # test add
    ids = index.add_texts(["test text"])

    # test get
    print(index.get_by_ids(ids))

    # test upsert
    index.upsert([(Document(page_content="updated test text 2"), ids[0])])
    print(index.get_by_ids(ids))
