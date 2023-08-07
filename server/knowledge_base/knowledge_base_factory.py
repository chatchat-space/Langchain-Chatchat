from typing import Union
from server.knowledge_base.kb_service.base import KBService, SupportedVSType, init_db, load_kb_from_db
from server.knowledge_base.kb_service.default_kb_service import DefaultKBService
from server.knowledge_base.kb_service.milvus_kb_service import MilvusKBService
from configs.model_config import EMBEDDING_MODEL


class KBServiceFactory:

    @staticmethod
    def get_service(kb_name: str,
                    vector_store_type: Union[str, SupportedVSType],
                    embed_model: str = EMBEDDING_MODEL,
                    ) -> KBService:
        if isinstance(vector_store_type, str):
            vector_store_type = getattr(SupportedVSType, vector_store_type.upper())
        if SupportedVSType.FAISS == vector_store_type:
            from server.knowledge_base.kb_service.faiss_kb_service import FaissKBService
            return FaissKBService(kb_name, embed_model=embed_model)
        # todo: Milvus has different init params
        # elif SupportedVSType.MILVUS == vector_store_type:
        #     from server.knowledge_base.kb_service.milvus_kb_service import MilvusKBService
        #     return MilvusKBService(kb_name,)
        elif SupportedVSType.DEFAULT == vector_store_type: # kb_exists of default kbservice is False, to make validation easier.
            return DefaultKBService(kb_name)

    @staticmethod
    def get_service_by_name(kb_name: str
                            ) -> KBService:
        kb_name, vs_type, embed_model = load_kb_from_db(kb_name)
        return KBServiceFactory.get_service(kb_name, vs_type, embed_model)

    @staticmethod
    def get_default():
        return KBServiceFactory.get_service("default", SupportedVSType.DEFAULT)


if __name__ == '__main__':
    KBService = KBServiceFactory.get_service("test", SupportedVSType.FAISS)
    init_db()
    KBService.create_kb()
    KBService = KBServiceFactory.get_default()
    print(KBService.list_kbs())
    KBService = KBServiceFactory.get_service_by_name("test")
    print(KBService.list_docs())
    KBService.drop_kb()
