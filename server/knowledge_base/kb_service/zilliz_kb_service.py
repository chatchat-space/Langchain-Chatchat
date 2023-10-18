from typing import List, Dict, Optional
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import Zilliz
from configs import kbs_config
from server.knowledge_base.kb_service.base import KBService, SupportedVSType, EmbeddingsFunAdapter, \
    score_threshold_process
from server.knowledge_base.utils import KnowledgeFile


class ZillizKBService(KBService):
    zilliz: Zilliz

    @staticmethod
    def get_collection(zilliz_name):
        from pymilvus import Collection
        return Collection(zilliz_name)

    # def save_vector_store(self):
    #     if self.zilliz.col:
    #         self.zilliz.col.flush()

    def get_doc_by_id(self, id: str) -> Optional[Document]:
        if self.zilliz.col:
            data_list = self.zilliz.col.query(expr=f'pk == {id}', output_fields=["*"])
            if len(data_list) > 0:
                data = data_list[0]
                text = data.pop("text")
                return Document(page_content=text, metadata=data)

    @staticmethod
    def search(zilliz_name, content, limit=3):
        search_params = {
            "metric_type": "IP",
            "params": {},
        }
        c = ZillizKBService.get_collection(zilliz_name)
        return c.search(content, "embeddings", search_params, limit=limit, output_fields=["content"])

    def do_create_kb(self):
        pass

    def vs_type(self) -> str:
        return SupportedVSType.ZILLIZ

    def _load_zilliz(self, embeddings: Embeddings = None):
        if embeddings is None:
            embeddings = self._load_embeddings()
        zilliz_args = kbs_config.get("zilliz")
        self.zilliz = Zilliz(embedding_function=EmbeddingsFunAdapter(embeddings),
                            collection_name=self.kb_name, connection_args=zilliz_args)


    def do_init(self):
        self._load_zilliz()

    def do_drop_kb(self):
        if self.zilliz.col:
            self.zilliz.col.release()
            self.zilliz.col.drop()

    def do_search(self, query: str, top_k: int, score_threshold: float, embeddings: Embeddings):
        self._load_zilliz(embeddings=EmbeddingsFunAdapter(embeddings))
        return score_threshold_process(score_threshold, top_k, self.zilliz.similarity_search_with_score(query, top_k))

    def do_add_doc(self, docs: List[Document], **kwargs) -> List[Dict]:
        for doc in docs:
            for k, v in doc.metadata.items():
                doc.metadata[k] = str(v)
            for field in self.zilliz.fields:
                doc.metadata.setdefault(field, "")
            doc.metadata.pop(self.zilliz._text_field, None)
            doc.metadata.pop(self.zilliz._vector_field, None)

        ids = self.zilliz.add_documents(docs)
        doc_infos = [{"id": id, "metadata": doc.metadata} for id, doc in zip(ids, docs)]
        return doc_infos

    def do_delete_doc(self, kb_file: KnowledgeFile, **kwargs):
        if self.zilliz.col:
            filepath = kb_file.filepath.replace('\\', '\\\\')
            delete_list = [item.get("pk") for item in
                           self.zilliz.col.query(expr=f'source == "{filepath}"', output_fields=["pk"])]
            self.zilliz.col.delete(expr=f'pk in {delete_list}')

    def do_clear_vs(self):
        if self.zilliz.col:
            self.do_drop_kb()
            self.do_init()


if __name__ == '__main__':

    from server.db.base import Base, engine

    Base.metadata.create_all(bind=engine)
    zillizService = ZillizKBService("test")

