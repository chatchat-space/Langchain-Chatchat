from server.db.models.knowledge_base_model import KnowledgeBaseModel
from server.db.models.knowledge_file_model import KnowledgeFileModel
from server.db.session import with_session
from server.knowledge_base.knowledge_file import KnowledgeFile


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
            session.add(kb_file)
            kb.file_count += 1
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
def doc_exists(session, kb_file: KnowledgeFile):
    existing_file = session.query(KnowledgeFileModel).filter_by(file_name=kb_file.filename,
                                                                kb_name=kb_file.kb_name).first()
    return True if existing_file else False
