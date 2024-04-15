## FunctionDef bing_search(text, result_len)
**bing_search**: 此函数用于通过Bing搜索引擎进行文本搜索并返回搜索结果。

**参数**:
- `text`: 需要搜索的文本内容。
- `result_len`: 返回的搜索结果数量，默认为`SEARCH_ENGINE_TOP_K`。
- `**kwargs`: 接受额外的关键字参数，用于扩展或自定义搜索行为。

**代码描述**:
`bing_search`函数首先检查环境变量中是否设置了`BING_SEARCH_URL`和`BING_SUBSCRIPTION_KEY`。如果这两个环境变量未设置，函数将返回一个包含错误信息的字典，提示用户需要设置这些环境变量。错误信息包括一个提示信息、一个标题以及一个链接，该链接指向相关的帮助文档。

如果环境变量设置正确，函数将创建一个`BingSearchAPIWrapper`实例，使用提供的`BING_SUBSCRIPTION_KEY`和`BING_SEARCH_URL`。然后，使用此实例调用`results`方法，传入需要搜索的文本(`text`)和结果数量(`result_len`)。最后，返回搜索结果。

**注意**:
- 确保在使用此函数之前已正确设置环境变量`BING_SEARCH_URL`和`BING_SUBSCRIPTION_KEY`，否则将无法执行搜索操作。
- `result_len`参数允许调用者自定义返回的搜索结果数量，但实际返回结果也受Bing搜索API的限制。
- 通过`**kwargs`参数，可以传递额外的搜索选项给Bing搜索API，但需要确保这些选项是API支持的。

**输出示例**:
```python
[
    {
        "snippet": "这是搜索结果的摘要",
        "title": "搜索结果标题",
        "link": "https://example.com/search-result"
    },
    {
        "snippet": "这是另一个搜索结果的摘要",
        "title": "另一个搜索结果标题",
        "link": "https://example.com/another-search-result"
    }
]
```
此示例展示了函数可能返回的搜索结果列表，每个结果包含`snippet`（摘要）、`title`（标题）和`link`（链接）。
## FunctionDef duckduckgo_search(text, result_len)
**duckduckgo_search**: 此函数用于通过DuckDuckGo搜索引擎执行文本搜索并返回结果。

**参数**:
- `text`: 需要搜索的文本。
- `result_len`: 返回结果的数量，默认值为`SEARCH_ENGINE_TOP_K`，这是一个预设的常量，用于指定默认的返回结果数量。
- `**kwargs`: 接受额外的关键字参数，这些参数可以用于扩展或自定义搜索行为。

**代码描述**:
`duckduckgo_search`函数首先创建了一个`DuckDuckGoSearchAPIWrapper`的实例，这是一个封装了DuckDuckGo搜索API调用的类。通过这个实例，函数使用`results`方法执行搜索。`text`参数是用户希望搜索的文本内容，而`result_len`参数指定了希望返回的搜索结果数量。如果调用时没有指定`result_len`，则会使用`SEARCH_ENGINE_TOP_K`作为默认值。此外，函数还接受任何额外的关键字参数（`**kwargs`），这提供了额外的灵活性，允许调用者根据需要传递更多的参数给搜索API。

**注意**:
- 确保在使用此函数之前已正确设置和配置了`DuckDuckGoSearchAPIWrapper`类，包括任何必要的认证信息或API密钥。
- `SEARCH_ENGINE_TOP_K`是一个预定义常量，需要在使用此函数之前定义。它决定了在未明确指定结果数量时返回的默认结果数量。
- 由于`**kwargs`提供了额外的参数传递功能，使用时应注意只包含DuckDuckGo搜索API支持的参数，以避免发生错误。

