## 常用 API 接口调用方式

### 说明

所有接口可以到 `{api_address}/docs` 中查看参数和测试。

### /tools

该接口列出所有工具及其参数信息。  
输入参数：无  
输出示例：
```
{
  "code": 200,
  "msg": "success",
  "data": {
    "search_local_knowledgebase": {
      "name": "search_local_knowledgebase",
      "title": "本地知识库",
      "description": "Use local knowledgebase from one or more of these: test: 关于test的知识库 samples: 关于本项目issue的解答 to get information，Only local data on this knowledge use this tool. The 'database' should be one of the above [test samples].",
      "args": {
        "database": {
          "title": "Database",
          "description": "Database for Knowledge Search",
          "choices": [
            "test",
            "samples"
          ],
          "type": "string"
        },
        "query": {
          "title": "Query",
          "description": "Query for Knowledge Search",
          "type": "string"
        }
      },
      "config": {
        "use": false,
        "top_k": 3,
        "score_threshold": 1,
        "conclude_prompt": {
          "with_result": "<指令>根据已知信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 \"根据已知信息无法回答该问题\"，不允许在答案中添加编造成分，答案请使用中文。 </指令>\n<已知信息>{{ context }}</已知信息>\n<问题>{{ question }}</问题>\n",
          "without_result": "请你根据我的提问回答我的问题:\n{{ question }}\n请注意，你必须在回答结束后强调，你的回答是根据你的经验回答而不是参考资料回答的。\n"
        }
      }
    },
    ...
  }
}
```

### /chat/chat/completions

最主要的对话接口，兼容 openai sdk 格式。它支持以下3种对话模式：  
- 纯 LLM 对话。传入 `model`, `messages` 参数即可，可选参数： `temperature`, `max_tokens`, `stream` 等。
- Agent 对话。在 LLM 对话的基础上，传入 `tools` 参数，可以让 LLM 选择合适的工具和参数，作为对话的参考。
- 半 Agent 对话。在 LLM 对话的基础上，传入 `tool_choice` 参数，可以让 LLM 解析参数，直接调用指定的工具，作为对话的参考。如果使用的 LLM 解析参数的效果不理想，也可以手动指定工具参数。

输入参数：与 openai sdk 参数一致。针对 chatchat 做了以下优化：  
- `tools` 参数可以使用 chatchat 中编写的工具名称，所有支持的工具可以通过 `/tools` 接口获取。
- 在指定 `tool_choice` 的情况下，可以在 `extra_body` 中传入 `tool_input={...}` 来手动指定工具参数。
- 使用 Agent 功能时，`stream` 参数必须指定为 `True`。因为 Agent 是分步执行的，必须通过 SSE 把每个步骤逐一输出。注意：此时 SSE 的单元是执行步骤，LLM 的输出是非流式的。

