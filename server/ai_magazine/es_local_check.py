from elasticsearch import Elasticsearch

es = Elasticsearch(
        ["http://localhost:9200"],
        sniff_on_start=False,            # 连接前测试
        sniff_on_connection_fail=True,  # 节点无响应时刷新节点
        sniffer_timeout=60              # 设置超时时间
    )


# 找到索引shijie下的所有内容
def es_search_all(index):
    res = es.search(index=index, body={"query": {"match_all": {}}})
    print(res)
    return res

# 删除某个索引
def es_delete_index(index):
    res = es.indices.delete(index=index)
    print(res)
    return res

# 创建某个索引
def es_create_index(index):
    res = es.indices.create(index=index)
    print(res)
    return res


# 查询是否存在某条数据的id字段
def es_search_id(index, id):
    res = es.search(index=index, body={"query": {"match": {"id": id}}})
    print(res)
    return res


# 进行某个查询
def es_search_test():
    # 查询index为shijie下,relatedMajors.name.keyword字段为计算机科学与技术,且topicTags.name.keyword字段为专业重点扫盲的文章
    query = {
        "size": 10,  # 指定返回的文档数量
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "relatedMajors.name.keyword": "计算机科学与技术"
                        }
                    },
                    {
                        "match": {
                            "topicTags.name.keyword": "专业重点扫盲"
                        }
                    }
                ]
            }
        }
    }
    
    res = es.search(index="shijie", body=query)
    print(len(res["hits"]["hits"]))


# es_search_all("shijie")
# es_delete_index("shijie")
es_create_index("shijie")
# es_search_id("shijie", "234")
# es_search_test()