import sys
from pathlib import Path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from configs import ONLINE_LLM_MODEL
from server.model_workers.base import *
from server.utils import get_model_worker_config, list_config_llm_models
from pprint import pprint
import pytest


workers = []
for x in list_config_llm_models()["online"]:
    if x in ONLINE_LLM_MODEL and x not in workers:
        workers.append(x)
print(f"all workers to test: {workers}")

# workers = ["fangzhou-api"]


@pytest.mark.parametrize("worker", workers)
def test_chat(worker):
    params = ApiChatParams(
        messages = [
            {"role": "user", "content": "你是谁"},
        ],
    )
    print(f"\nchat with {worker} \n")

    if worker_class := get_model_worker_config(worker).get("worker_class"):
        for x in worker_class().do_chat(params):
            pprint(x)
            assert isinstance(x, dict)
            assert x["error_code"] == 0


@pytest.mark.parametrize("worker", workers)
def test_embeddings(worker):
    params = ApiEmbeddingsParams(
        texts = [
            "LangChain-Chatchat (原 Langchain-ChatGLM): 基于 Langchain 与 ChatGLM 等大语言模型的本地知识库问答应用实现。",
            "一种利用 langchain 思想实现的基于本地知识库的问答应用，目标期望建立一套对中文场景与开源模型支持友好、可离线运行的知识库问答解决方案。",
        ]
    )

    if worker_class := get_model_worker_config(worker).get("worker_class"):
        if worker_class.can_embedding():
            print(f"\embeddings with {worker} \n")
            resp = worker_class().do_embeddings(params)

            pprint(resp, depth=2)
            assert resp["code"] == 200
            assert "data" in resp
            embeddings = resp["data"]
            assert isinstance(embeddings, list) and len(embeddings) > 0
            assert isinstance(embeddings[0], list) and len(embeddings[0]) > 0
            assert isinstance(embeddings[0][0], float)
            print("向量长度：", len(embeddings[0]))


# @pytest.mark.parametrize("worker", workers)
# def test_completion(worker):
#     params = ApiCompletionParams(prompt="五十六个民族")
    
#     print(f"\completion with {worker} \n")

#     worker_class = get_model_worker_config(worker)["worker_class"]
#     resp = worker_class().do_completion(params)
#     pprint(resp)
