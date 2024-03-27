import json
from typing import List, Dict, Optional
import logging

from langchain.schema import Document
from langchain.vectorstores.oracle_vector_prepare import ORCLVector,DistanceStrategy
from sqlalchemy import text

from configs import kbs_config

from server.knowledge_base.kb_service.base import SupportedVSType, KBService, EmbeddingsFunAdapter, \
    score_threshold_process
from server.knowledge_base.utils import KnowledgeFile
import shutil

class ORCLKBService(KBService):
    orcl_vector: ORCLVector

    def _load_orcl_vector(self):
        self.orcl_vector = ORCLVector(embedding_function=EmbeddingsFunAdapter(self.embed_model),
                                  collection_name=self.kb_name,
                                  distance_strategy=DistanceStrategy.COSINE,
                                  connection_string=kbs_config.get("orcl").get("connection_uri"))

    def get_doc_by_ids(self, ids: List[str]) -> List[Document]:
        with self.orcl_vector.connect() as connect:
            self.logger = logging.getLogger(__name__)
            cursor = connect.cursor()
            stmt = """SELECT document, cmetadata FROM langchain_oracle_embedding WHERE uuid IN :ids"""
            self.logger.debug(f"Executing get_doc_by_ids: {ids}")
            results = [Document(page_content=row[0], metadata=row[1]) for row in
                       cursor.execute(stmt, ids).fetchall()]
            return results

    # TODO:
    def del_doc_by_ids(self, ids: List[str]) -> bool:
        return super().del_doc_by_ids(ids)

    def do_init(self):
        self._load_orcl_vector()

    def do_create_kb(self):
        pass

    def vs_type(self) -> str:
        return SupportedVSType.ORCL

    def do_drop_kb(self):
        with self.orcl_vector.connect() as connect:
            self.logger = logging.getLogger(__name__)
            cursor = connect.cursor()
            self.logger.info(f"DELETE kb_name from langchain_oracle_embedding: {self.kb_name}")
            cursor.execute(
                    """
                        DELETE
                        FROM
                            langchain_oracle_embedding
                        WHERE
                        collection_id = ( SELECT uuid FROM langchain_oracle_collection WHERE name = :1 )
                     """, [self.kb_name])
            cursor.execute(
                     """
                         DELETE
                         FROM
                             langchain_oracle_collection
                         WHERE
                             name = :1
                     """, [self.kb_name])

            cursor.close()
            connect.commit()
            shutil.rmtree(self.kb_path)

    def do_search(self, query: str, top_k: int, score_threshold: float):
        self._load_orcl_vector()
        embed_func = EmbeddingsFunAdapter(self.embed_model)
        embeddings = embed_func.embed_query(query)
        docs = self.orcl_vector.similarity_search_with_score_by_vector(embeddings, top_k)
        return score_threshold_process(score_threshold, top_k, docs)

    def do_add_doc(self, docs: List[Document], **kwargs) -> List[Dict]:
        ids = self.orcl_vector.add_documents(docs)
        doc_infos = [{"id": id, "metadata": doc.metadata} for id, doc in zip(ids, docs)]
        return doc_infos

    def do_delete_doc(self, kb_file: KnowledgeFile, **kwargs):
        with self.orcl_vector.connect() as connect:
            filepath = kb_file.filepath.replace('\\', '\\\\')
            self.logger = logging.getLogger(__name__)
            self.logger.info(
                text(
                    ''' DELETE FROM langchain_oracle_embedding WHERE JSON_VALUE(cmetadata, '$.source') = '"filepath"'; '''.replace(
                        "filepath", filepath)))

            cursor = connect.cursor()
            cursor.execute("DELETE FROM langchain_oracle_embedding WHERE JSON_VALUE(cmetadata, '$.source') = '" + filepath + "'")
            connect.commit()

    def do_clear_vs(self):
        self.orcl_vector.delete_collection()
        self.orcl_vector.create_collection()


if __name__ == '__main__':
    from server.db.base import Base, engine

    # Base.metadata.create_all(bind=engine)
    oRCLBService = OrclKBService("test")
    # pGKBService.create_kb()
    # pGKBService.add_doc(KnowledgeFile("README.md", "test"))
    # pGKBService.delete_doc(KnowledgeFile("README.md", "test"))
    # pGKBService.drop_kb()
    print(oRCLKBService.get_doc_by_ids(["f1e51390-3029-4a19-90dc-7118aaa25772"]))
    # print(pGKBService.search_docs("如何启动api服务"))
