## FunctionDef search_docs(query, knowledge_base_name, top_k, score_threshold, file_name, metadata)
**search_docs**: 此函数的功能是根据用户输入的查询条件，在指定的知识库中搜索相关文档。

**参数**:
- `query`: 字符串类型，默认为空字符串，表示用户的查询输入。
- `knowledge_base_name`: 字符串类型，必填，表示要搜索的知识库名称。
- `top_k`: 整型，表示返回的匹配向量数目。
- `score_threshold`: 浮点型，取值范围在0-1之间，表示知识库匹配相关度阈值。SCORE越小，相关度越高，取到1相当于不筛选。
- `file_name`: 字符串类型，默认为空字符串，表示文件名称，支持sql通配符。
- `metadata`: 字典类型，默认为空字典，表示根据metadata进行过滤，仅支持一级键。

**代码描述**:
函数首先通过`KBServiceFactory.get_service_by_name`方法获取指定知识库的服务实例。如果知识库服务实例存在，函数将根据是否提供了`query`参数来决定搜索逻辑。如果提供了`query`参数，函数将调用知识库服务实例的`search_docs`方法进行搜索，并将搜索结果转换为`DocumentWithVSId`对象列表返回。如果没有提供`query`但提供了`file_name`或`metadata`参数，函数将调用知识库服务实例的`list_docs`方法列出文档。最终，函数返回一个包含`DocumentWithVSId`对象的列表。

**注意**:
- 在使用此函数时，确保传入的知识库名称在系统中已存在，否则将无法获取知识库服务实例，导致搜索失败。
- `score_threshold`参数用于过滤搜索结果，较低的值意味着更高的相关性要求，可根据实际需求调整。
- 当`query`参数为空时，可以通过`file_name`或`metadata`参数来列出知识库中的文档，这在需要根据特定条件获取文档列表时非常有用。

**输出示例**:
假设在知识库中搜索"技术文档"，并且设置`top_k=2`，`score_threshold=0.5`，可能得到如下输出：
```python
[
    DocumentWithVSId(id="doc1", score=0.45, metadata={"title": "技术文档介绍", "author": "张三"}),
    DocumentWithVSId(id="doc2", score=0.48, metadata={"title": "技术文档使用手册", "author": "李四"})
]
```
此输出示例展示了根据查询条件返回的前两个最相关的文档对象列表，每个对象包含文档的唯一标识符、匹配得分以及元数据信息。
## FunctionDef update_docs_by_id(knowledge_base_name, docs)
**update_docs_by_id**: 按照文档 ID 更新文档内容。

**参数**:
- `knowledge_base_name`: 知识库名称，类型为字符串。此参数用于指定要更新文档的知识库。
- `docs`: 要更新的文档内容，类型为字典，形如 `{id: Document, ...}`。字典的键为文档的 ID，值为 `Document` 对象。

**代码描述**:
`update_docs_by_id` 函数首先通过 `KBServiceFactory.get_service_by_name` 方法，根据传入的知识库名称 `knowledge_base_name` 获取对应的知识库服务实例。如果指定的知识库不存在，函数将返回一个 `BaseResponse` 对象，其 `code` 属性设置为500，`msg` 属性表示指定的知识库不存在的错误信息。如果知识库存在，函数将调用知识库服务实例的 `update_doc_by_ids` 方法，尝试更新传入的文档。如果更新成功，函数返回一个 `BaseResponse` 对象，其 `msg` 属性表示文档更新成功的信息；如果更新失败，返回的 `BaseResponse` 对象的 `msg` 属性将表示文档更新失败的信息。

**注意**:
- 在调用此函数之前，确保传入的 `knowledge_base_name` 在系统中存在，否则将无法找到对应的知识库进行操作。
- `docs` 参数中的 `Document` 对象应包含要更新的文档内容。确保文档 ID 与知识库中现有文档的 ID 匹配，以便正确更新。
- 此函数的执行结果（成功或失败）将通过返回的 `BaseResponse` 对象的 `msg` 属性反馈。因此，调用此函数后应检查返回值，以确认操作结果。

