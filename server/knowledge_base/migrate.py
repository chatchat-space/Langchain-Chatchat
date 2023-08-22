from configs.model_config import EMBEDDING_MODEL, DEFAULT_VS_TYPE
from server.knowledge_base.utils import get_file_path, list_kbs_from_folder, list_docs_from_folder, KnowledgeFile
from server.knowledge_base.kb_service.base import KBServiceFactory
from server.db.repository.knowledge_file_repository import add_doc_to_db
from server.db.base import Base, engine
import os
from typing import Literal, Callable, Any


def create_tables():
    Base.metadata.create_all(bind=engine)


def reset_tables():
    Base.metadata.drop_all(bind=engine)
    create_tables()


def folder2db(
    kb_name: str,
    mode: Literal["recreate_vs", "fill_info_only", "update_in_db", "increament"],
    vs_type: Literal["faiss", "milvus", "pg", "chromadb"] = DEFAULT_VS_TYPE,
    embed_model: str = EMBEDDING_MODEL,
    callback_before: Callable = None,
    callback_after: Callable = None,
):
    '''
    use existed files in local folder to populate database and/or vector store.
    set parameter `mode` to:
        recreate_vs: recreate all vector store and fill info to database using existed files in local folder
        fill_info_only: do not create vector store, fill info to db using existed files only
        update_in_db: update vector store and database info using local files that existed in database only
        increament: create vector store and database info for local files that not existed in database only
    '''
    kb = KBServiceFactory.get_service(kb_name, vs_type, embed_model)
    kb.create_kb()

    if mode == "recreate_vs":
        kb.clear_vs()
        docs = list_docs_from_folder(kb_name)
        for i, doc in enumerate(docs):
            try:
                kb_file = KnowledgeFile(doc, kb_name)
                if callable(callback_before):
                    callback_before(kb_file, i, docs)
                if i == len(docs) - 1:
                    not_refresh_vs_cache = False
                else:
                    not_refresh_vs_cache = True
                kb.add_doc(kb_file, not_refresh_vs_cache=not_refresh_vs_cache)
                if callable(callback_after):
                    callback_after(kb_file, i, docs)
            except Exception as e:
                print(e)
    elif mode == "fill_info_only":
        docs = list_docs_from_folder(kb_name)
        for i, doc in enumerate(docs):
            try:
                kb_file = KnowledgeFile(doc, kb_name)
                if callable(callback_before):
                    callback_before(kb_file, i, docs)
                add_doc_to_db(kb_file)
                if callable(callback_after):
                    callback_after(kb_file, i, docs)
            except Exception as e:
                print(e)
    elif mode == "update_in_db":
        docs = kb.list_docs()
        for i, doc in enumerate(docs):
            try:
                kb_file = KnowledgeFile(doc, kb_name)
                if callable(callback_before):
                    callback_before(kb_file, i, docs)
                if i == len(docs) - 1:
                    not_refresh_vs_cache = False
                else:
                    not_refresh_vs_cache = True
                kb.update_doc(kb_file, not_refresh_vs_cache=not_refresh_vs_cache)
                if callable(callback_after):
                    callback_after(kb_file, i, docs)
            except Exception as e:
                print(e)
    elif mode == "increament":
        db_docs = kb.list_docs()
        folder_docs = list_docs_from_folder(kb_name)
        docs = list(set(folder_docs) - set(db_docs))
        for i, doc in enumerate(docs):
            try:
                kb_file = KnowledgeFile(doc, kb_name)
                if callable(callback_before):
                    callback_before(kb_file, i, docs)
                if i == len(docs) - 1:
                    not_refresh_vs_cache = False
                else:
                    not_refresh_vs_cache = True
                kb.add_doc(kb_file, not_refresh_vs_cache=not_refresh_vs_cache)
                if callable(callback_after):
                    callback_after(kb_file, i, docs)
            except Exception as e:
                print(e)
    else:
        raise ValueError(f"unspported migrate mode: {mode}")


def recreate_all_vs(
    vs_type: Literal["faiss", "milvus", "pg", "chromadb"] = DEFAULT_VS_TYPE,
    embed_mode: str = EMBEDDING_MODEL,
    **kwargs: Any,
):
    '''
    used to recreate a vector store or change current vector store to another type or embed_model
    '''
    for kb_name in list_kbs_from_folder():
        folder2db(kb_name, "recreate_vs", vs_type, embed_mode, **kwargs)


def prune_db_docs(kb_name: str):
    '''
    delete docs in database that not existed in local folder.
    it is used to delete database docs after user deleted some doc files in file browser
    '''
    kb = KBServiceFactory.get_service_by_name(kb_name)
    if kb.exists():
        docs_in_db = kb.list_docs()
        docs_in_folder = list_docs_from_folder(kb_name)
        docs = list(set(docs_in_db) - set(docs_in_folder))
        for doc in docs:
            kb.delete_doc(KnowledgeFile(doc, kb_name))
        return docs

def prune_folder_docs(kb_name: str):
    '''
    delete doc files in local folder that not existed in database.
    is is used to free local disk space by delete unused doc files.
    '''
    kb = KBServiceFactory.get_service_by_name(kb_name)
    if kb.exists():
        docs_in_db = kb.list_docs()
        docs_in_folder = list_docs_from_folder(kb_name)
        docs = list(set(docs_in_folder) - set(docs_in_db))
        for doc in docs:
            os.remove(get_file_path(kb_name, doc))
        return docs
