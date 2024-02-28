## FunctionDef embed_texts(texts, embed_model, to_query)
**embed_texts**: 该函数的功能是对文本进行向量化处理，并返回向量化结果。

**参数**:
- `texts`: 需要进行向量化处理的文本列表。
- `embed_model`: 使用的嵌入模型名称，默认为配置中指定的嵌入模型。
- `to_query`: 布尔值，指示向量化的文本是否用于查询，默认为False。

**代码描述**:
`embed_texts`函数首先检查指定的嵌入模型是否在本地嵌入模型列表中。如果是，它将使用`load_local_embeddings`函数加载本地嵌入模型，并对文本进行向量化处理，然后返回包含向量化结果的`BaseResponse`对象。如果指定的嵌入模型不在本地模型列表中，函数将检查模型是否在支持嵌入功能的在线模型列表中。对于在线模型，函数将根据模型配置创建相应的工作类实例，并调用其嵌入方法进行文本向量化，同样返回`BaseResponse`对象。如果指定的嵌入模型既不在本地模型列表中也不在在线模型列表中，函数将返回一个错误信息，指出指定的模型不支持嵌入功能。在整个过程中，如果遇到任何异常，函数将捕获异常并返回包含错误信息的`BaseResponse`对象。

**注意**:
- 在使用`embed_texts`函数时，需要确保传入的`texts`参数是有效的文本列表。
- `embed_model`参数应正确指定，以便函数能够找到并使用正确的嵌入模型进行文本向量化处理。
- `to_query`参数应根据实际需求设置，以优化向量化结果的使用场景。
- 函数的执行结果依赖于指定嵌入模型的有效性和可用性，因此在使用前应确认模型配置正确且模型可用。

**输出示例**:
调用`embed_texts(texts=["你好", "世界"], embed_model="example_model", to_query=False)`可能会返回如下`BaseResponse`对象：
```python
BaseResponse(code=200, msg="success", data=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
```
这表示两个文本"你好"和"世界"被成功向量化，向量化结果分别为`[0.1, 0.2, 0.3]`和`[0.4, 0.5, 0.6]`。
## FunctionDef aembed_texts(texts, embed_model, to_query)
**aembed_texts**: 此函数的功能是对文本列表进行异步向量化处理，并返回一个包含向量化结果的BaseResponse对象。

**参数**:
- `texts`: 需要进行向量化处理的文本列表，类型为List[str]。
- `embed_model`: 使用的嵌入模型名称，默认值为配置中指定的嵌入模型，类型为str。
- `to_query`: 布尔值，指示向量化的文本是否用于查询，默认为False。

**代码描述**:
`aembed_texts`函数首先检查`embed_model`是否在本地嵌入模型列表中。如果是，则使用`load_local_embeddings`函数加载本地嵌入模型，并异步调用`aembed_documents`方法进行文本向量化处理，最后返回包含向量化结果的`BaseResponse`对象。如果`embed_model`在支持嵌入功能的在线模型列表中，则通过`run_in_threadpool`函数异步调用`embed_texts`函数进行文本向量化处理，并返回相应的`BaseResponse`对象。如果在向量化过程中出现异常，函数将捕获异常并返回一个包含错误信息的`BaseResponse`对象，状态码设为500。

**注意**:
- 在调用此函数时，需要确保传入的`texts`参数是有效的文本列表。
- `embed_model`参数应正确指定，以便函数能够找到并使用正确的嵌入模型进行文本向量化处理。如果未指定，将使用默认配置的嵌入模型。
- `to_query`参数应根据实际需求设置。如果向量化的文本用于查询，应将此参数设置为True，以优化向量化结果的使用场景。
- 函数的执行结果依赖于指定嵌入模型的有效性和可用性，因此在使用前应确认模型配置正确且模型可用。

**输出示例**:
调用`await aembed_texts(texts=["你好", "世界"], embed_model="example_model", to_query=False)`可能会返回如下`BaseResponse`对象：
```python
BaseResponse(code=200, msg="success", data=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
```
这表示两个文本"你好"和"世界"被成功向量化，向量化结果分别为`[0.1, 0.2, 0.3]`和`[0.4, 0.5, 0.6]`。