**输出示例**:
如果指定的知识库名称不存在，函数可能返回如下的 `BaseResponse` 对象：
```python
BaseResponse(code=500, msg="指定的知识库 不存在")
```
如果文档更新成功，函数将返回：
```python
BaseResponse(msg="文档更新成功")
```
如果文档更新失败，函数将返回：
```python
BaseResponse(msg="文档更新失败")
```

此函数是项目中知识库管理功能的一部分，允许通过 API 直接根据文档 ID 更新知识库中的文档内容。它在 `server/api.py` 文件中通过 `mount_knowledge_routes` 函数注册为 API 路由，使得前端或其他服务可以通过发送 HTTP 请求来调用此功能，实现知识库文档的更新操作。
## FunctionDef list_files(knowledge_base_name)
**list_files**: 此函数用于列出指定知识库中的所有文件名。

**参数**:
- `knowledge_base_name`: 字符串类型，表示要查询文件列表的知识库名称。

**代码描述**: `list_files` 函数首先验证传入的知识库名称的合法性，如果名称不合法（例如包含潜在的安全风险字符），则返回一个403状态码和错误信息。之后，函数对知识库名称进行URL解码处理，以确保能够正确处理经过URL编码的知识库名称。接着，通过 `KBServiceFactory.get_service_by_name` 方法获取对应知识库的服务实例。如果该知识库不存在，则返回一个404状态码和错误信息。如果知识库存在，函数将调用知识库服务实例的 `list_files` 方法获取所有文件名，并将这些文件名作为数据返回给客户端。

**注意**:
- 在调用此函数之前，需要确保传入的知识库名称是经过URL编码的，以避免潜在的URL解析错误。
- 此函数依赖于 `KBServiceFactory.get_service_by_name` 方法来获取知识库服务实例，因此需要确保知识库名称在系统中是存在的。
- 返回的文件名列表是通过 `ListResponse` 类封装的，这意味着除了文件名列表数据外，还会包含响应的状态码和状态消息。

**输出示例**:
假设存在一个名为 "技术文档库" 的知识库，其中包含三个文件 "doc1.docx", "doc2.pdf", "doc3.txt"，调用 `list_files("技术文档库")` 将返回如下响应体：
```
{
    "code": 200,
    "msg": "success",
    "data": ["doc1.docx", "doc2.pdf", "doc3.txt"]
}
```
如果传入的知识库名称不合法或知识库不存在，将返回相应的错误状态码和消息，例如：
```
{
    "code": 403,
    "msg": "Don't attack me",
    "data": []
}
```
或
```
{
    "code": 404,
    "msg": "未找到知识库 技术文档库",
    "data": []
}
```
## FunctionDef _save_files_in_thread(files, knowledge_base_name, override)
**_save_files_in_thread**: 该函数的功能是通过多线程将上传的文件保存到对应知识库目录内。

**参数**:
- `files`: 一个`UploadFile`对象列表，表示需要保存的文件。
- `knowledge_base_name`: 字符串，指定要保存文件的知识库名称。
- `override`: 布尔值，指示如果文件已存在是否覆盖原文件。

**代码描述**:
`_save_files_in_thread`函数主要通过内部定义的`save_file`函数来处理单个文件的保存逻辑。对于每个上传的文件，它会首先检查目标路径是否存在同名文件，如果存在且不允许覆盖，或者文件大小相同，则记录一条警告日志并返回一个包含错误代码404的字典。如果文件不存在或允许覆盖，函数会创建必要的目录结构，并将文件内容写入目标路径。在写入文件的过程中，如果遇到异常，则记录一条错误日志并返回一个包含错误代码500的字典。

此函数使用`run_in_thread_pool`来并发执行`save_file`函数，以提高文件保存的效率。`run_in_thread_pool`接受一个函数和一个参数列表，其中每个参数都是一个字典，包含了`save_file`所需的参数。这样，`_save_files_in_thread`可以同时处理多个文件的保存操作，每个文件的保存操作在一个独立的线程中执行。

