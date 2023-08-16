from server.db.models.knowledge_base_model import KnowledgeBaseModel
from server.db.models.knowledge_file_model import KnowledgeFileModel
from server.db.session import with_session
from server.knowledge_base.utils import KnowledgeFile


@with_session
def list_docs_from_db(session, kb_name):
    files = session.query(KnowledgeFileModel).filter_by(kb_name=kb_name).all()
    docs = [f.file_name for f in files]
    return docs


@with_session
def add_doc_to_db(session, kb_file: KnowledgeFile):
    kb = session.query(KnowledgeBaseModel).filter_by(kb_name=kb_file.kb_name).first()
    if kb:
        # 如果已经存在该文件，则更新文件版本号
        existing_file = session.query(KnowledgeFileModel).filter_by(file_name=kb_file.filename,
                                                                    kb_name=kb_file.kb_name).first()
        if existing_file:
            existing_file.file_version += 1
        # 否则，添加新文件
        else:
            new_file = KnowledgeFileModel(
                file_name=kb_file.filename,
                file_ext=kb_file.ext,
                kb_name=kb_file.kb_name,
                document_loader_name=kb_file.document_loader_name,
                text_splitter_name=kb_file.text_splitter_name or "SpacyTextSplitter",
            )
            kb.file_count += 1
            session.add(new_file)
    return True


@with_session
def delete_file_from_db(session, kb_file: KnowledgeFile):
    existing_file = session.query(KnowledgeFileModel).filter_by(file_name=kb_file.filename,
                                                                kb_name=kb_file.kb_name).first()
    if existing_file:
        session.delete(existing_file)
        session.commit()

        kb = session.query(KnowledgeBaseModel).filter_by(kb_name=kb_file.kb_name).first()
        if kb:
            kb.file_count -= 1
            session.commit()
    return True


@with_session
def delete_files_from_db(session, knowledge_base_name: str):
    session.query(KnowledgeFileModel).filter_by(kb_name=knowledge_base_name).delete()

    kb = session.query(KnowledgeBaseModel).filter_by(kb_name=knowledge_base_name).first()
    if kb:
        kb.file_count = 0

    session.commit()
    return True


@with_session
def doc_exists(session, kb_file: KnowledgeFile):
    existing_file = session.query(KnowledgeFileModel).filter_by(file_name=kb_file.filename,
                                                                kb_name=kb_file.kb_name).first()
    return True if existing_file else False


@with_session
def get_file_detail(session, kb_name: str, filename: str) -> dict:
    file: KnowledgeFileModel = (session.query(KnowledgeFileModel)
                                .filter_by(file_name=filename,
                                            kb_name=kb_name).first())
    if file:
        return {
            "kb_name": file.kb_name,
            "file_name": file.file_name,
            "file_ext": file.file_ext,
            "file_version": file.file_version,
            "document_loader": file.document_loader_name,
            "text_splitter": file.text_splitter_name,
            "create_time": file.create_time,
        }
    else:
        return {}