**输出示例**:
```python
[
    {"title": "DuckDuckGo", "snippet": "DuckDuckGo是一个注重隐私的搜索引擎。", "url": "https://duckduckgo.com"},
    {"title": "DuckDuckGo隐私政策", "snippet": "了解DuckDuckGo如何保护您的隐私。", "url": "https://duckduckgo.com/privacy"}
]
```
此输出示例展示了一个可能的返回值，其中包含了搜索结果的列表。每个结果是一个字典，包含标题(`title`)、摘要(`snippet`)和URL(`url`)。实际返回的结果将根据搜索的文本和结果数量的指定而有所不同。
## FunctionDef metaphor_search(text, result_len, split_result, chunk_size, chunk_overlap)
**metaphor_search**: 此函数的功能是基于给定文本进行隐喻搜索，并返回搜索结果的列表。

**参数**:
- `text`: 需要搜索的文本，类型为字符串。
- `result_len`: 返回结果的最大数量，默认为`SEARCH_ENGINE_TOP_K`。
- `split_result`: 是否将搜索结果分割成更小的文本块，默认为`False`。
- `chunk_size`: 分割文本块的大小，默认为500个字符。
- `chunk_overlap`: 分割文本块时的重叠字符数，默认为`OVERLAP_SIZE`。

**代码描述**:
此函数首先检查是否提供了`METAPHOR_API_KEY`，如果没有提供，则直接返回空列表。如果提供了，函数将使用此API密钥创建一个`Metaphor`客户端，并使用该客户端对给定的文本进行搜索。搜索结果的数量由`result_len`参数控制，且默认启用自动提示功能。

搜索结果中的每个条目都会通过`markdownify`函数转换其摘要部分，以便更好地展示。

如果`split_result`参数为`True`，函数将对每个搜索结果的内容进行分割，以生成更小的文本块。这些文本块通过`RecursiveCharacterTextSplitter`根据给定的分割符和`chunk_size`、`chunk_overlap`参数进行分割。然后，基于与原始搜索文本的相似度，选择相似度最高的`result_len`个文本块作为最终结果。

如果`split_result`为`False`，则直接返回搜索结果的摘要、链接和标题。

**注意**:
- 确保在使用此函数之前已正确设置`METAPHOR_API_KEY`。
- `SEARCH_ENGINE_TOP_K`和`OVERLAP_SIZE`需要根据实际情况预先定义。
- 分割结果的功能适用于需要对长文本进行进一步分析的场景。

**输出示例**:
```python
[
    {
        "snippet": "这是搜索结果的一个示例文本片段。",
        "link": "https://example.com/link-to-source",
        "title": "示例文本标题"
    },
    # 更多搜索结果...
]
```
此输出示例展示了当`split_result`为`False`时，函数可能返回的搜索结果的格式。每个结果包含了文本片段（`snippet`）、源链接（`link`）和标题（`title`）。
## FunctionDef search_result2docs(search_results)
**search_result2docs**: 此函数的功能是将搜索结果转换为文档列表。

**参数**:
- search_results: 搜索结果的列表，每个结果是一个包含至少一个“snippet”、“link”和“title”键的字典。

**代码描述**:
`search_result2docs`函数接收一个搜索结果列表作为输入，遍历这个列表，并为每个结果创建一个`Document`对象。这个`Document`对象包含页面内容（由结果中的“snippet”键提供，如果不存在则为空字符串）、来源链接（由“link”键提供，如果不存在则为空字符串）和文件名（由“title”键提供，如果不存在则为空字符串）。这些信息被存储在`Document`对象的`page_content`和`metadata`属性中。最后，所有创建的`Document`对象被收集到一个列表中并返回。

在项目中，`search_result2docs`函数被`lookup_search_engine`函数调用，用于处理从特定搜索引擎返回的搜索结果。`lookup_search_engine`函数首先根据给定的查询参数和搜索引擎名称，通过搜索引擎获取搜索结果，然后调用`search_result2docs`函数将这些搜索结果转换为`Document`对象的列表，以便进一步处理或展示。

**注意**:
- 确保传入的搜索结果列表格式正确，每个结果字典至少包含“snippet”、“link”和“title”三个键。
- 函数的输出依赖于输入的搜索结果的质量和完整性。