在项目中，`aembed_texts`函数被用于处理需要异步进行文本向量化的场景，如在知识库服务中对文本进行异步向量化以支持快速的文本查询和相似度计算。此外，它也支持通过在线API进行文本向量化，为项目提供了灵活的向量化解决方案。
## FunctionDef embed_texts_endpoint(texts, embed_model, to_query)
**embed_texts_endpoint**: 该函数的功能是对文本列表进行向量化处理，并返回处理结果。

**参数**:
- `texts`: 要嵌入的文本列表，是一个字符串列表。该参数是必需的。
- `embed_model`: 使用的嵌入模型。这可以是本地部署的Embedding模型，也可以是在线API提供的嵌入服务。默认值为配置中指定的嵌入模型。
- `to_query`: 布尔值，指示向量是否用于查询。有些模型如Minimax对存储/查询的向量进行了区分优化。默认值为False。

**代码描述**:
`embed_texts_endpoint`函数首先接收一个文本列表、一个嵌入模型名称以及一个布尔值参数。它调用`embed_texts`函数，将这些参数传递给该函数进行处理。`embed_texts`函数根据指定的嵌入模型对文本进行向量化处理，并返回一个`BaseResponse`对象，其中包含了向量化的结果。如果在向量化过程中遇到任何异常，`embed_texts`函数会捕获这些异常并返回一个包含错误信息的`BaseResponse`对象。`embed_texts_endpoint`函数最终返回`embed_texts`函数的输出，即向量化处理的结果。

**注意**:
- 在调用`embed_texts_endpoint`函数时，必须提供有效的文本列表。
- `embed_model`参数应该准确指定，以确保函数能够找到并使用正确的嵌入模型进行处理。
- 根据实际需求设置`to_query`参数，以优化向量化结果的使用场景。
- 函数的执行结果依赖于指定嵌入模型的有效性和可用性，因此在使用前应确认模型配置正确且模型可用。

**输出示例**:
调用`embed_texts_endpoint(texts=["hello", "world"], embed_model="example_model", to_query=False)`可能会返回如下`BaseResponse`对象：
```python
BaseResponse(code=200, msg="success", data=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
```
这表示两个文本"hello"和"world"被成功向量化，向量化结果分别为`[0.1, 0.2, 0.3]`和`[0.4, 0.5, 0.6]`。
## FunctionDef embed_documents(docs, embed_model, to_query)
**embed_documents**: 该函数的功能是将文档列表向量化，转化为向量存储系统可以接受的参数格式。

**参数**:
- `docs`: 文档对象的列表，每个文档包含页面内容和元数据。
- `embed_model`: 字符串类型，指定用于文档向量化的嵌入模型，默认使用预设的嵌入模型。
- `to_query`: 布尔类型，指示向量化的结果是否用于查询，默认为False。

**代码描述**:
`embed_documents`函数首先从文档列表中提取页面内容和元数据，分别存储在`texts`和`metadatas`列表中。接着，调用`embed_texts`函数对`texts`列表中的文本进行向量化处理，其中`embed_model`参数指定使用的嵌入模型，`to_query`参数指示向量化的目的。`embed_texts`函数返回一个包含向量化结果的数据结构。如果向量化成功，`embed_documents`函数将返回一个字典，包含原始文本列表`texts`、向量化结果`embeddings`和元数据列表`metadatas`。

**注意**:
- 在调用`embed_documents`函数时，确保传入的`docs`参数是有效的文档对象列表。
- `embed_model`参数应指向有效的嵌入模型，以确保文本能被正确向量化。
- 根据使用场景选择`to_query`参数的值，以优化向量化结果的应用。

**输出示例**:
假设调用`embed_documents(docs=[Document1, Document2], embed_model="example_model", to_query=False)`，可能会返回如下字典：
```python
{
    "texts": ["文档1的内容", "文档2的内容"],
    "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
    "metadatas": [{"title": "文档1标题"}, {"title": "文档2标题"}]
}
```
这表示两个文档被成功向量化，其中`texts`包含了文档的原始内容，`embeddings`包含了对应的向量化结果，`metadatas`包含了文档的元数据信息。
