import requests
import json

if __name__ == "__main__":
    url = 'http://localhost:7861/chat/chat'
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

    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    if response.status_code == 200:
        for line in response.iter_content(decode_unicode=True):
            print(line, flush=True)
    else:
        print("Error:", response.status_code)


    r = requests.post(
        openai_url + "/chat/completions",
        json={"model": LLM_MODEL, "messages": "你好", "max_tokens": 1000})
    data = r.json()
    print(f"/chat/completions\n")
    print(data)
    assert "choices" in data

