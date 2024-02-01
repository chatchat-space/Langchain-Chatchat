from elasticsearch import Elasticsearch
from fastapi import Body
from fastapi.responses import JSONResponse
from typing import *

# 增加时间格式 YYYY-MM-DD HH:MM
import time
import datetime
time_format = "%Y-%m-%d %H:%M"


# 连接ES
es = Elasticsearch(
    ["http://localhost:9200"],
    sniff_on_start=False,            # 连接前测试
    sniff_on_connection_fail=True,  # 节点无响应时刷新节点
    sniffer_timeout=60              # 设置超时时间
)

def es_search_id(index, id):
    res = es.search(index=index, body={"query": {"match": {"id": id}}})
    return res["hits"]["hits"], len(res["hits"]["hits"])

def es_add_data(
    index_name: str = Body(..., description="索引名称", examples=["shijie"]),
    input_data: Optional[List] = Body([], description="输入指令", examples=[{"id":"123","title":"清华人物"}]),
):
    ret = {
        "status": "",
        "response" : ""
    }
    
    wrong_list = []
    
    # res = es.index(index='shijie', body=data)
    if len(input_data) == 0:
        ret["response"] = "没有提供数据"
        return JSONResponse(ret)
    else:
        for t in input_data:
            # 判断当前数据库有没有这个id, 有的话就覆盖，没有的话就添加
            es_search_id_res, len_check = es_search_id(index_name, t["id"])
            if len_check < 1:
                t["created_at"] = datetime.datetime.now().strftime(time_format)
                t["last_modifier_at"] = datetime.datetime.now().strftime(time_format)
                print(t)
                res = es.index(index=index_name, body=t)
                if res["result"] == "created":
                    print("添加成功")
                else:
                    wrong_list.append(t["id"])
            else:
                for temp in es_search_id_res:
                    print(temp["_id"])
                    t["created_at"] = temp["_source"]["created_at"]
                    t["last_modifier_at"] = datetime.datetime.now().strftime(time_format)
                    update_query = {
                        "doc": t
                    }
                    res = es.update(index=index_name, id=temp["_id"], body=update_query, doc_type="_doc")
                    if res["result"] == "updated":
                        print("更新成功")
                    else:
                        if res["result"] == "noop":
                            pass
                        else:
                            print("更新失败")
                            wrong_list.append(t["id"])
            print(res)
    
    if len(wrong_list) ==0:
        ret["status"] = "success"
        ret["response"] = "添加成功"
    else:
        ret["status"] = "fail"
        ret["response"] = "添加失败，id为" + str(wrong_list) + "的数据添加失败"
    
    return JSONResponse(ret)

