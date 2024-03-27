## FunctionDef knowledge_base_chat(query, knowledge_base_name, top_k, score_threshold, history, stream, model_name, temperature, max_tokens, prompt_name, request)
**knowledge_base_chat**: 该函数用于处理用户与知识库的交互对话。

**参数**:
- `query`: 用户的输入查询，类型为字符串。
- `knowledge_base_name`: 知识库的名称，类型为字符串。
- `top_k`: 匹配向量数，类型为整数。
- `score_threshold`: 知识库匹配相关度阈值，取值范围在0-1之间，类型为浮点数。
- `history`: 历史对话列表，每个元素为一个`History`对象。
- `stream`: 是否以流式输出，类型为布尔值。
- `model_name`: LLM模型名称，类型为字符串。
- `temperature`: LLM采样温度，类型为浮点数。
- `max_tokens`: 限制LLM生成Token数量，类型为整数或None。
- `prompt_name`: 使用的prompt模板名称，类型为字符串。
- `request`: 当前的请求对象，类型为`Request`。

**代码描述**:
函数首先通过`KBServiceFactory.get_service_by_name`方法获取指定名称的知识库服务实例。如果未找到对应的知识库，将返回404状态码的响应。然后，将传入的历史对话数据转换为`History`对象列表。接下来，定义了一个异步生成器`knowledge_base_chat_iterator`，用于处理知识库查询和LLM模型生成回答的逻辑。在这个生成器中，首先根据条件调整`max_tokens`的值，然后创建LLM模型实例，并执行文档搜索。如果启用了重排序（reranker），则对搜索结果进行重排序处理。根据搜索结果构建上下文，并生成LLM模型的输入提示。最后，使用LLM模型生成回答，并根据`stream`参数决定是以流式输出还是一次性输出所有结果。

**注意**:
- 在调用此函数时，需要确保传入的知识库名称在系统中已经存在，否则会返回404错误。
- `history`参数允许传入空列表，表示没有历史对话。
- `stream`参数控制输出模式，当设置为True时，将以流式输出回答和文档信息；否则，将一次性返回所有内容。
- 函数内部使用了多个异步操作，因此在调用时需要使用`await`关键字。

**输出示例**:
调用`knowledge_base_chat`函数可能返回的JSON格式示例：
```json
{
  "answer": "这是根据您的查询生成的回答。",
  "docs": [
    "出处 [1] [文档名称](文档链接) \n\n文档内容\n\n",
    "<span style='color:red'>未找到相关文档,该回答为大模型自身能力解答！</span>"
  ]
}
```
如果启用了流式输出，每个生成的回答片段和文档信息将作为独立的JSON对象逐个发送。
### FunctionDef knowledge_base_chat_iterator(query, top_k, history, model_name, prompt_name)
**knowledge_base_chat_iterator**: 此函数的功能是异步迭代生成基于知识库的聊天回答。

**参数**:
- `query`: 字符串类型，用户的查询内容。
- `top_k`: 整型，指定返回的最相关文档数量。
- `history`: 可选的历史记录列表，每个历史记录是一个`History`对象。
- `model_name`: 字符串类型，默认为`model_name`，指定使用的模型名称。
- `prompt_name`: 字符串类型，默认为`prompt_name`，指定使用的提示模板名称。

**代码描述**:
`knowledge_base_chat_iterator`函数是一个异步生成器，用于处理用户的查询请求，并基于知识库内容异步生成聊天回答。首先，函数检查`max_tokens`的有效性，并根据需要调整其值。接着，使用`get_ChatOpenAI`函数初始化一个聊天模型实例，该模型配置了模型名称、温度、最大token数和回调函数。

函数通过`run_in_threadpool`异步运行`search_docs`函数，根据用户的查询内容在知识库中搜索相关文档。如果启用了重排序功能（`USE_RERANKER`），则使用`LangchainReranker`类对搜索结果进行重排序，以提高结果的相关性。

根据搜索到的文档数量，函数选择相应的提示模板。如果没有找到相关文档，使用“empty”模板；否则，使用指定的`prompt_name`模板。然后，将历史记录和用户的查询请求转换为聊天提示模板。

使用`LLMChain`类创建一个聊天链，并通过`wrap_done`函数包装异步任务，以便在任务完成时进行回调处理。函数还生成了源文档的信息，包括文档的出处和内容。

最后，根据是否启用流式传输（`stream`），函数以不同方式异步生成聊天回答。如果启用流式传输，使用服务器发送事件（server-sent-events）逐个发送回答的token；否则，将所有token拼接后一次性返回。

**注意**:
- 在使用此函数时，需要确保提供的`model_name`和`prompt_name`在系统中已配置且有效。
- 当启用重排序功能时，需要确保`LangchainReranker`类的配置正确，包括模型路径和设备类型。
- 函数的异步特性要求调用者使用`async`和`await`关键字进行调用，以确保异步操作的正确执行。
- 在处理大量查询请求时，合理配置`top_k`和重排序参数可以有效提高处理效率和回答质量。
***
