from server.knowledge_base.kb_service.base import KBService


class DefaultKBService(KBService):
    def vs_type(self) -> str:
        return "default"

    def do_create_kbs(self):
        pass

    def do_init(self):
        pass

    def do_remove_kbs(self):
        pass

    def do_search(self):
        pass

    def do_insert_multi_knowledge(self):
        pass

    def do_insert_one_knowledge(self):
        pass

    def do_delete(self):
        pass
