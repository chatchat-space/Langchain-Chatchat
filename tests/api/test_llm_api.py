import requests
import json
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))
from configs.server_config import FSCHAT_MODEL_WORKERS
from server.utils import api_address, get_model_worker_config

from pprint import pprint
import random
from typing import List


def get_configured_models() -> List[str]:
    model_workers = list(FSCHAT_MODEL_WORKERS)
    if "default" in model_workers:
        model_workers.remove("default")
    return model_workers


api_base_url = api_address()


def get_running_models(api="/llm_model/list_models"):
    url = api_base_url + api
    r = requests.post(url)
    if r.status_code == 200:
        return r.json()["data"]
    return []


def test_running_models(api="/llm_model/list_running_models"):
    url = api_base_url + api
    r = requests.post(url)
    assert r.status_code == 200
    print("\n获取当前正在运行的模型列表：")
    pprint(r.json())
    assert isinstance(r.json()["data"], list)
    assert len(r.json()["data"]) > 0


# 不建议使用stop_model功能。按现在的实现，停止了就只能手动再启动
# def test_stop_model(api="/llm_model/stop"):
#     url = api_base_url + api
#     r = requests.post(url, json={""})


def test_change_model(api="/llm_model/change_model"):
    url = api_base_url + api

    running_models = get_running_models()
    assert len(running_models) > 0

    model_workers = get_configured_models()

    availabel_new_models = list(set(model_workers) - set(running_models))
    assert len(availabel_new_models) > 0
    print(availabel_new_models)

    local_models = [x for x in running_models if not get_model_worker_config(x).get("online_api")]
    model_name = random.choice(local_models)
    new_model_name = random.choice(availabel_new_models)
    print(f"\n尝试将模型从 {model_name} 切换到 {new_model_name}")
    r = requests.post(url, json={"model_name": model_name, "new_model_name": new_model_name})
    assert r.status_code == 200

    running_models = get_running_models()
    assert new_model_name in running_models
