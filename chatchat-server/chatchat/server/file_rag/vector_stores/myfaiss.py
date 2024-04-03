from __future__ import annotations

import enum
import os
from threading import RLock, Event
from typing import Dict, List, Tuple, Optional, Callable, Any, Literal

from langchain.schema.document import Document
from langchain.vectorstores.faiss import FAISS as _FAISS
from langchain_community.docstore.base import Docstore
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.embeddings import Embeddings
from memoization import cached, CachingAlgorithmFlag

from chatchat.configs import CACHED_VS_NUM, CACHED_MEMO_VS_NUM, logger, log_verbose


__all = ["FaissStore", "LocalFaissCache", "MemoFaissCache"]


class FaissStore(_FAISS):
    '''
    make FAISS to load lazy and thread safe
    you should not instant it directly, use factory instead
    '''
    def __init__(
        self,
        embedding_function: Embeddings = None,
        index: enum.Any = None,
        docstore: Docstore = None,
        index_to_docstore_id: Dict[int, str] = {},
        relevance_score_fn: Callable[[float], float] | None = None,
        normalize_L2: bool = False,
        distance_strategy: DistanceStrategy = DistanceStrategy.EUCLIDEAN_DISTANCE,
        folder_path: str = None,
        index_name: str = "index",
    ):
        # let us instance a FAISS object without loading index
        super().__init__(
            embedding_function=embedding_function,
            index=index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
            relevance_score_fn=relevance_score_fn,
            normalize_L2=normalize_L2,
            distance_strategy=distance_strategy,
        )
        self.folder_path = folder_path
        self.index_name = index_name
        self.write_lock = RLock()
        self.ready_to_search = Event()
        self.last_mtime = None

    def __add(self, texts: enum.Iterable[str], embeddings: enum.Iterable[List[float]], metadatas: enum.Iterable[Dict] | None = None, ids: List[str] | None = None) -> List[str]:
        '''
        all add_* methods go through here
        '''
        with self.write_lock:
            self.ready_to_search.clear()
            ret = super().__add(texts, embeddings, metadatas, ids)
            if self.folder_path:
                self.save_local()
            self.ready_to_search.set()
            return ret

    def delete(self, ids: List[str] | None = None, **kwargs: enum.Any) -> bool | None:
        with self.write_lock:
            self.ready_to_search.clear()
            ret = super().delete(ids, **kwargs)
            if self.folder_path:
                self.save_local()
            self.ready_to_search.set()
            return ret

    @classmethod
    def _copy_from_faiss(cls, vs: _FAISS):
        obj = cls(
            embedding_function = vs.embedding_function,
            index = vs.index,
            docstore = vs.docstore,
            index_to_docstore_id = vs.index_to_docstore_id,
            relevance_score_fn = vs.override_relevance_score_fn,
            normalize_L2 = vs._normalize_L2,
            distance_strategy = vs.distance_strategy,
        )
        return obj

    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Embeddings,
        metadatas: List[Dict] | None = None,
        ids: List[str] | None = None,
        index_name: str = "index",
        **kwargs: Any,
    ) -> FaissStore:
        '''
        all from_* methods go through here.
        make it init vector store with empty documents.
        '''
        is_empty = False
        if not texts:
            is_empty = True
            texts = ["hello world"]
            ids = ["temp_to_del"]
        vs = super().from_texts(texts, embedding, metadatas, ids, **kwargs)
        if is_empty:
            vs.delete(ids)
        obj = cls._copy_from_faiss(vs)
        obj.index_name = index_name
        obj.ready_to_search.set()
        return obj

    @classmethod
    def load_local(
        cls,
        folder_path: str = None,
        embeddings: Embeddings = None,
        index_name: str = "index",
        allow_dangerous_deserialization: bool = False,
        **kwargs,
    ) -> FaissStore:
        vs = super().load_local(
            folder_path=folder_path,
            embeddings=embeddings,
            index_name=index_name,
            allow_dangerous_deserialization=allow_dangerous_deserialization,
            **kwargs,
        )
        obj = cls._copy_from_faiss(vs)
        obj.folder_path = folder_path
        obj.index_name = index_name
        obj.ready_to_search.set()
        return obj

    def save_local(self, folder_path: str = None, index_name: str = None) -> None:
        folder_path = folder_path or self.folder_path
        index_name = index_name or self.index
        self.folder_path = folder_path
        self.index_name = index_name
        with self.write_lock:
            self.ready_to_search.clear()
            ret = super().save_local(folder_path, index_name)
            index_path = os.path.join(folder_path, f"{index_name}.faiss")
            mtime = int(os.path.getmtime(index_path))
            self.last_mtime = mtime
            self.ready_to_search.set()
            return ret

    def similarity_search_with_score_by_vector(self, embedding: List[float], k: int = 4, filter: Callable[..., Any] | Dict[str, enum.Any] | None = None, fetch_k: int = 20, **kwargs: enum.Any) -> List[Tuple[Document | float]]:
        '''
        all similarity search methods go through here
        '''
        self.ready_to_search.wait()
        return super().similarity_search_with_score_by_vector(embedding, k, filter, fetch_k, **kwargs)

    def max_marginal_relevance_search_with_score_by_vector(self, embedding: List[float], *, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, filter: Callable[..., Any] | Dict[str, enum.Any] | None = None) -> List[Tuple[Document | float]]:
        '''
        all max marginal relevance search methods go through here
        '''
        self.ready_to_search.wait()
        return super().max_marginal_relevance_search_with_score_by_vector(embedding, k=k, fetch_k=fetch_k, lambda_mult=lambda_mult, filter=filter)


