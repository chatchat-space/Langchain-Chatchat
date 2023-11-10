import json
from typing import List, Dict, Optional

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import PGVector
from langchain.vectorstores.pgvector import DistanceStrategy
from sqlalchemy import text

from configs import kbs_config

from server.knowledge_base.kb_service.base import SupportedVSType, KBService, EmbeddingsFunAdapter, \
    score_threshold_process
from server.knowledge_base.utils import load_embeddings, KnowledgeFile
from server.utils import embedding_device as get_embedding_device


class PGKBService(KBService):
    pg_vector: PGVector

    def _load_pg_vector(self, embedding_device: str = get_embedding_device(), embeddings: Embeddings = None):
        _embeddings = embeddings
        if _embeddings is None:
            _embeddings = load_embeddings(self.embed_model, embedding_device)
        self.pg_vector = PGVector(embedding_function=EmbeddingsFunAdapter(_embeddings),
                                  collection_name=self.kb_name,
                                  distance_strategy=DistanceStrategy.EUCLIDEAN,
                                  connection_string=kbs_config.get("pg").get("connection_uri"))

    def get_doc_by_id(self, id: str) -> Optional[Document]:
        with self.pg_vector.connect() as connect:
            stmt = text("SELECT document, cmetadata FROM langchain_pg_embedding WHERE collection_id=:id")
            results = [Document(page_content=row[0], metadata=row[1]) for row in
                       connect.execute(stmt, parameters={'id': id}).fetchall()]
            if len(results) > 0:
                return results[0]

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
        self._load_pg_vector(embeddings=embeddings)
        return score_threshold_process(score_threshold, top_k,
                                       self.pg_vector.similarity_search_with_score(query, top_k))

    def do_add_doc(self, docs: List[Document], **kwargs) -> List[Dict]:
        ids = self.pg_vector.add_documents(docs)
        doc_infos = [{"id": id, "metadata": doc.metadata} for id, doc in zip(ids, docs)]
        return doc_infos

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
        self.pg_vector.create_collection()


if __name__ == '__main__':
    from server.db.base import Base, engine

    # Base.metadata.create_all(bind=engine)
    pGKBService = PGKBService("test")
    # pGKBService.create_kb()
    # pGKBService.add_doc(KnowledgeFile("README.md", "test"))
    # pGKBService.delete_doc(KnowledgeFile("README.md", "test"))
    # pGKBService.drop_kb()
    print(pGKBService.get_doc_by_id("f1e51390-3029-4a19-90dc-7118aaa25772"))
    # print(pGKBService.search_docs("如何启动api服务"))