调用示例：
- 纯 LLM 对话：
    ```python3
    base_url = "http://127.0.0.1:7861/chat"
    data = {
        "model": "qwen1.5-chat",
        "messages": [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好，我是人工智能大模型"},
            {"role": "user", "content": "请用100字左右的文字介绍自己"},
        ],
        "stream": True,
        "temperature": 0.7,
    }

    # 方式一：使用 requests
    import requests
    response = requests.post(f"{base_url}/chat/completions", json=data, stream=True)
    for line in response.iter_content(None, decode_unicode=True):
        print(line, end="", flush=True)

    # 方式二：使用 openai sdk
    import openai
    client = openai.Client(base_url=base_url, api_key="EMPTY")
    resp = client.chat.completions.create(**data)
    for r in resp:
        print(r)
    ```

    ```shell
    # 方式一输出，SSE 格式
    data: {"id":"chat6aa251c3-3425-11ef-be81-603a7c6af450","choices":[{"delta":{"content":"","function_call":null,"role":"assistant","tool_calls":null},"finish_reason":null,"index":0,"logprobs":null}],"created":1719452077,"model":"qwen1.5-chat","object":"chat.completion.chunk","system_fingerprint":null,"usage":null,"message_id":null,"status":null}
    data: {"id":"chat6aa251c3-3425-11ef-be81-603a7c6af450","choices":[{"delta":{"content":"我是","function_call":null,"role":null,"tool_calls":null},"finish_reason":null,"index":0,"logprobs":null}],"created":1719452077,"model":"qwen1.5-chat","object":"chat.completion.chunk","system_fingerprint":null,"usage":null,"message_id":null,"status":null}
    data: {"id":"chat6abf605c-3425-11ef-9f15-603a7c6af450","choices":[{"delta":{"content":"阿里云","function_call":null,"role":null,"tool_calls":null},"finish_reason":null,"index":0,"logprobs":null}],"created":1719452078,"model":"qwen1.5-chat","object":"chat.completion.chunk","system_fingerprint":null,"usage":null,"message_id":null,"status":null}
    data: {"id":"chat6ad00242-3425-11ef-af45-603a7c6af450","choices":[{"delta":{"content":"自主研发的","function_call":null,"role":null,"tool_calls":null},"finish_reason":null,"index":0,"logprobs":null}],"created":1719452078,"model":"qwen1.5-chat","object":"chat.completion.chunk","system_fingerprint":null,"usage":null,"message_id":null,"status":null}
    ...
    ```
    ```shell
    # 方式二输出：
    ChatCompletionChunk(id='chat682070c8-3426-11ef-947d-603a7c6af450', choices=[Choice(delta=ChoiceDelta(content='', function_call=None, role='assistant', tool_calls=None), finish_reason=None, index=0, logprobs=None)], created=1719452503, model='qwen1.5-chat', object='chat.completion.chunk', system_fingerprint=None, usage=None, message_id=None, status=None)
    ChatCompletionChunk(id='chat682070c8-3426-11ef-947d-603a7c6af450', choices=[Choice(delta=ChoiceDelta(content='我是', function_call=None, role=None, tool_calls=None), finish_reason=None, index=0, logprobs=None)], created=1719452503, model='qwen1.5-chat', object='chat.completion.chunk', system_fingerprint=None, usage=None, message_id=None, status=None)
    ChatCompletionChunk(id='chat683fdd72-3426-11ef-be33-603a7c6af450', choices=[Choice(delta=ChoiceDelta(content='由阿里', function_call=None, role=None, tool_calls=None), finish_reason=None, index=0, logprobs=None)], created=1719452503, model='qwen1.5-chat', object='chat.completion.chunk', system_fingerprint=None, usage=None, message_id=None, status=None)
    ChatCompletionChunk(id='chat68511ba1-3426-11ef-b2be-603a7c6af450', choices=[Choice(delta=ChoiceDelta(content='云开发', function_call=None, role=None, tool_calls=None), finish_reason=None, index=0, logprobs=None)], created=1719452503, model='qwen1.5-chat', object='chat.completion.chunk', system_fingerprint=None, usage=None, message_id=None, status=None)
    ...
    ```