def _custom_local_faiss_key(
    embedding: Embeddings,
    folder_path: str,
    index_name: str,
    allow_dangerous_deserialization: bool,
):
    """
    Make a cache key with Embeddings support
    """
    return (
        embedding.model,
        folder_path,
        index_name,
        allow_dangerous_deserialization,
    )


@cached(max_size=CACHED_VS_NUM, algorithm=CachingAlgorithmFlag.LFU, custom_key_maker=_custom_local_faiss_key)
def _load_local_faiss(
    embedding: Embeddings,
    folder_path: str,
    index_name: str,
    allow_dangerous_deserialization: bool,
) -> FaissStore:
    return FaissStore.load_local(
        folder_path=folder_path,
        embeddings=embedding,
        index_name=index_name,
        allow_dangerous_deserialization=allow_dangerous_deserialization,
    )


def LocalFaissCache(
    embedding: Embeddings,
    folder_path: str,
    index_name: str = "index",
    allow_dangerous_deserialization: bool = False,
) -> FaissStore:
    '''
    factory function to load local faiss index with cache
    '''
    index_path = os.path.join(folder_path, f"{index_name}.faiss")
    mtime = int(os.path.getmtime(index_path))

    def _remove_outdated(arguments, result, is_alive):
        '''remove cache that behind disk mtime'''
        if (arguments[0] == (embedding, folder_path, index_name, allow_dangerous_deserialization)
            and result.last_mtime < mtime):
            return True
        return False

    _load_local_faiss.cache_remove_if(_remove_outdated)
    result = _load_local_faiss(embedding, folder_path, index_name, allow_dangerous_deserialization)
    if log_verbose:
        logger.info(f"cache info for {folder_path}/{index_name}:\n{_load_local_faiss.cache_info()}")
    return result


def _custom_memo_faiss_key(index_name: str, embedding: Embeddings):
    """
    Make a cache key with Embeddings support
    """
    return (index_name, embedding.model)


@cached(max_size=CACHED_MEMO_VS_NUM, algorithm=CachingAlgorithmFlag.LFU, custom_key_maker=_custom_memo_faiss_key)
def _load_memo_faiss(index_name, embedding):
    return FaissStore.from_texts([], embedding=embedding, index_name=index_name)

def MemoFaissCache(
    index_name: str,
    embedding: Embeddings,
) -> FaissStore:
    '''
    factory function to load memory faiss index with cache, an index_name should be specified.
    '''
    result = _load_memo_faiss(index_name, embedding)
    if log_verbose:
        logger.info(f"cache info for {index_name}:\n{_load_memo_faiss.cache_info()}")
    return result