**注意**:
- 在使用此函数时，需要确保`knowledge_base_name`是有效的，且对应的知识库目录具有写入权限。
- 由于使用了多线程，需要注意线程安全问题，尤其是在写文件和创建目录时。
- 函数返回一个生成器，每次迭代返回一个文件的保存结果，因此调用此函数时需要适当处理这些结果。

**输出示例**:
```python
{
    "code": 200,
    "msg": "成功上传文件 example.txt",
    "data": {
        "knowledge_base_name": "sample_kb",
        "file_name": "example.txt"
    }
}
```
此示例展示了一个成功保存文件的返回值，其中包含了状态码、消息以及文件的相关信息。
### FunctionDef save_file(file, knowledge_base_name, override)
**save_file**: 此函数的功能是保存上传的单个文件到指定的知识库中。

**参数**:
- file: UploadFile类型，表示需要上传的文件。
- knowledge_base_name: 字符串类型，表示目标知识库的名称。
- override: 布尔类型，指示如果文件已存在是否覆盖原文件。

**代码描述**:
`save_file` 函数首先从上传的文件中提取文件名，并使用 `get_file_path` 函数构造目标文件的存储路径。此路径是基于知识库名称和文件名动态生成的，确保文件能够被正确地保存在对应的知识库目录下。

函数接着读取上传文件的内容。在尝试保存文件之前，会检查目标路径上的文件是否已存在，以及是否设置了不覆盖已存在文件的选项（`override` 参数）。如果文件已存在且不允许覆盖，函数将记录一条警告日志，并返回一个包含错误代码和消息的字典。

如果目标文件夹不存在，函数会创建必要的目录结构。然后，以二进制写入模式打开目标文件路径，将上传的文件内容写入其中。

在文件成功保存后，函数返回一个包含成功代码和消息的字典。如果在文件保存过程中发生异常，函数会捕获异常，记录一条错误日志，并返回一个包含错误代码和消息的字典。

**注意**:
- 在使用此函数之前，确保传入的 `file` 参数是一个有效的 `UploadFile` 对象，且 `knowledge_base_name` 参数正确指向一个存在的知识库。
- 如果设置 `override` 参数为 `False`，而目标文件已存在且文件大小与上传文件相同，则不会进行文件覆盖，而是返回文件已存在的消息。
- 异常处理是此函数的重要组成部分，确保了文件操作过程中的稳定性和可靠性。

**输出示例**:
成功上传文件时，可能的返回值为：
```
{
    "code": 200,
    "msg": "成功上传文件 example.docx",
    "data": {
        "knowledge_base_name": "my_knowledge_base",
        "file_name": "example.docx"
    }
}
```
如果文件已存在且不覆盖，返回值可能为：
```
{
    "code": 404,
    "msg": "文件 example.docx 已存在。",
    "data": {
        "knowledge_base_name": "my_knowledge_base",
        "file_name": "example.docx"
    }
}
```
在文件上传失败时，返回值可能为：
```
{
    "code": 500,
    "msg": "example.docx 文件上传失败，报错信息为: [具体错误信息]",
    "data": {
        "knowledge_base_name": "my_knowledge_base",
        "file_name": "example.docx"
    }
}
```
***
## FunctionDef upload_docs(files, knowledge_base_name, override, to_vector_store, chunk_size, chunk_overlap, zh_title_enhance, docs, not_refresh_vs_cache)
**upload_docs**: 此函数用于上传文件到知识库，并可选择进行文件的向量化处理。

