#encoding:utf-8
import json
import os
import nltk
import uvicorn
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request
import time

from chains.local_doc_qa import LocalDocSearch
from configs.model_config import (EMBEDDING_DEVICE,
                                  EMBEDDING_MODEL, NLTK_DATA_PATH,
                                  VECTOR_SEARCH_TOP_K, LOCAL_DOC_PATH)
import datetime

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

app = FastAPI()


def stream(json_post_raw):
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    question = json_post_list.get('question')
    result = local_doc_search.get_knowledge_based_stream_answer(query=question, vs_path=vs_path)
    for response in result:
        yield response
        time.sleep(0.0011)

@app.get("/local_doc_search_stream_chat")
async def local_product_search_stream_chat(request: Request):
    global local_doc_search
    global vs_path
    json_post_raw = await request.json()
    return StreamingResponse(stream(json_post_raw), media_type="text/event-stream")


@app.get("/local_doc_search_chat")
async def local_product_search_chat(request: Request):
    global local_doc_search
    global vs_path

    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    question = json_post_list.get('question')
    print("honey honey: ", json_post_list)
    now = datetime.datetime.now()
    time1 = now.strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(vs_path):
        answer = {
            "query": question,
            "result": f"Knowledge base not found",
            "status": 404,
            "time": time1
        }
        return answer
    # 获取相似知识
    result = local_doc_search.get_knowledge_based_answer(query=question, vs_path=vs_path)
    print(result.content)
    return result.content

if __name__ == "__main__":
    local_doc_search = LocalDocSearch()
    local_doc_search.init_cfg(
        embedding_model=EMBEDDING_MODEL,
        embedding_device=EMBEDDING_DEVICE,
        top_k=VECTOR_SEARCH_TOP_K,
    )
    # vs初始化
    vs_path = None
    temp, loaded_files = local_doc_search.init_knowledge_vector_store(filepath=LOCAL_DOC_PATH)
    if temp is not None:
        vs_path = temp
        # 如果loaded_files和len(filepath)不一致，则说明部分文件没有加载成功
        # 如果是路径错误，则应该支持重新加载
        print(f"the loaded vs_path is 加载的vs_path为: {vs_path}")

    config = uvicorn.Config(app, host='0.0.0.0', port=7861, workers=1, log_level="info")
    server = uvicorn.Server(config)
    server.run()
