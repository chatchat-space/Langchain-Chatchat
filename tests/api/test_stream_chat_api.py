import requests
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from configs.server_config import API_SERVER, api_address

from pprint import pprint


api_base_url = api_address()


def dump_input(d, title):
    print("\n")
    print("=" * 30 + title + "  input " + "="*30)
    pprint(d)


def dump_output(r, title):
    print("\n")
    print("=" * 30 + title + "  output" + "="*30)
    for line in r.iter_content(None, decode_unicode=True):
        print(line, end="", flush=True)


headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

data = {
    "query": "请用100字左右的文字介绍自己",
    "history": [
        {
            "role": "user",
            "content": "你好"
        },
        {
            "role": "assistant",
            "content": "你好，我是 ChatGLM"
        }
    ],
    "stream": True
}



def test_chat_fastchat(api="/chat/fastchat"):
    url = f"{api_base_url}{api}"
    data2 = {
        "stream": True,
        "messages": data["history"] + [{"role": "user", "content": "推荐一部科幻电影"}]
    }
    dump_input(data2, api)
    response = requests.post(url, headers=headers, json=data2, stream=True)
    dump_output(response, api)
    assert response.status_code == 200


def test_chat_chat(api="/chat/chat"):
    url = f"{api_base_url}{api}"
    dump_input(data, api)
    response = requests.post(url, headers=headers, json=data, stream=True)
    dump_output(response, api)
    assert response.status_code == 200


def test_knowledge_chat(api="/chat/knowledge_base_chat"):
    url = f"{api_base_url}{api}"
    data = {
        "query": "如何提问以获得高质量答案",
        "knowledge_base_name": "samples",
        "history": [
            {
                "role": "user",
                "content": "你好"
            },
            {
                "role": "assistant",
                "content": "你好，我是 ChatGLM"
            }
        ],
        "stream": True
    }
    dump_input(data, api)
    response = requests.post(url, headers=headers, json=data, stream=True)
    print("\n")
    print("=" * 30 + api + "  output" + "="*30)
    first = True
    for line in response.iter_content(None, decode_unicode=True):
        data = json.loads(line)
        if first:
            for doc in data["docs"]:
                print(doc)
            first = False
        print(data["answer"], end="", flush=True)
    assert response.status_code == 200


def test_search_engine_chat(api="/chat/search_engine_chat"):
    url = f"{api_base_url}{api}"
    for se in ["bing", "duckduckgo"]:
        dump_input(data, api)
        response = requests.post(url, json=data, stream=True)
        dump_output(response, api)
        assert response.status_code == 200
