from server.knowledge_base.kb_service.base import KBService, SupportedVSType
from server.db.repository.knowledge_base_repository import load_kb_from_db
from server.knowledge_base.kb_service.default_kb_service import DefaultKBService


class KBServiceFactory:

    @staticmethod
    def get_service(kb_name: str,
                    vector_store_type: SupportedVSType
                    ) -> KBService:
        if SupportedVSType.FAISS == vector_store_type:
            from server.knowledge_base.kb_service.faiss_kb_service import FaissKBService
            return FaissKBService(kb_name)
        elif SupportedVSType.MILVUS == vector_store_type:
            from server.knowledge_base.kb_service.milvus_kb_service import MilvusKBService
            return MilvusKBService(kb_name)
        elif SupportedVSType.DEFAULT == vector_store_type:
            return DefaultKBService(kb_name)

    @staticmethod
    def get_service_by_name(kb_name: str
                            ) -> KBService:
        kb_name, vs_type, _ = load_kb_from_db(kb_name)
        return KBServiceFactory.get_service(kb_name, vs_type)

    @staticmethod
    def get_default():
        return KBServiceFactory.get_service("default", SupportedVSType.DEFAULT)


if __name__ == '__main__':
    # 测试建表使用
    # from server.db.base import Base, engine
    # Base.metadata.create_all(bind=engine)
    KBService = KBServiceFactory.get_service("test", SupportedVSType.FAISS)
    KBService.create_kb()
    KBService = KBServiceFactory.get_default()
    print(KBService.list_kbs())
    KBService = KBServiceFactory.get_service_by_name("test")
    print(KBService.list_docs())
    KBService.drop_kb()