**参数**:
- `files`: 上传的文件列表，支持多文件上传。
- `knowledge_base_name`: 知识库名称，指定要上传文件的目标知识库。
- `override`: 布尔值，指示是否覆盖已有文件。
- `to_vector_store`: 布尔值，指示上传文件后是否进行向量化处理。
- `chunk_size`: 知识库中单段文本的最大长度。
- `chunk_overlap`: 知识库中相邻文本的重合长度。
- `zh_title_enhance`: 布尔值，指示是否开启中文标题加强功能。
- `docs`: 自定义的docs，需转为json字符串格式。
- `not_refresh_vs_cache`: 布尔值，指示是否暂不保存向量库（用于FAISS）。

**代码描述**:
函数首先验证知识库名称的合法性，如果不合法，则返回403状态码并提示错误信息。接着，根据知识库名称获取对应的知识库服务实例。如果实例获取失败，则返回404状态码并提示未找到知识库。

函数继续执行，将上传的文件保存到磁盘，并记录保存失败的文件。对于需要进行向量化处理的文件，函数将调用`update_docs`函数进行处理，并更新失败文件列表。如果`not_refresh_vs_cache`为`False`，则会保存向量库。

最后，函数返回包含操作结果的响应，其中包括失败文件列表。

**注意**:
- 确保传入的知识库名称在系统中已存在。
- 上传的文件将被保存到指定的知识库目录中，如果`override`参数为`False`，则不会覆盖已存在的同名文件。
- 如果选择进行向量化处理，需要考虑服务器的性能和资源限制。
- 自定义的docs需要正确格式化为json字符串，以确保能够被正确解析和处理。

**输出示例**:
```json
{
  "code": 200,
  "msg": "文件上传与向量化完成",
  "data": {
    "failed_files": {
      "error_file.txt": "文件保存失败的错误信息"
    }
  }
}
```
此示例展示了函数执行成功的情况，其中`failed_files`字段列出了处理失败的文件及其错误信息。
## FunctionDef delete_docs(knowledge_base_name, file_names, delete_content, not_refresh_vs_cache)
**delete_docs**: 此函数用于从知识库中删除指定的文件。

**参数**:
- `knowledge_base_name`: 知识库的名称，类型为字符串，示例值为["samples"]。
- `file_names`: 需要删除的文件名称列表，类型为字符串列表，示例值为[["file_name.md", "test.txt"]]。
- `delete_content`: 布尔值，指定是否从磁盘中删除文件内容，默认为`False`。
- `not_refresh_vs_cache`: 布尔值，指定是否暂不保存向量库（用于FAISS），默认为`False`，描述为"暂不保存向量库（用于FAISS）"。

**代码描述**:
函数首先验证知识库名称的合法性，如果不合法，则返回403状态码和错误消息"Don't attack me"。之后，对知识库名称进行URL解码，并尝试获取对应的知识库服务实例。如果知识库服务实例不存在，则返回404状态码和错误消息，指出未找到知识库。

对于每个指定的文件名，函数检查文件是否存在于知识库中。如果文件不存在，将其添加到失败文件列表中。对于存在的文件，尝试删除文件，包括从知识库中删除记录和可选的从磁盘中删除文件内容。如果删除过程中发生异常，将异常信息记录到失败文件列表中，并记录错误日志。

如果`not_refresh_vs_cache`为`False`，则调用`save_vector_store`方法保存向量库。最后，函数返回200状态码和包含失败文件列表的响应。

**注意**:
- 在调用此函数之前，确保传入的知识库名称和文件名列表正确，且知识库存在。
- `delete_content`参数应谨慎使用，因为一旦从磁盘删除文件内容，该操作是不可逆的。
- `not_refresh_vs_cache`参数用于控制是否立即保存向量库的状态，这在批量删除文件时可以用来优化性能。

**输出示例**:
如果所有指定的文件都成功删除，且没有需要刷新的向量库，函数可能返回如下响应：
```json
{
  "code": 200,
  "msg": "文件删除完成",
  "data": {
    "failed_files": {}
  }
}
```
如果存在未找到或删除失败的文件，响应中的`failed_files`将包含这些文件的名称和相关错误信息。
## FunctionDef update_info(knowledge_base_name, kb_info)
**update_info**: 此函数用于更新知识库的介绍信息。