- Agent 对话  
    以下示例仅展示使用 `requests` 的情况，可以自行尝试使用 `openai sdk` 进行请求，参数和输出内容是一样的。
    ```python3
    base_url = "http://127.0.0.1:7861/chat"
    tools = list(requests.get(f"http://127.0.0.1:7861/tools").json()["data"])
    data = {
        "model": "qwen1.5-chat",
        "messages": [
            {"role": "user", "content": "37+48=？"},
        ],
        "stream": True,
        "temperature": 0.7,
        "tools": tools,
    }

    import requests
    response = requests.post(f"{base_url}/chat/completions", json=data, stream=True)
    for line in response.iter_content(None, decode_unicode=True):
        print(line)
    ```
    ```shell
    # 输出：
    data: {"id": "chat39830df6-d016-4b91-b502-e113bb71542c", "object": "chat.completion.chunk", "model": "qwen1.5-chat", "created": 1719453364, "status": 1, "message_type": 1, "message_id": null, "is_ref": false, "choices": [{"delta": {"content": "", "tool_calls": []}, "role": "assistant"}]}
    data: {"id": "chatb05f9cb2-1e93-4657-806b-29ec135483b9", "object": "chat.completion.chunk", "model": "qwen1.5-chat", "created": 1719453367, "status": 3, "message_type": 1, "message_id": null, "is_ref": false, "choices": [{"delta": {"content": "Thought: The problem involves adding two numbers: 37 and 48. To perform this calculation, I will use the calculator API.\nAction: calculate\nAction Input: {\"text\": \"37 + 48\"}", "tool_calls": []}, "role": "assistant"}]}
    data: {"id": "chat73adade0-b62f-412a-a448-9002a59cbc30", "object": "chat.completion.chunk", "model": "qwen1.5-chat", "created": 1719453367, "status": 4, "message_type": 1, "message_id": null, "is_ref": false, "choices": [{"delta": {"content": "Thought: The problem involves adding two numbers: 37 and 48. To perform this calculation, I will use the calculator API.\nAction: calculate\nAction Input: {\"text\": \"37 + 48\"}", "tool_calls": []}, "role": "assistant"}]}
    data: {"id": "chat7752232b-7360-4010-bc55-e50fa8ac9f44", "object": "chat.completion.chunk", "model": "qwen1.5-chat", "created": 1719453367, "status": 6, "message_type": 1, "message_id": null, "is_ref": false, "choices": [{"delta": {"content": "", "tool_calls": [{"index": 0, "id": "f2b20744-3958-4e3b-9e51-c5738d87a020", "type": "function", "function": {"name": "calculate", "arguments": "{'text': '37 + 48'}"}, "tool_output": null, "is_error": false}]}, "role": "assistant"}]}
    data: {"id": "chatef5f948e-4772-477d-823d-ce74b38ba586", "object": "chat.completion.chunk", "model": "qwen1.5-chat", "created": 1719453367, "status": 7, "message_type": 1, "message_id": null, "is_ref": false, "choices": [{"delta": {"content": "", "tool_calls": [{"index": 0, "id": "f2b20744-3958-4e3b-9e51-c5738d87a020", "type": "function", "function": {"name": "calculate", "arguments": "{'text': '37 + 48'}"}, "tool_output": "85", "is_error": false}]}, "role": "assistant"}]}
    data: {"id": "chatdee106c6-42e6-41cf-b2df-692431829e4d", "object": "chat.completion.chunk", "model": "qwen1.5-chat", "created": 1719453367, "status": 1, "message_type": 1, "message_id": null, "is_ref": false, "choices": [{"delta": {"content": "", "tool_calls": []}, "role": "assistant"}]}
    data: {"id": "chat819ef11b-576f-4489-b6bb-47565eb69ee8", "object": "chat.completion.chunk", "model": "qwen1.5-chat", "created": 1719453370, "status": 3, "message_type": 1, "message_id": null, "is_ref": false, "choices": [{"delta": {"content": " The calculation 37 + 48 has been successfully performed using the calculate API, resulting in the result of 85. Therefore, the final answer to the given question is 85. \n\nJSON Object:\n{\n  \"answer\": 85\n}", "tool_calls": []}, "role": "assistant"}]}
    data: {"id": "chatb6b1071b-5346-4713-922c-b2887728491f", "object": "chat.completion.chunk", "model": "qwen1.5-chat", "created": 1719453370, "status": 5, "message_type": 1, "message_id": null, "is_ref": false, "choices": [{"delta": {"content": " The calculation 37 + 48 has been successfully performed using the calculate API, resulting in the result of 85. Therefore, the final answer to the given question is 85. \n\nJSON Object:\n{\n  \"answer\": 85\n}", "tool_calls": []}, "role": "assistant"}]}
    ```
    输出中包含一个 `status` 字段，代表 Agent 当前执行阶段。在 `status` 为 6 和 7 的输出中，可以看到 tool_call 的相关信息。具体值为：
    ```python3
    class AgentStatus:
        llm_start: int = 1
        llm_new_token: int = 2
        llm_end: int = 3
        agent_action: int = 4
        agent_finish: int = 5
        tool_start: int = 6
        tool_end: int = 7
        error: int = 8
    ```

    输出中包含一个 `message_type` 字段，代表输出内容的类型，主要用于前端渲染不同的消息，当前除了`text2image` 工具是 `IMAGE`，其它都是 `TEXT`。具体值为：
    ```python3
    class MsgType:
        TEXT = 1
        IMAGE = 2
        AUDIO = 3
        VIDEO = 4
    ```
- 知识库对话（LLM 自动解析参数）
    直接指定 `tool_choice` 为 `"search_local_knowledgebase"`工具即可使用知识库对话功能。其它工具对话类似。
    ```python3
    base_url = "http://127.0.0.1:7861/chat"
    data = {
        "messages": [
            {"role": "user", "content": "如何提问以获得高质量答案"},
        ],
        "model": "qwen1.5-chat",
        "tool_choice": "search_local_knowledgebase",
        "stream": True,
    }

    import requests
    response = requests.post(f"{base_url}/chat/completions", json=data, stream=True)
    for line in response.iter_content(None, decode_unicode=True):
        print(line)
    ```
    在 `status` 为 6 和 7 的返回值中，可以获取工具的调用和输出信息。  
    由于输出信息太多，这里不做展示，请自行测试。
- 知识库对话（手动传入参数）
    直接指定 `tool_choice` 为 `"search_local_knowledgebase"`，在 `extra_body` 中通过 `tool_input` 设定工具参数，即可手动调用工具，实现指定知识库对话。
    ```python3
    base_url = "http://127.0.0.1:7861/chat"
    data = {
        "messages": [
            {"role": "user", "content": "如何提问以获得高质量答案"},
        ],
        "model": "qwen1.5-chat",
        "tool_choice": "search_local_knowledgebase",
        "extra_body": {"tool_input": {"database": "samples", "query": "如何提问以获得高质量答案"}},
        "stream": True,
    }

    import requests
    response = requests.post(f"{base_url}/chat/completions", json=data, stream=True)
    for line in response.iter_content(None, decode_unicode=True):
        print(line)
    ```
    在输出中可以看出 `status` 为 6 和 7 的工具解析过程已经不存在了，说明工具调用不是通过 LLM 完成的。  
    由于输出信息太多，这里不做展示，请自行测试。