**输出示例**:
假设`search_results`参数是以下列表：
```python
[
    {"snippet": "这是搜索结果的摘要", "link": "https://example.com", "title": "示例标题"},
    {"snippet": "第二个搜索结果的摘要", "link": "https://example2.com", "title": "第二个示例标题"}
]
```
那么函数的返回值可能是一个包含两个`Document`对象的列表，每个对象的`page_content`分别是"这是搜索结果的摘要"和"第二个搜索结果的摘要"，`metadata`包含相应的"source"和"filename"信息。
## FunctionDef lookup_search_engine(query, search_engine_name, top_k, split_result)
**lookup_search_engine**: 此函数的功能是异步查询指定搜索引擎并返回搜索结果转换后的文档列表。

**参数**:
- `query`: 字符串类型，表示要在搜索引擎中查询的关键词。
- `search_engine_name`: 字符串类型，指定要查询的搜索引擎的名称。
- `top_k`: 整型，默认值为`SEARCH_ENGINE_TOP_K`，表示返回的搜索结果的最大数量。
- `split_result`: 布尔类型，默认为`False`，指示是否拆分搜索结果。

**代码描述**:
`lookup_search_engine`函数首先通过`search_engine_name`参数从`SEARCH_ENGINES`字典中获取对应的搜索引擎函数。然后，它使用`run_in_threadpool`函数异步运行该搜索引擎函数，传入`query`、`result_len=top_k`和`split_result=split_result`作为参数，以获取搜索结果。获取到的搜索结果随后被传递给`search_result2docs`函数，该函数将搜索结果转换为文档(`Document`)对象的列表。最终，这个文档列表被返回。

在项目中，`lookup_search_engine`函数被`search_engine_chat_iterator`函数调用，用于获取搜索引擎的查询结果，并将这些结果转换为文档列表，以便在聊天迭代器中生成基于搜索引擎结果的聊天回复。

**注意**:
- 确保`search_engine_name`参数对应的搜索引擎已经在`SEARCH_ENGINES`字典中定义。
- `top_k`参数控制返回的搜索结果数量，根据需要调整以获取最优的搜索体验。
- `split_result`参数可以控制搜索结果是否需要被拆分，这取决于搜索引擎函数的具体实现和需求。

**输出示例**:
假设搜索查询返回了两个结果，函数的返回值可能是如下格式的文档列表：
```python
[
    Document(page_content="这是搜索结果的摘要", metadata={"source": "https://example.com", "filename": "示例标题"}),
    Document(page_content="第二个搜索结果的摘要", metadata={"source": "https://example2.com", "filename": "第二个示例标题"})
]
```
这个列表中的每个`Document`对象包含了搜索结果的摘要、来源链接和标题，可用于进一步的处理或展示。
## FunctionDef search_engine_chat(query, search_engine_name, top_k, history, stream, model_name, temperature, max_tokens, prompt_name, split_result)
**search_engine_chat**: 该函数用于通过搜索引擎检索信息，并结合历史对话和LLM模型生成回答。

**参数**:
- `query`: 用户输入的查询内容，类型为字符串。
- `search_engine_name`: 指定使用的搜索引擎名称，类型为字符串。
- `top_k`: 检索结果的数量，类型为整数。
- `history`: 历史对话列表，每个元素为一个`History`对象。
- `stream`: 是否以流式输出结果，类型为布尔值。
- `model_name`: 指定使用的LLM模型名称，类型为字符串。
- `temperature`: LLM模型采样温度，用于控制生成文本的多样性，类型为浮点数。
- `max_tokens`: 限制LLM生成Token的数量，类型为整数或None。
- `prompt_name`: 使用的prompt模板名称，类型为字符串。
- `split_result`: 是否对搜索结果进行拆分，主要用于metaphor搜索引擎，类型为布尔值。