**参数**:
- `knowledge_base_name`: 知识库的名称，类型为字符串。此参数是必需的，用于指定要更新介绍信息的知识库。
- `kb_info`: 知识库的介绍信息，类型为字符串。此参数是必需的，用于提供新的知识库介绍。

**代码描述**:
首先，`update_info` 函数通过调用 `validate_kb_name` 函数验证传入的知识库名称是否合法。如果知识库名称不合法（例如包含潜在的安全风险字符），函数将返回一个状态码为403的 `BaseResponse` 对象，消息为"Don't attack me"，表示请求被拒绝。

如果知识库名称验证通过，函数接着尝试通过 `KBServiceFactory.get_service_by_name` 方法获取对应知识库的服务实例。如果指定的知识库不存在（即服务实例为None），函数将返回一个状态码为404的 `BaseResponse` 对象，消息为"未找到知识库 {knowledge_base_name}"，表示未找到指定的知识库。

当知识库服务实例成功获取后，函数调用该实例的 `update_info` 方法，传入新的知识库介绍信息 `kb_info` 进行更新。

最后，函数返回一个状态码为200的 `BaseResponse` 对象，消息为"知识库介绍修改完成"，并在数据字段中返回更新后的知识库介绍信息，表示知识库介绍信息更新成功。

**注意**:
- 在调用此函数之前，确保传入的知识库名称在系统中已存在且合法，否则可能会导致更新失败。
- 更新知识库介绍信息的操作可能会受到知识库服务实例类型的限制，确保知识库服务支持信息更新操作。

**输出示例**:
如果更新操作成功，函数可能返回如下的 `BaseResponse` 对象示例：
```
{
    "code": 200,
    "msg": "知识库介绍修改完成",
    "data": {
        "kb_info": "这是一个更新后的知识库介绍"
    }
}
```
如果知识库名称不合法，返回的 `BaseResponse` 对象示例可能如下：
```
{
    "code": 403,
    "msg": "Don't attack me",
    "data": null
}
```
如果未找到指定的知识库，返回的 `BaseResponse` 对象示例可能如下：
```
{
    "code": 404,
    "msg": "未找到知识库 {knowledge_base_name}",
    "data": null
}
```
## FunctionDef update_docs(knowledge_base_name, file_names, chunk_size, chunk_overlap, zh_title_enhance, override_custom_docs, docs, not_refresh_vs_cache)
**update_docs**: 此函数用于更新知识库中的文档。

**参数**:
- `knowledge_base_name`: 知识库名称，字符串类型，必填参数。
- `file_names`: 文件名称列表，支持多文件，列表中每个元素为字符串类型。
- `chunk_size`: 知识库中单段文本最大长度，整数类型。
- `chunk_overlap`: 知识库中相邻文本重合长度，整数类型。
- `zh_title_enhance`: 是否开启中文标题加强，布尔类型。
- `override_custom_docs`: 是否覆盖之前自定义的docs，布尔类型，默认为False。
- `docs`: 自定义的docs，需要转为json字符串，字典类型。
- `not_refresh_vs_cache`: 暂不保存向量库（用于FAISS），布尔类型，默认为False。

**代码描述**:
此函数首先验证传入的知识库名称是否合法，如果不合法，则返回403状态码和错误信息。接着，通过知识库名称获取对应的知识库服务实例。如果实例获取失败，则返回404状态码和错误信息。

函数继续执行，生成需要加载docs的文件列表。对于每个文件，首先检查该文件是否使用了自定义docs，如果是且不覆盖自定义docs，则跳过该文件。否则，尝试将文件添加到待处理列表中。如果在此过程中出现异常，则记录错误信息。

接下来，函数将文件列表中的文件转换为docs，并进行向量化处理。这一步骤利用多线程在后台执行，以提高处理效率。处理完成后，如果指定了不刷新向量库缓存，则不立即保存向量库；否则，调用知识库服务的`save_vector_store`方法保存向量库。

