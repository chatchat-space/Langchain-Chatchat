from configs.model_config import EMBEDDING_MODEL, DEFAULT_VS_TYPE
from server.knowledge_base.utils import (get_file_path, list_kbs_from_folder,
                                        list_files_from_folder, run_in_thread_pool,
                                        files2docs_in_thread,
                                        KnowledgeFile,)
from server.knowledge_base.kb_service.base import KBServiceFactory, SupportedVSType
from server.db.repository.knowledge_file_repository import add_file_to_db
from server.db.base import Base, engine
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Literal, Any, List


pool = ThreadPoolExecutor(os.cpu_count())


def create_tables():
    Base.metadata.create_all(bind=engine)


def reset_tables():
    Base.metadata.drop_all(bind=engine)
    create_tables()


def file_to_kbfile(kb_name: str, files: List[str]) -> List[KnowledgeFile]:
    kb_files = []
    for file in files:
        try:
            kb_file = KnowledgeFile(filename=file, knowledge_base_name=kb_name)
            kb_files.append(kb_file)
        except Exception as e:
            print(f"{e}，已跳过")
    return kb_files


def folder2db(
    kb_name: str,
    mode: Literal["recreate_vs", "fill_info_only", "update_in_db", "increament"],
    vs_type: Literal["faiss", "milvus", "pg", "chromadb"] = DEFAULT_VS_TYPE,
    embed_model: str = EMBEDDING_MODEL,
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
        files_count = kb.count_files()
        print(f"知识库 {kb_name} 中共有 {files_count} 个文档。\n即将清除向量库。")
        kb.clear_vs()
        files_count = kb.count_files()
        print(f"清理后，知识库 {kb_name} 中共有 {files_count} 个文档。")

        kb_files = file_to_kbfile(kb_name, list_files_from_folder(kb_name))
        for success, result in files2docs_in_thread(kb_files, pool=pool):
            if success:
                _, filename, docs = result
                print(f"正在将 {kb_name}/{filename} 添加到向量库，共包含{len(docs)}条文档")
                kb_file = KnowledgeFile(filename=filename, knowledge_base_name=kb_name)
                kb.add_doc(kb_file=kb_file, docs=docs, not_refresh_vs_cache=True)
            else:
                print(result)

        if kb.vs_type() == SupportedVSType.FAISS:
            kb.save_vector_store()
            kb.refresh_vs_cache()
    elif mode == "fill_info_only":
        files = list_files_from_folder(kb_name)
        kb_files = file_to_kbfile(kb_name, files)

        for kb_file in kb_files:
            add_file_to_db(kb_file)
            print(f"已将 {kb_name}/{kb_file.filename} 添加到数据库")
    elif mode == "update_in_db":
        files = kb.list_files()
        kb_files = file_to_kbfile(kb_name, files)

        for kb_file in kb_files:
            kb.update_doc(kb_file, not_refresh_vs_cache=True)

        if kb.vs_type() == SupportedVSType.FAISS:
            kb.save_vector_store()
            kb.refresh_vs_cache()
    elif mode == "increament":
        db_files = kb.list_files()
        folder_files = list_files_from_folder(kb_name)
        files = list(set(folder_files) - set(db_files))
        kb_files = file_to_kbfile(kb_name, files)

        for success, result in files2docs_in_thread(kb_files, pool=pool):
            if success:
                _, filename, docs = result
                print(f"正在将 {kb_name}/{filename} 添加到向量库")
                kb_file = KnowledgeFile(filename=filename, knowledge_base_name=kb_name)
                kb.add_doc(kb_file=kb_file, docs=docs, not_refresh_vs_cache=True)
            else:
                print(result)

        if kb.vs_type() == SupportedVSType.FAISS:
            kb.save_vector_store()
            kb.refresh_vs_cache()
    else:
        print(f"unspported migrate mode: {mode}")


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


def prune_db_files(kb_name: str):
    '''
    delete files in database that not existed in local folder.
    it is used to delete database files after user deleted some doc files in file browser
    '''
    kb = KBServiceFactory.get_service_by_name(kb_name)
    if kb.exists():
        files_in_db = kb.list_files()
        files_in_folder = list_files_from_folder(kb_name)
        files = list(set(files_in_db) - set(files_in_folder))
        kb_files = file_to_kbfile(kb_name, files)
        for kb_file in kb_files:
            kb.delete_doc(kb_file, not_refresh_vs_cache=True)
        if kb.vs_type() == SupportedVSType.FAISS:
            kb.save_vector_store()
            kb.refresh_vs_cache()
        return kb_files

def prune_folder_files(kb_name: str):
    '''
    delete doc files in local folder that not existed in database.
    is is used to free local disk space by delete unused doc files.
    '''
    kb = KBServiceFactory.get_service_by_name(kb_name)
    if kb.exists():
        files_in_db = kb.list_files()
        files_in_folder = list_files_from_folder(kb_name)
        files = list(set(files_in_folder) - set(files_in_db))
        for file in files:
            os.remove(get_file_path(kb_name, file))
        return files
