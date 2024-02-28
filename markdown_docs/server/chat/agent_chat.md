## FunctionDef agent_chat(query, history, stream, model_name, temperature, max_tokens, prompt_name)
**agent_chat**: 该函数用于处理与代理的异步聊天对话。

**参数**:
- `query`: 用户输入的查询字符串，必填参数。
- `history`: 历史对话列表，每个元素为一个`History`对象。
- `stream`: 是否以流式输出的方式返回数据，默认为`False`。
- `model_name`: 使用的LLM模型名称，默认为`LLM_MODELS`列表中的第一个模型。
- `temperature`: LLM采样温度，用于调整生成文本的随机性，默认值由`TEMPERATURE`常量决定，取值范围为0.0到1.0。
- `max_tokens`: 限制LLM生成Token的数量，默认为`None`，代表使用模型的最大值。
- `prompt_name`: 使用的prompt模板名称，默认为"default"。

**代码描述**:
`agent_chat`函数是一个异步函数，主要负责处理用户与代理的聊天对话。它首先将传入的历史对话列表`history`转换为`History`对象列表。然后，定义了一个异步迭代器`agent_chat_iterator`，用于生成聊天回复。在`agent_chat_iterator`中，根据传入的参数和配置，初始化相应的LLM模型和工具，处理历史对话记录，并根据用户的查询生成回复。

如果设置了`stream`参数为`True`，则函数以流式输出的方式返回数据，适用于需要实时更新聊天内容的场景。在流式输出模式下，函数会根据不同的状态（如工具调用开始、完成、错误等）生成不同的JSON格式数据块，并通过`yield`语句异步返回给调用者。

在非流式输出模式下，函数会收集所有生成的聊天回复，并在最终将它们整合为一个JSON格式的响应体返回。

**注意**:
- 在使用`agent_chat`函数时，需要确保传入的`history`参数格式正确，即每个元素都应为`History`对象或能够转换为`History`对象的数据结构。
- `stream`参数的设置会影响函数的返回方式，根据实际应用场景选择合适的模式。
- 函数依赖于配置好的LLM模型和prompt模板，确保在调用前已正确配置这些依赖项。

**输出示例**:
在非流式输出模式下，假设用户的查询得到了一系列的聊天回复，函数可能返回如下格式的JSON数据：
```json
{
  "answer": "这是聊天过程中生成的回复文本。",
  "final_answer": "这是最终的回复文本。"
}
```
在流式输出模式下，函数会逐块返回数据，每块数据可能如下所示：
```json
{
  "tools": [
    "工具名称: 天气查询",
    "工具状态: 调用成功",
    "工具输入: 北京今天天气",
    "工具输出: 北京今天多云，10-14摄氏度"
  ]
}
```
或者在得到最终回复时：
```json
{
  "final_answer": "这是最终的回复文本。"
}
```
### FunctionDef agent_chat_iterator(query, history, model_name, prompt_name)
**agent_chat_iterator**: 此函数的功能是异步迭代生成代理聊天的响应。

**参数**:
- `query`: 字符串类型，用户的查询或输入。
- `history`: 可选的`List[History]`类型，表示对话历史记录。
- `model_name`: 字符串类型，默认为`LLM_MODELS`列表中的第一个模型，用于指定使用的语言模型。
- `prompt_name`: 字符串类型，用于指定提示模板的名称。

**代码描述**:
`agent_chat_iterator`函数是一个异步生成器，用于处理代理聊天的逻辑。首先，函数检查`max_tokens`是否为整数且小于等于0，如果是，则将其设置为`None`。接着，使用`get_ChatOpenAI`函数初始化一个聊天模型实例，并通过`get_kb_details`函数获取知识库列表，将其存储在模型容器的数据库中。如果存在`Agent_MODEL`，则使用该模型初始化另一个聊天模型实例，并将其存储在模型容器中；否则，使用之前初始化的模型。

函数通过`get_prompt_template`函数获取指定的提示模板，并使用`CustomPromptTemplate`类创建一个自定义提示模板实例。然后，使用`CustomOutputParser`类创建一个输出解析器实例，并根据模型名称决定使用`initialize_glm3_agent`函数初始化GLM3代理执行器，或者使用`LLMSingleActionAgent`和`AgentExecutor`创建一个代理执行器。

在异步循环中，函数尝试创建一个任务，使用`wrap_done`函数包装代理执行器的调用，并在完成时通过回调通知。如果设置了`stream`参数，则函数会异步迭代回调处理器的输出，并根据状态生成不同的响应数据，最终以JSON格式产生输出。如果未设置`stream`参数，则会收集所有输出数据，并在最后生成一个包含答案和最终答案的JSON对象。

**注意**:
- 在使用此函数时，需要确保提供的`history`参数格式正确，且每个历史记录项都应为`History`类的实例。
- `model_name`和`prompt_name`参数应根据实际需要选择合适的模型和提示模板。
- 函数内部使用了多个异步操作和自定义类，如`CustomAsyncIteratorCallbackHandler`、`CustomPromptTemplate`和`CustomOutputParser`，需要确保这些组件的正确实现和配置。
- 此函数设计为与前端实现实时或异步的聊天交互，因此在集成到聊天系统时，应考虑其异步特性和对外部回调的处理方式。
***