最后，函数返回200状态码和处理结果，包括处理失败的文件列表。

**注意**:
- 在使用此函数时，确保传入的知识库名称在系统中已存在。
- 如果需要对文件进行自定义docs处理，确保`docs`参数格式正确，并且文件名与`file_names`中的文件名匹配。
- 此函数支持批量处理文件，但需要注意服务器资源和性能限制。

**输出示例**:
```json
{
  "code": 200,
  "msg": "更新文档完成",
  "data": {
    "failed_files": {
      "error_file.txt": "加载文档时出错"
    }
  }
}
```
此示例展示了函数执行成功的情况，其中`failed_files`字段列出了处理失败的文件及其错误信息。
## FunctionDef download_doc(knowledge_base_name, file_name, preview)
**download_doc**: 此函数用于下载知识库中的文档。

**参数**:
- `knowledge_base_name`: 知识库名称，用于指定从哪个知识库下载文档。
- `file_name`: 文件名称，指定要下载的文件名。
- `preview`: 是否预览，布尔值，指示用户是希望在浏览器中预览文件还是直接下载文件。

**代码描述**:
`download_doc` 函数首先通过调用 `validate_kb_name` 函数验证传入的知识库名称是否合法。如果知识库名称不合法，函数将返回一个带有403状态码的 `BaseResponse` 对象，提示用户不要进行攻击。接着，函数尝试通过 `KBServiceFactory.get_service_by_name` 方法获取对应知识库的服务实例。如果找不到对应的知识库服务实例，将返回一个带有404状态码的 `BaseResponse` 对象，提示未找到指定的知识库。

根据 `preview` 参数的值，函数设置 `content_disposition_type`。如果 `preview` 为 `True`，则设置为 `"inline"`，允许在浏览器中预览文件；否则，`content_disposition_type` 为 `None`，表示文件将被下载。

然后，函数创建一个 `KnowledgeFile` 实例，用于表示和处理知识库中的文件。如果文件存在于磁盘上，函数将返回一个 `FileResponse` 对象，允许用户下载或预览文件。如果在尝试读取文件时发生异常，函数将记录错误信息并返回一个带有500状态码的 `BaseResponse` 对象，提示读取文件失败。

**注意**:
- 在调用此函数之前，确保传入的知识库名称和文件名称是正确的。
- 如果知识库名称不合法或文件不存在，函数将返回错误响应。
- 此函数支持文件预览和下载功能，通过 `preview` 参数控制。

**输出示例**:
假设存在一个名为 "samples" 的知识库，其中包含一个名为 "test.txt" 的文件。如果调用 `download_doc(knowledge_base_name="samples", file_name="test.txt", preview=False)`，函数将返回一个 `FileResponse` 对象，允许用户下载 "test.txt" 文件。如果指定的文件不存在，将返回一个带有404状态码的 `BaseResponse` 对象，提示未找到文件。
## FunctionDef recreate_vector_store(knowledge_base_name, allow_empty_kb, vs_type, embed_model, chunk_size, chunk_overlap, zh_title_enhance, not_refresh_vs_cache)
**recreate_vector_store**: 该函数用于根据内容文件夹中的文档重建向量库。

**参数**:
- `knowledge_base_name`: 知识库名称，类型为字符串，默认示例为“samples”。
- `allow_empty_kb`: 是否允许空的知识库，布尔类型，默认为True。
- `vs_type`: 向量库类型，字符串类型，默认值为`DEFAULT_VS_TYPE`。
- `embed_model`: 嵌入模型名称，字符串类型，默认值为`EMBEDDING_MODEL`。
- `chunk_size`: 知识库中单段文本的最大长度，整数类型，默认值为`CHUNK_SIZE`。
- `chunk_overlap`: 知识库中相邻文本的重合长度，整数类型，默认值为`OVERLAP_SIZE`。
- `zh_title_enhance`: 是否开启中文标题加强功能，布尔类型，默认值为`ZH_TITLE_ENHANCE`。
- `not_refresh_vs_cache`: 是否暂不保存向量库（用于FAISS），布尔类型，默认为False。

