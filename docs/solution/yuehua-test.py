import requests

base_url = "http://127.0.0.1:7861/chat"

# data = {
#     "model": "qwen2-instruct",
#     "messages": [
#         {"role": "user", "content": "请以`斗破苍穹小医仙`的故事为背景，写一篇300字的短篇小说."},
#     ],
#     # "stream": True,
#     "stream": False,
#     "temperature": 0.7,
#     # "max_tokens": 4096,
#     # "max_tokens": 30,
# }

# tools = list(requests.get(f"http://127.0.0.1:7861/tools").json()["data"])
# data = {
#     "model": "qwen2-instruct",
#     "messages": [
#         {"role": "user", "content": "请以`斗破苍穹小医仙`的故事为背景，写一篇300字的短篇小说."},
#     ],
#     "stream": True,
#     "temperature": 0.7,
#     "tools": tools,
#     # "max_tokens": 4096,
#     # "max_tokens": 30,
# }

# tools = list(requests.get(f"http://127.0.0.1:7861/tools").json()["data"])
# data = {
#     "model": "qwen2-instruct",
#     "messages": [
#         {"role": "user", "content": "37+48=？"},
#     ],
#     "stream": True,
#     "temperature": 0.7,
#     "tools": tools,
#     # "max_tokens": 4096,
#     # "max_tokens": 30,
# }

data = {
    "messages": [
        {"role": "user", "content": "The youtube video of Xiao Yixian in Fights Break Sphere?"},
    ],
    "model": "gpt-4o-mini",
    "tools": ["search_internet", "search_youtube"],
    "stream": True,
    "temperature": 0.01,
    "graph": "base_graph",
}

response = requests.post(f"{base_url}/chat/completions", json=data, stream=True)
for line in response.iter_content(None, decode_unicode=True):
    print(line)