**代码描述**:
该函数首先检查指定的搜索引擎是否支持，如果不支持或需要的配置项未设置，将返回错误信息。然后，将历史对话列表中的数据转换为`History`对象列表。接着，定义了一个异步迭代器`search_engine_chat_iterator`，用于执行搜索操作和生成回答。在这个迭代器中，首先根据条件调整`max_tokens`的值，然后创建LLM模型实例，并执行搜索引擎查询。查询结果和历史对话将被用于构建LLM模型的输入提示，以生成回答。根据`stream`参数的值，函数将以不同的方式输出结果：如果为True，则以流式形式输出每个生成的Token和最终的文档列表；如果为False，则将所有生成的Token拼接成完整的回答后一次性输出，同时附上文档列表。最后，返回一个`EventSourceResponse`对象，包含异步迭代器的执行结果。

**注意**:
- 在使用该函数时，需要确保指定的搜索引擎已经在项目中支持，并且相关配置项（如API密钥）已正确设置。
- `history`参数应为`History`对象的列表，每个对象代表一条历史对话记录。
- 该函数支持流式输出，适用于需要实时展示生成结果的场景。
- 函数的执行依赖于外部的LLM模型和搜索引擎服务，因此执行时间可能受到网络状况和服务响应时间的影响。

**输出示例**:
```json
{
  "answer": "根据您的查询，这里是生成的回答。",
  "docs": [
    "出处 [1] [来源链接](http://example.com)\n\n相关文档内容。\n\n",
    "出处 [2] [来源链接](http://example.com)\n\n相关文档内容。\n\n"
  ]
}
```
如果`stream`为True，输出将以多个json字符串的形式逐步发送，每个字符串包含一个Token或文档列表。如果为False，将输出一个包含完整回答和文档列表的json字符串。
### FunctionDef search_engine_chat_iterator(query, search_engine_name, top_k, history, model_name, prompt_name)
**search_engine_chat_iterator**: 此函数的功能是异步迭代搜索引擎查询结果，并生成基于这些结果的聊天回复。

**参数**:
- `query`: 字符串类型，用户的查询请求。
- `search_engine_name`: 字符串类型，指定要查询的搜索引擎名称。
- `top_k`: 整型，指定返回的搜索结果的最大数量。
- `history`: 可选的`List[History]`类型，表示对话历史记录。
- `model_name`: 字符串类型，默认为`LLM_MODELS[0]`，指定使用的语言模型名称。
- `prompt_name`: 字符串类型，指定使用的提示模板名称。

**代码描述**:
`search_engine_chat_iterator`函数首先检查`max_tokens`的值，如果为非正整数，则将其设置为`None`。接着，通过`get_ChatOpenAI`函数初始化一个`ChatOpenAI`实例，该实例用于生成基于语言模型的聊天回复。函数使用`lookup_search_engine`异步查询指定的搜索引擎，获取搜索结果，并将这些结果转换为文本形式的上下文。

接下来，函数通过`get_prompt_template`获取指定的提示模板，并结合对话历史记录，构造出完整的聊天提示。这个提示将作为语言模型的输入，以生成聊天回复。函数创建一个异步任务，使用`wrap_done`函数包装这个任务，以便在任务完成或发生异常时进行通知。

函数还处理了搜索结果的文档来源信息，将其格式化为特定的字符串列表。如果没有找到相关文档，会添加一条特定的消息表示未找到相关文档。

最后，根据`stream`变量的值，函数可能以流式传输的方式逐个生成聊天回复，或者将所有回复合并后一次性返回。在流式传输模式下，每个生成的回复都会被立即发送给客户端，而在非流式模式下，则会等待所有回复生成完成后统一返回。

**注意**:
- 在使用此函数时，需要确保提供的`search_engine_name`对应于已配置的搜索引擎。
- `history`参数允许包含对话的历史记录，这对于生成更加连贯和上下文相关的回复非常重要。
- 函数利用了异步编程模式，因此在调用此函数时应注意使用`await`关键字。
- 在处理大量或复杂的查询时，函数的执行时间可能较长，因此在设计用户界面和交互逻辑时应考虑到潜在的延迟。
***
