from typing import List

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import PGVector
from sqlalchemy import text

from configs.model_config import EMBEDDING_DEVICE, kbs_config
from server.knowledge_base.kb_service.base import SupportedVSType, KBService
from server.knowledge_base.utils import load_embeddings, KnowledgeFile


class PGKBService(KBService):
    pg_vector: PGVector

    def _load_pg_vector(self, embedding_device: str = EMBEDDING_DEVICE, embeddings: Embeddings = None):
        _embeddings = embeddings
        if _embeddings is None:
            _embeddings = load_embeddings(self.embed_model, embedding_device)
        self.pg_vector = PGVector(embedding_function=_embeddings,
                                  collection_name=self.kb_name,
                                  connection_string=kbs_config.get("pg").get("connection_uri"))

    def do_init(self):
        self._load_pg_vector()

    def do_create_kb(self):
        pass

    def vs_type(self) -> str:
        return SupportedVSType.PG

    def do_drop_kb(self):
        with self.pg_vector.connect() as connect:
            connect.execute(text(f'''
                    -- 删除 langchain_pg_embedding 表中关联到 langchain_pg_collection 表中 的记录
                    DELETE FROM langchain_pg_embedding
                    WHERE collection_id IN (
                      SELECT uuid FROM langchain_pg_collection WHERE name = '{self.kb_name}'
                    );
                    -- 删除 langchain_pg_collection 表中 记录
                    DELETE FROM langchain_pg_collection WHERE name = '{self.kb_name}';
            '''))
            connect.commit()

    def do_search(self, query: str, top_k: int, score_threshold: float, embeddings: Embeddings):
        # todo: support score threshold
        self._load_pg_vector(embeddings=embeddings)
        return self.pg_vector.similarity_search_with_score(query, top_k)

    def add_doc(self, kb_file: KnowledgeFile, **kwargs):
        """
        向知识库添加文件
        """
        docs = kb_file.file2text()
        self.pg_vector.add_documents(docs)
        from server.db.repository.knowledge_file_repository import add_doc_to_db
        status = add_doc_to_db(kb_file)
        return status

    def do_add_doc(self, docs: List[Document], embeddings: Embeddings, **kwargs):
        pass

    def do_delete_doc(self, kb_file: KnowledgeFile, **kwargs):
        with self.pg_vector.connect() as connect:
            filepath = kb_file.filepath.replace('\\', '\\\\')
            connect.execute(
                text(
                    ''' DELETE FROM langchain_pg_embedding WHERE cmetadata::jsonb @> '{"source": "filepath"}'::jsonb;'''.replace(
                        "filepath", filepath)))
            connect.commit()

    def do_clear_vs(self):
        self.pg_vector.delete_collection()


if __name__ == '__main__':
    from server.db.base import Base, engine

    Base.metadata.create_all(bind=engine)
    pGKBService = PGKBService("test")
    pGKBService.create_kb()
    pGKBService.add_doc(KnowledgeFile("README.md", "test"))
    pGKBService.delete_doc(KnowledgeFile("README.md", "test"))
    pGKBService.drop_kb()
    print(pGKBService.search_docs("测试"))
