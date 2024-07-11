import json
import sys
from pathlib import Path

import requests

sys.path.append(str(Path(__file__).parent.parent.parent))
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint

from chatchat.server.utils import api_address

api_base_url = api_address()


def dump_input(d, title):
    print("\n")
    print("=" * 30 + title + "  input " + "=" * 30)
    pprint(d)


def dump_output(r, title):
    print("\n")
    print("=" * 30 + title + "  output" + "=" * 30)
    for line in r.iter_content(None, decode_unicode=True):
        print(line, end="", flush=True)


headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


def knowledge_chat(api="/chat/knowledge_base_chat"):
    url = f"{api_base_url}{api}"
    data = {
        "query": "如何提问以获得高质量答案",
        "knowledge_base_name": "samples",
        "history": [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好，我是 ChatGLM"},
        ],
        "stream": True,
    }
    result = []
    response = requests.post(url, headers=headers, json=data, stream=True)

    for line in response.iter_content(None, decode_unicode=True):
        data = json.loads(line[6:])
        result.append(data)

    return result


def test_thread():
    threads = []
    times = []
    pool = ThreadPoolExecutor()
    start = time.time()
    for i in range(10):
        t = pool.submit(knowledge_chat)
        threads.append(t)

    for r in as_completed(threads):
        end = time.time()
        times.append(end - start)
        print("\nResult:\n")
        pprint(r.result())

    print("\nTime used:\n")
    for x in times:
        print(f"{x}")
