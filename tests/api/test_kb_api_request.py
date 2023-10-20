import requests
import json
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))
from server.utils import api_address
from configs import VECTOR_SEARCH_TOP_K
from server.knowledge_base.utils import get_kb_path, get_file_path
from webui_pages.utils import ApiRequest

from pprint import pprint


api_base_url = api_address()
api: ApiRequest = ApiRequest(api_base_url)


kb = "kb_for_api_test"
test_files = {
    "FAQ.MD": str(root_path / "docs" / "FAQ.MD"),
    "README.MD": str(root_path / "README.MD"),
    "test.txt": get_file_path("samples", "test.txt"),
}

print("\n\nApiRquest调用\n")


def test_delete_kb_before():
    if not Path(get_kb_path(kb)).exists():
        return

    data = api.delete_knowledge_base(kb)
    pprint(data)
    assert data["code"] == 200
    assert isinstance(data["data"], list) and len(data["data"]) > 0
    assert kb not in data["data"]


def test_create_kb():
    print(f"\n尝试用空名称创建知识库：")
    data = api.create_knowledge_base(" ")
    pprint(data)
    assert data["code"] == 404
    assert data["msg"] == "知识库名称不能为空，请重新填写知识库名称"

    print(f"\n创建新知识库： {kb}")
    data = api.create_knowledge_base(kb)
    pprint(data)
    assert data["code"] == 200
    assert data["msg"] == f"已新增知识库 {kb}"

    print(f"\n尝试创建同名知识库： {kb}")
    data = api.create_knowledge_base(kb)
    pprint(data)
    assert data["code"] == 404
    assert data["msg"] == f"已存在同名知识库 {kb}"


def test_list_kbs():
    data = api.list_knowledge_bases()
    pprint(data)
    assert isinstance(data, list) and len(data) > 0
    assert kb in data


def test_upload_docs():
    files = list(test_files.values())

    print(f"\n上传知识文件")
    data = {"knowledge_base_name": kb, "override": True}
    data = api.upload_kb_docs(files, **data)
    pprint(data)
    assert data["code"] == 200
    assert len(data["data"]["failed_files"]) == 0

    print(f"\n尝试重新上传知识文件， 不覆盖")
    data = {"knowledge_base_name": kb, "override": False}
    data = api.upload_kb_docs(files, **data)
    pprint(data)
    assert data["code"] == 200
    assert len(data["data"]["failed_files"]) == len(test_files)

    print(f"\n尝试重新上传知识文件， 覆盖，自定义docs")
    docs = {"FAQ.MD": [{"page_content": "custom docs", "metadata": {}}]}
    data = {"knowledge_base_name": kb, "override": True, "docs": docs}
    data = api.upload_kb_docs(files, **data)
    pprint(data)
    assert data["code"] == 200
    assert len(data["data"]["failed_files"]) == 0


def test_list_files():
    print("\n获取知识库中文件列表：")
    data = api.list_kb_docs(knowledge_base_name=kb)
    pprint(data)
    assert isinstance(data, list)
    for name in test_files:
        assert name in data


def test_search_docs():
    query = "介绍一下langchain-chatchat项目"
    print("\n检索知识库：")
    print(query)
    data = api.search_kb_docs(query, kb)
    pprint(data)
    assert isinstance(data, list) and len(data) == VECTOR_SEARCH_TOP_K


def test_update_docs():
    print(f"\n更新知识文件")
    data = api.update_kb_docs(knowledge_base_name=kb, file_names=list(test_files))
    pprint(data)
    assert data["code"] == 200
    assert len(data["data"]["failed_files"]) == 0


def test_delete_docs():
    print(f"\n删除知识文件")
    data = api.delete_kb_docs(knowledge_base_name=kb, file_names=list(test_files))
    pprint(data)
    assert data["code"] == 200
    assert len(data["data"]["failed_files"]) == 0

    query = "介绍一下langchain-chatchat项目"
    print("\n尝试检索删除后的检索知识库：")
    print(query)
    data = api.search_kb_docs(query, kb)
    pprint(data)
    assert isinstance(data, list) and len(data) == 0


def test_recreate_vs():
    print("\n重建知识库：")
    r = api.recreate_vector_store(kb)
    for data in r:
        assert isinstance(data, dict)
        assert data["code"] == 200
        print(data["msg"])

    query = "本项目支持哪些文件格式?"
    print("\n尝试检索重建后的检索知识库：")
    print(query)
    data = api.search_kb_docs(query, kb)
    pprint(data)
    assert isinstance(data, list) and len(data) == VECTOR_SEARCH_TOP_K


def test_delete_kb_after():
    print("\n删除知识库")
    data = api.delete_knowledge_base(kb)
    pprint(data)

    # check kb not exists anymore
    print("\n获取知识库列表：")
    data = api.list_knowledge_bases()
    pprint(data)
    assert isinstance(data, list) and len(data) > 0
    assert kb not in data
