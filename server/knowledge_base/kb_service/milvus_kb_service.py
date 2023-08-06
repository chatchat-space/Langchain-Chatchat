from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)

from server.knowledge_base.kb_service.base import KBService


def get_collection(milvus_name):
    return Collection(milvus_name)


def search(milvus_name, content, limit=3):
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }
    c = get_collection(milvus_name)
    return c.search(content, "embeddings", search_params, limit=limit, output_fields=["random"])


class MilvusKBService():
    milvus_host: str
    milvus_port: int
    dim: int

    def __init__(self, knowledge_base_name: str, vector_store_type: str, milvus_host="localhost", milvus_port=19530,
                 dim=8):

        super().__init__(knowledge_base_name, vector_store_type)
        self.milvus_host = milvus_host
        self.milvus_port = milvus_port
        self.dim = dim

    def connect(self):
        connections.connect("default", host=self.milvus_host, port=self.milvus_port)

    def create_collection(self, milvus_name):
        fields = [
            FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="content", dtype=DataType.STRING),
            FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
        ]
        schema = CollectionSchema(fields)
        collection = Collection(milvus_name, schema)
        index = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        collection.create_index("embeddings", index)
        collection.load()
        return collection

    def insert_collection(self, milvus_name, content=[]):
        get_collection(milvus_name).insert(dataset)


if __name__ == '__main__':
    milvusService = MilvusService(milvus_host='192.168.50.128')
    milvusService.insert_collection(test,dataset)
