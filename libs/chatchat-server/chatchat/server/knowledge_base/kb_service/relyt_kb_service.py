from typing import Dict, List

from configs import kbs_config
from langchain.schema import Document
from langchain_community.vectorstores.pgvecto_rs import PGVecto_rs
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from server.knowledge_base.kb_service.base import (
    EmbeddingsFunAdapter,
    KBService,
    SupportedVSType,
    score_threshold_process,
)
from server.knowledge_base.utils import KnowledgeFile


class RelytKBService(KBService):
    def _load_relyt_vector(self):
        embedding_func = EmbeddingsFunAdapter(self.embed_model)
        sample_embedding = embedding_func.embed_query("Hello relyt!")
        self.relyt = PGVecto_rs(
            embedding=embedding_func,
            dimension=len(sample_embedding),
            db_url=kbs_config.get("relyt").get("connection_uri"),
            collection_name=self.kb_name,
        )
        self.engine = create_engine(kbs_config.get("relyt").get("connection_uri"))

    def get_doc_by_ids(self, ids: List[str]) -> List[Document]:
        ids_str = ", ".join([f"{id}" for id in ids])
        with Session(self.engine) as session:
            stmt = text(
                f"SELECT text, meta FROM collection_{self.kb_name} WHERE id in (:ids)"
            )
            results = [
                Document(page_content=row[0], metadata=row[1])
                for row in session.execute(stmt, {"ids": ids_str}).fetchall()
            ]
            return results

    def del_doc_by_ids(self, ids: List[str]) -> bool:
        ids_str = ", ".join([f"{id}" for id in ids])
        with Session(self.engine) as session:
            stmt = text(f"DELETE FROM collection_{self.kb_name} WHERE id in (:ids)")
            session.execute(stmt, {"ids": ids_str})
            session.commit()
        return True

    def do_init(self):
        self._load_relyt_vector()
        self.do_create_kb()

    def do_create_kb(self):
        index_name = f"idx_{self.kb_name}_embedding"
        with self.engine.connect() as conn:
            with conn.begin():
                index_query = text(
                    f"""
                        SELECT 1
                        FROM pg_indexes
                        WHERE indexname = '{index_name}';
                    """
                )
                result = conn.execute(index_query).scalar()
                if not result:
                    index_statement = text(
                        f"""
                            CREATE INDEX {index_name}
                            ON collection_{self.kb_name}
                            USING vectors (embedding vector_l2_ops)
                            WITH (options = $$
                            optimizing.optimizing_threads = 30
                            segment.max_growing_segment_size = 2000
                            segment.max_sealed_segment_size = 30000000
                            [indexing.hnsw]
                            m=30
                            ef_construction=500
                            $$);
                        """
                    )
                    conn.execute(index_statement)

    def vs_type(self) -> str:
        return SupportedVSType.RELYT

    def do_drop_kb(self):
        drop_statement = text(f"DROP TABLE IF EXISTS collection_{self.kb_name};")
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(drop_statement)

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
        stmt = f"DELETE FROM collection_{self.kb_name} WHERE meta->>'source'='{filepath}'; "
        with Session(self.engine) as session:
            session.execute(text(stmt))
            session.commit()

    def do_clear_vs(self):
        self.do_drop_kb()


if __name__ == "__main__":
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
