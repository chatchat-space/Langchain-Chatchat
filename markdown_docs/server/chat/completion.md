## FunctionDef completion(query, stream, echo, model_name, temperature, max_tokens, prompt_name)
**completion**: 此函数用于处理用户输入，生成并返回由LLM模型补全的文本。

**参数**:
- `query`: 用户输入的文本。
- `stream`: 是否以流式输出结果。
- `echo`: 是否在输出结果中回显输入文本。
- `model_name`: 使用的LLM模型名称。
- `temperature`: LLM模型采样温度，用于控制生成文本的随机性。
- `max_tokens`: 限制LLM模型生成的Token数量。
- `prompt_name`: 使用的prompt模板名称。

**代码描述**:
此函数首先定义了一个异步生成器`completion_iterator`，该生成器负责实际的文本生成逻辑。它使用`get_OpenAI`函数初始化一个LLM模型，并根据提供的参数配置模型。然后，它使用`get_prompt_template`函数获取指定的prompt模板，并将用户输入的`query`传递给LLM模型进行处理。根据`stream`参数的值，此函数可以以流式方式逐个返回生成的Token，或者等待所有Token生成完成后一次性返回结果。最后，使用`EventSourceResponse`包装`completion_iterator`生成器，以适合流式输出的HTTP响应格式返回结果。

在项目中，`completion`函数通过`/other/completion`路由在`server/api.py`文件中被注册为一个POST请求的处理器。这表明它设计用于处理来自客户端的文本补全请求，客户端可以通过发送POST请求到此路由，并在请求体中提供相应的参数，来获取LLM模型基于用户输入生成的补全文本。

**注意**:
- 确保`model_name`参数对应的LLM模型已正确配置且可用。
- `temperature`参数应在0.0到1.0之间，以控制生成文本的随机性。
- 如果`max_tokens`设为负数或0，将不会限制Token数量。

**输出示例**:
如果`stream`参数为`False`，并且用户输入为"今天天气如何"，一个可能的返回值示例为：
```
"今天天气晴朗，适合外出。"
```
如果`stream`参数为`True`，则可能逐个返回上述文本中的每个字或词。
### FunctionDef completion_iterator(query, model_name, prompt_name, echo)
**completion_iterator**: 此函数的功能是异步迭代生成基于给定查询的完成文本。

**参数**:
- `query`: 字符串类型，用户的查询输入。
- `model_name`: 字符串类型，默认为LLM_MODELS列表中的第一个模型，指定使用的语言模型名称。
- `prompt_name`: 字符串类型，指定使用的提示模板名称。
- `echo`: 布尔类型，指示是否回显输入。

**代码描述**:
`completion_iterator`函数是一个异步生成器，用于根据用户的查询输入生成文本。首先，函数检查`max_tokens`参数是否为整数且小于等于0，如果是，则将其设置为None。接着，通过`get_OpenAI`函数初始化一个配置好的OpenAI模型实例，其中包括模型名称、温度、最大令牌数、回调函数列表以及是否回显输入等参数。然后，使用`get_prompt_template`函数加载指定类型和名称的提示模板，并通过`PromptTemplate.from_template`方法创建一个`PromptTemplate`实例。之后，创建一个`LLMChain`实例，将提示模板和语言模型作为参数传入。

函数接下来创建一个异步任务，使用`asyncio.create_task`方法将`chain.acall`方法的调用包装起来，并通过`wrap_done`函数与一个回调函数关联，以便在任务完成时进行通知。根据`stream`变量的值，函数将以不同的方式生成文本。如果`stream`为真，则通过`callback.aiter()`异步迭代每个生成的令牌，并使用服务器发送事件（server-sent-events）来流式传输响应。如果`stream`为假，则将所有生成的令牌累加到一个字符串中，然后一次性生成整个答案。

最后，函数等待之前创建的异步任务完成，确保所有生成的文本都已处理完毕。

**注意**:
- 使用此函数时，需要确保`query`参数正确无误，因为它直接影响生成文本的内容。
- `model_name`和`prompt_name`参数应根据需要选择合适的模型和提示模板，以获得最佳的文本生成效果。
- 在使用流式传输功能时，应考虑客户端如何处理流式数据，以确保用户体验。
- 此函数依赖于`get_OpenAI`和`get_prompt_template`等函数，因此在使用前应确保相关配置和模板已正确设置。
***
