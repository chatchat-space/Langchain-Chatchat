import requests
import json
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))
from server.utils import api_address
from configs.model_config import VECTOR_SEARCH_TOP_K
from server.knowledge_base.utils import get_kb_path

from pprint import pprint


api_base_url = api_address()

kb = "kb_for_api_test"
test_files = {
    "README.MD": str(root_path / "README.MD"),
    "FAQ.MD": str(root_path / "docs" / "FAQ.MD")
}


def test_delete_kb_before(api="/knowledge_base/delete_knowledge_base"):
    if not Path(get_kb_path(kb)).exists():
        return

    url = api_base_url + api
    print("\n测试知识库存在，需要删除")
    r = requests.post(url, json=kb)
    data = r.json()
    pprint(data)

    # check kb not exists anymore
    url = api_base_url + "/knowledge_base/list_knowledge_bases"
    print("\n获取知识库列表：")
    r = requests.get(url)
    data = r.json()
    pprint(data)
    assert data["code"] == 200
    assert isinstance(data["data"], list) and len(data["data"]) > 0
    assert kb not in data["data"]


def test_create_kb(api="/knowledge_base/create_knowledge_base"):
    url = api_base_url + api

    print(f"\n尝试用空名称创建知识库：")
    r = requests.post(url, json={"knowledge_base_name": " "})
    data = r.json()
    pprint(data)
    assert data["code"] == 404
    assert data["msg"] == "知识库名称不能为空，请重新填写知识库名称"

    print(f"\n创建新知识库： {kb}")
    r = requests.post(url, json={"knowledge_base_name": kb})
    data = r.json()
    pprint(data)
    assert data["code"] == 200
    assert data["msg"] == f"已新增知识库 {kb}"

    print(f"\n尝试创建同名知识库： {kb}")
    r = requests.post(url, json={"knowledge_base_name": kb})
    data = r.json()
    pprint(data)
    assert data["code"] == 404
    assert data["msg"] == f"已存在同名知识库 {kb}"


def test_list_kbs(api="/knowledge_base/list_knowledge_bases"):
    url = api_base_url + api
    print("\n获取知识库列表：")
    r = requests.get(url)
    data = r.json()
    pprint(data)
    assert data["code"] == 200
    assert isinstance(data["data"], list) and len(data["data"]) > 0
    assert kb in data["data"]


def test_upload_doc(api="/knowledge_base/upload_doc"):
    url = api_base_url + api
    for name, path in test_files.items():
        print(f"\n上传知识文件： {name}")
        data = {"knowledge_base_name": kb, "override": True}
        files = {"file": (name, open(path, "rb"))}
        r = requests.post(url, data=data, files=files)
        data = r.json()
        pprint(data)
        assert data["code"] == 200
        assert data["msg"] == f"成功上传文件 {name}"

    for name, path in test_files.items():
        print(f"\n尝试重新上传知识文件： {name}， 不覆盖")
        data = {"knowledge_base_name": kb, "override": False}
        files = {"file": (name, open(path, "rb"))}
        r = requests.post(url, data=data, files=files)
        data = r.json()
        pprint(data)
        assert data["code"] == 404
        assert data["msg"] == f"文件 {name} 已存在。"

    for name, path in test_files.items():
        print(f"\n尝试重新上传知识文件： {name}， 覆盖")
        data = {"knowledge_base_name": kb, "override": True}
        files = {"file": (name, open(path, "rb"))}
        r = requests.post(url, data=data, files=files)
        data = r.json()
        pprint(data)
        assert data["code"] == 200
        assert data["msg"] == f"成功上传文件 {name}"


def test_list_files(api="/knowledge_base/list_files"):
    url = api_base_url + api
    print("\n获取知识库中文件列表：")
    r = requests.get(url, params={"knowledge_base_name": kb})
    data = r.json()
    pprint(data)
    assert data["code"] == 200
    assert isinstance(data["data"], list)
    for name in test_files:
        assert name in data["data"]


def test_search_docs(api="/knowledge_base/search_docs"):
    url = api_base_url + api
    query = "介绍一下langchain-chatchat项目"
    print("\n检索知识库：")
    print(query)
    r = requests.post(url, json={"knowledge_base_name": kb, "query": query})
    data = r.json()
    pprint(data)
    assert isinstance(data, list) and len(data) == VECTOR_SEARCH_TOP_K


def test_update_doc(api="/knowledge_base/update_doc"):
    url = api_base_url + api
    for name, path in test_files.items():
        print(f"\n更新知识文件： {name}")
        r = requests.post(url, json={"knowledge_base_name": kb, "file_name": name})
        data = r.json()
        pprint(data)
        assert data["code"] == 200
        assert data["msg"] == f"成功更新文件 {name}"


def test_delete_doc(api="/knowledge_base/delete_doc"):
    url = api_base_url + api
    for name, path in test_files.items():
        print(f"\n删除知识文件： {name}")
        r = requests.post(url, json={"knowledge_base_name": kb, "doc_name": name})
        data = r.json()
        pprint(data)
        assert data["code"] == 200
        assert data["msg"] == f"{name} 文件删除成功"

    url = api_base_url + "/knowledge_base/search_docs"
    query = "介绍一下langchain-chatchat项目"
    print("\n尝试检索删除后的检索知识库：")
    print(query)
    r = requests.post(url, json={"knowledge_base_name": kb, "query": query})
    data = r.json()
    pprint(data)
    assert isinstance(data, list) and len(data) == 0


def test_recreate_vs(api="/knowledge_base/recreate_vector_store"):
    url = api_base_url + api
    print("\n重建知识库：")
    r = requests.post(url, json={"knowledge_base_name": kb}, stream=True)
    for chunk in r.iter_content(None):
        data = json.loads(chunk)
        assert isinstance(data, dict)
        assert data["code"] == 200
        print(data["msg"])

    url = api_base_url + "/knowledge_base/search_docs"
    query = "本项目支持哪些文件格式?"
    print("\n尝试检索重建后的检索知识库：")
    print(query)
    r = requests.post(url, json={"knowledge_base_name": kb, "query": query})
    data = r.json()
    pprint(data)
    assert isinstance(data, list) and len(data) == VECTOR_SEARCH_TOP_K


def test_delete_kb_after(api="/knowledge_base/delete_knowledge_base"):
    url = api_base_url + api
    print("\n删除知识库")
    r = requests.post(url, json=kb)
    data = r.json()
    pprint(data)

    # check kb not exists anymore
    url = api_base_url + "/knowledge_base/list_knowledge_bases"
    print("\n获取知识库列表：")
    r = requests.get(url)
    data = r.json()
    pprint(data)
    assert data["code"] == 200
    assert isinstance(data["data"], list) and len(data["data"]) > 0
    assert kb not in data["data"]
