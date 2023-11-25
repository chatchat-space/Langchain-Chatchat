import requests
import json
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))
from server.utils import api_address

api_base_url = api_address()

kb = "samples"
file_name = "/media/gpt4-pdf-chatbot-langchain/langchain-ChatGLM/knowledge_base/samples/content/llm/大模型技术栈-实战与应用.md"


def test_summary_file_to_vector_store(api="/knowledge_base/kb_summary_api/summary_file_to_vector_store"):
    url = api_base_url + api
    print("\n文件摘要：")
    r = requests.post(url, json={"knowledge_base_name": kb,
                                 "file_name": file_name
                                 }, stream=True)
    for chunk in r.iter_content(None):
        data = json.loads(chunk)
        assert isinstance(data, dict)
        assert data["code"] == 200
        print(data["msg"])