**代码描述**:
`recreate_vector_store`函数主要用于在用户直接将文件复制到内容文件夹而不是通过网络上传输的情况下，从这些内容文件中重建向量库。默认情况下，只有在`info.db`中存在且包含文档文件的知识库才会被返回。通过将`allow_empty_kb`设置为True，可以使该函数也适用于那些在`info.db`中不存在或没有文档的空知识库。函数内部首先尝试获取指定的知识库服务，如果知识库不存在且不允许空的知识库，则返回404错误。如果知识库存在，则清除现有的向量库并重新创建。随后，函数遍历内容文件夹中的所有文件，并将它们转换为文档，同时考虑文本的分块大小、重合长度以及是否开启中文标题加强功能。每处理完一个文件，就会生成一个包含处理状态的JSON对象，并通过生成器返回。如果在添加文件到知识库时出现错误，则记录错误并跳过该文件。最后，如果不是设置为不刷新向量库缓存，则保存向量库。

在项目中，`recreate_vector_store`函数通过`server/api.py/mount_knowledge_routes`被注册为FastAPI的一个POST路由。这意味着该函数可以通过HTTP POST请求被调用，用于在用户通过其他方式将文件直接放入内容文件夹后，重新构建知识库的向量库。这在管理知识库时特别有用，尤其是在需要批量更新文档内容而不想逐个上传时。

**注意**:
- 确保在调用此函数之前，内容文件夹中的文件格式和内容符合知识库的要求。
- 函数的执行时间可能会根据内容文件夹中的文件数量和大小而有很大差异。

**输出示例**:
```json
{
    "code": 200,
    "msg": "(1 / 10): example.docx",
    "total": 10,
    "finished": 1,
    "doc": "example.docx"
}
```
此JSON对象表示第一个文件处理成功，总共有10个文件需要处理，当前已完成1个。
### FunctionDef output
**output**: 此函数的功能是重建知识库的向量存储，并输出处理过程中的状态信息。

**参数**: 此函数不接受任何外部参数。

**代码描述**: 
`output` 函数首先通过 `KBServiceFactory.get_service` 方法获取对应知识库的服务实例，该实例根据知识库名称、向量存储类型和嵌入模型来确定。如果指定的知识库不存在且不允许创建空的知识库，则函数会生成并返回一个包含错误代码404和相应错误信息的JSON对象。如果知识库存在，函数会先清除知识库中的向量存储，然后重新创建知识库。

接下来，函数通过 `list_files_from_folder` 方法列出知识库文件夹中的所有文件，并为每个文件创建一个 `KnowledgeFile` 实例。这些文件实例随后被批量处理，通过 `files2docs_in_thread` 方法将文件内容转换为文档，并添加到知识库中。在文件转换过程中，函数会逐个生成并返回包含处理状态的JSON对象，这些对象包含了处理进度、文件名等信息。

如果在文件转换过程中遇到错误，函数会记录错误信息并生成包含错误代码500和相应错误信息的JSON对象。所有文件处理完成后，如果不需要刷新向量存储缓存，则会调用 `save_vector_store` 方法保存向量库。

**注意**:
- 在调用此函数之前，需要确保 `KBServiceFactory.get_service` 能够根据提供的参数正确返回知识库服务实例。
- `list_files_from_folder` 方法用于列出知识库文件夹中的所有文件，确保知识库文件夹路径正确。
- `files2docs_in_thread` 方法负责将文件内容转换为文档并添加到知识库中，该过程是多线程执行的，需要注意线程安全问题。
- `save_vector_store` 方法用于保存向量库，确保在调用此方法之前，所有需要保存的数据已经正确处理完毕。
- 此函数通过生成器返回处理状态信息，调用方需要适当处理这些生成的JSON对象，以实现状态监控或错误处理。
***
