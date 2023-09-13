#!/user/bin/env python3
"""
File_Name: es_kb_service.py
Author: TangGuoLiang
Email: 896165277@qq.com
Created: 2023-09-05
"""
from typing import List
import os
import shutil
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores.elasticsearch import ElasticsearchStore
from configs.model_config import KB_ROOT_PATH, EMBEDDING_MODEL, EMBEDDING_DEVICE, CACHED_VS_NUM
from server.knowledge_base.kb_service.base import KBService, SupportedVSType
from server.knowledge_base.utils import load_embeddings
from elasticsearch import Elasticsearch
from configs.model_config import logger
from configs.model_config import kbs_config

class ESKBService(KBService):

    def do_init(self):
        self.kb_path = self.get_kb_path(self.kb_name)
        self.index_name = self.kb_path.split("/")[-1]
        self.IP = kbs_config[self.vs_type()]['host']
        self.PORT = kbs_config[self.vs_type()]['port']
        self.embeddings_model = load_embeddings(self.embed_model, EMBEDDING_DEVICE)
        try:
            # ES python客户端连接（仅连接）
            self.es_client_python = Elasticsearch(f"{self.IP}:{self.PORT}")
        except ConnectionError:
            logger.error("连接到 Elasticsearch 失败！")
        except Exception as e:
            logger.error(f"Error 发生 : {e}")

        try:
            # langchain ES 连接、创建索引
            self.db_init = ElasticsearchStore(
                es_url=f"{self.IP}:{self.PORT}",
                index_name=self.index_name,
                query_field="context",
                vector_query_field="vector",
                embedding=self.embeddings_model,
            )
        except ConnectionError:
            logger.error("### 连接到 Elasticsearch 失败！")
        except Exception as e:
            logger.error(f"Error 发生 : {e}")

    @staticmethod
    def get_kb_path(knowledge_base_name: str):
        return os.path.join(KB_ROOT_PATH, knowledge_base_name)

    @staticmethod
    def get_vs_path(knowledge_base_name: str):
        return os.path.join(ESKBService.get_kb_path(knowledge_base_name), "vector_store")

    def do_create_kb(self):
        if os.path.exists(self.doc_path):
            os.makedirs(os.path.join(self.kb_path, "vector_store"))

    def vs_type(self) -> str:
        return SupportedVSType.ES

    def _load_es(self, docs, embed_model):
        # 将docs写入到ES中
        try:
            # 连接 + 同时写入文档
            self.db = ElasticsearchStore.from_documents(
                    documents=docs,
                    embedding=embed_model,
                    es_url= f"{self.IP}:{self.PORT}",
                    index_name=self.index_name,
                    distance_strategy="COSINE",
                    query_field="context",
                    vector_query_field="vector",
                    verify_certs=False,
                )
        except ConnectionError:
            logger.error("连接到 Elasticsearch 失败！")
        except Exception as e:
            logger.error(f"Error 发生 : {e}")



    def do_search(self, query:str, top_k: int, score_threshold: float, embeddings: Embeddings):
        # 文本相似性检索
        docs = self.db_init.similarity_search_with_score(query=query,
                                         k=top_k)
        return docs


    def do_delete_doc(self, kb_file, **kwargs):
        if self.es_client_python.indices.exists(index=self.index_name):
            # 从向量数据库中删除索引(文档名称是Keyword)
            query = {
                "query": {
                    "term": {
                        "metadata.source.keyword": kb_file.filepath
                    }
                }
            }
            # 注意设置size，默认返回10个。
            search_results = self.es_client_python.search(body=query, size=50)
            delete_list = [hit["_id"] for hit in search_results['hits']['hits']]
            if len(delete_list) == 0:
                return None
            else:
                for doc_id in delete_list:
                    try:
                        self.es_client_python.delete(index=self.index_name,
                                                     id=doc_id,
                                                     refresh=True)
                    except Exception as e:
                        logger.error("ES Docs Delete Error!")

            # self.db_init.delete(ids=delete_list)
            #self.es_client_python.indices.refresh(index=self.index_name)


    def do_add_doc(self, docs: List[Document], **kwargs):
        '''向知识库添加文件'''
        self._load_es(docs=docs, embed_model=self.embeddings_model)
        # 获取 id 和 source , 格式：[{"id": str, "metadata": dict}, ...]
        file_path = docs[0].metadata.get("source")
        if self.es_client_python.indices.exists(index=self.index_name):
            query = {
                "query": {
                    "term": {
                        "metadata.source.keyword": file_path
                    }
                }
            }
            search_results = self.es_client_python.search(body=query)
            if len(search_results["hits"]["hits"]) == 0:
                raise ValueError("召回元素个数为0")
            info_docs = [{"id":hit["_id"], "metadata": hit["_source"]["metadata"]} for hit in search_results["hits"]["hits"]]
            return info_docs


    def do_clear_vs(self):
        """从知识库删除全部向量"""
        if self.es_client_python.indices.exists(index=self.kb_name):
            self.es_client_python.indices.delete(index=self.kb_name)


    def do_drop_kb(self):
        """删除知识库"""
        # self.kb_file: 知识库路径
        if os.path.exists(self.kb_path):
            shutil.rmtree(self.kb_path)








