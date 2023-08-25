from typing import List

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import Milvus

from configs.model_config import SCORE_THRESHOLD, kbs_config

from server.knowledge_base.kb_service.base import KBService, SupportedVSType
from server.knowledge_base.utils import KnowledgeFile


class MilvusKBService(KBService):
    milvus: Milvus

    @staticmethod
    def get_collection(milvus_name):
        from pymilvus import Collection
        return Collection(milvus_name)

    @staticmethod
    def search(milvus_name, content, limit=3):
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10},
        }
        c = MilvusKBService.get_collection(milvus_name)
        return c.search(content, "embeddings", search_params, limit=limit, output_fields=["content"])

    def do_create_kb(self):
        pass

    def vs_type(self) -> str:
        return SupportedVSType.MILVUS

    def _load_milvus(self, embeddings: Embeddings = None):
        if embeddings is None:
            embeddings = self._load_embeddings()
        self.milvus = Milvus(embedding_function=embeddings,
                             collection_name=self.kb_name, connection_args=kbs_config.get("milvus"))

    def do_init(self):
        self._load_milvus()

    def do_drop_kb(self):
        self.milvus.col.drop()

    def do_search(self, query: str, top_k: int,score_threshold: float, embeddings: Embeddings):
        # todo: support score threshold
        self._load_milvus(embeddings=embeddings)
        return self.milvus.similarity_search_with_score(query, top_k)

    def add_doc(self, kb_file: KnowledgeFile, **kwargs):
        """
        向知识库添加文件
        """
        docs = kb_file.file2text()
        self.milvus.add_documents(docs)
        from server.db.repository.knowledge_file_repository import add_doc_to_db
        status = add_doc_to_db(kb_file)
        return status

    def do_add_doc(self, docs: List[Document], embeddings: Embeddings, **kwargs):
        pass

    def do_delete_doc(self, kb_file: KnowledgeFile, **kwargs):
        filepath = kb_file.filepath.replace('\\', '\\\\')
        delete_list = [item.get("pk") for item in
                       self.milvus.col.query(expr=f'source == "{filepath}"', output_fields=["pk"])]
        self.milvus.col.delete(expr=f'pk in {delete_list}')

    def do_clear_vs(self):
        if self.milvus.col:
            self.milvus.col.drop()


if __name__ == '__main__':
    # 测试建表使用
    from server.db.base import Base, engine

    Base.metadata.create_all(bind=engine)
    milvusService = MilvusKBService("test")
    milvusService.add_doc(KnowledgeFile("README.md", "test"))
    milvusService.delete_doc(KnowledgeFile("README.md", "test"))
    milvusService.do_drop_kb()
    print(milvusService.search_docs("测试"))
