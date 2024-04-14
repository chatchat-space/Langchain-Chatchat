from typing import List, Dict

from langchain.schema import Document
from langchain_community.vectorstores.relyt import Relyt
from sqlalchemy import text
from sqlalchemy.orm import Session

from configs import kbs_config
from server.knowledge_base.kb_service.base import SupportedVSType, KBService, EmbeddingsFunAdapter, \
    score_threshold_process
from server.knowledge_base.utils import KnowledgeFile


class RelytKBService(KBService):

    def _load_relyt_vector(self):
        embedding_func = EmbeddingsFunAdapter(self.embed_model)
        sample_embedding = embedding_func.embed_query("Hello pgvecto_rs!")
        self.relyt = Relyt(
            embedding_function=embedding_func,
            embedding_dimension=len(sample_embedding),
            connection_string=kbs_config.get("relyt").get("connection_uri"),
            collection_name=self.kb_name,
        )

    def get_doc_by_ids(self, ids: List[str]) -> List[Document]:
        with Session(self.relyt.engine) as session:
            stmt = text(f"SELECT document, metadata FROM {self.kb_name} WHERE id = ANY(:ids)")
            results = [Document(page_content=row[0], metadata=row[1]) for row in
                      session.execute(stmt, {'ids': ids}).fetchall()]
            return results

    def del_doc_by_ids(self, ids: List[str]) -> bool:
        with Session(self.relyt.engine) as session:
            stmt = text(f"DELETE FROM {self.kb_name} WHERE id = ANY(:ids)")
            session.execute(stmt, {'ids': ids})
            session.commit()
        return True

    def do_init(self):
        self._load_relyt_vector()

    def do_create_kb(self):
        pass

    def vs_type(self) -> str:
        return SupportedVSType.RELYT

    def do_drop_kb(self):
        self.relyt.delete_collection()

    def do_search(self, query: str, top_k: int, score_threshold: float):
        docs = self.relyt.similarity_search_with_score(query, top_k)
        return score_threshold_process(score_threshold, top_k, docs)

    def do_add_doc(self, docs: List[Document], **kwargs) -> List[Dict]:
        print(docs)
        ids = self.relyt.add_documents(docs)
        print(ids)
        doc_infos = [{"id": id, "metadata": doc.metadata} for id, doc in zip(ids, docs)]
        return doc_infos

    def do_delete_doc(self, kb_file: KnowledgeFile, **kwargs):
        filepath = self.get_relative_source_path(kb_file.filepath)
        stmt = f"DELETE FROM {self.kb_name} WHERE metadata->>'source'='{filepath}'; "
        with Session(self.relyt.engine) as session:
            session.execute(text(stmt))
            session.commit()

    def do_clear_vs(self):
        self.do_drop_kb()


if __name__ == '__main__':
    from server.db.base import Base, engine
    Base.metadata.create_all(bind=engine)
    relyt_kb_service = RelytKBService("collection_test")
    kf = KnowledgeFile("README.md", "test")
    print(kf)
    relyt_kb_service.add_doc(kf)
    print("has add README")
    relyt_kb_service.delete_doc(KnowledgeFile("README.md", "test"))
    relyt_kb_service.drop_kb()
    print(relyt_kb_service.get_doc_by_ids(["444022434274215486"]))
    print(relyt_kb_service.search_docs("如何启动api服务"))
