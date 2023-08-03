import requests

payload = {"question": "美国大学"}
# ret = requests.get("http://0.0.0.0:7861/local_doc_search_chat", json=payload)
# for i in ret:
#     print(i)

for i in requests.get(url="http://0.0.0.0:7861/local_doc_search_stream_chat", json=payload, stream=True):
    print(i)
