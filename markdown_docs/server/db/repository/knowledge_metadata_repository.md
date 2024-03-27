## FunctionDef list_summary_from_db(session, kb_name, metadata)
**list_summary_from_db**: 该函数的功能是列出某知识库中的chunk summary信息。

**参数**:
- `session`: 数据库会话实例，用于执行数据库查询。
- `kb_name`: 字符串类型，指定要查询的知识库名称。
- `metadata`: 字典类型，默认为空字典，用于过滤具有特定元数据的summary。

**代码描述**:
`list_summary_from_db` 函数通过接收一个数据库会话、知识库名称以及可选的元数据字典作为参数，来查询特定知识库中的summary信息。首先，函数使用传入的知识库名称对`SummaryChunkModel`模型进行过滤查询，以获取该知识库下的所有summary信息。如果提供了元数据字典，函数将进一步根据元数据的键值对过滤这些summary信息。最终，函数将查询结果格式化为一个列表，每个元素是一个字典，包含summary的id、summary_context、summary_id、doc_ids以及metadata，然后返回这个列表。

**注意**:
- 在使用`list_summary_from_db`函数时，确保传入的`session`是一个有效的数据库会话实例。
- `kb_name`参数应确保与数据库中存储的知识库名称匹配，该参数支持大小写不敏感的匹配。
- 当使用`metadata`参数进行过滤查询时，确保字典中的键和值与`SummaryChunkModel`中的`meta_data`字段中存储的键值对相匹配。

**输出示例**:
调用`list_summary_from_db`函数可能返回如下格式的列表：
```
[
    {
        "id": "1",
        "summary_context": "这是一个关于AI技术的摘要",
        "summary_id": "summary123",
        "doc_ids": "['doc1', 'doc2']",
        "metadata": {}
    },
    {
        "id": "2",
        "summary_context": "这是第二个摘要的示例文本",
        "summary_id": "summary456",
        "doc_ids": "['doc3', 'doc4']",
        "metadata": {"page": "1-2"}
    }
]
```
这个示例展示了两个summary的信息，每个summary包含id、摘要内容（summary_context）、摘要ID（summary_id）、关联的文档ID列表（doc_ids）以及额外的元数据信息（metadata）。
## FunctionDef delete_summary_from_db(session, kb_name)
**delete_summary_from_db**: 该函数的功能是删除指定知识库的chunk summary，并返回被删除的chunk summary信息。

**参数**:
- `session`: 数据库会话实例，用于执行数据库操作。
- `kb_name`: 字符串类型，指定要删除summary的知识库名称。

**代码描述**:
`delete_summary_from_db` 函数首先调用 `list_summary_from_db` 函数，根据传入的知识库名称 `kb_name` 列出该知识库中所有的chunk summary信息。接着，函数构造一个查询，通过 `session.query` 方法和 `SummaryChunkModel` 模型，使用 `filter` 方法对知识库名称进行过滤，匹配大小写不敏感的知识库名称。然后，使用 `query.delete` 方法删除匹配的所有记录，并通过 `session.commit` 方法提交更改到数据库。最后，函数返回之前通过 `list_summary_from_db` 函数获取的被删除的chunk summary信息列表。

**注意**:
- 在调用此函数之前，确保传入的 `session` 是一个有效的数据库会话实例，并且已经正确配置。
- `kb_name` 参数应确保与数据库中存储的知识库名称匹配，且该参数支持大小写不敏感的匹配，以确保能正确找到目标知识库。
- 函数执行删除操作后会立即提交更改，因此请谨慎使用，以避免误删除重要数据。

**输出示例**:
调用 `delete_summary_from_db` 函数可能返回如下格式的列表：
```
[
    {
        "id": "1",
        "summary_context": "这是一个关于AI技术的摘要",
        "doc_ids": "['doc1', 'doc2']"
    },
    {
        "id": "2",
        "summary_context": "这是第二个摘要的示例文本",
        "doc_ids": "['doc3', 'doc4']"
    }
]
```
这个示例展示了两个被删除的summary的信息，每个summary包含id、摘要内容（summary_context）以及关联的文档ID列表（doc_ids）。
## FunctionDef add_summary_to_db(session, kb_name, summary_infos)
**add_summary_to_db**: 此函数的功能是将总结信息添加到数据库中。

**参数**:
- `session`: 数据库会话实例，用于执行数据库操作。
- `kb_name`: 字符串类型，指定要添加摘要信息的知识库名称。
- `summary_infos`: 字典列表，每个字典包含一个总结信息，包括总结文本、文档标识符等信息。

**代码描述**:
`add_summary_to_db` 函数接收一个数据库会话、知识库名称以及一个包含多个总结信息的列表。每个总结信息是一个字典，包含了总结文本(`summary_context`)、总结ID(`summary_id`)、文档ID列表(`doc_ids`)以及额外的元数据(`metadata`)。函数遍历这个列表，为每个总结信息创建一个`SummaryChunkModel`实例，并将其添加到数据库会话中。完成所有总结信息的添加后，函数提交会话以保存更改，并返回`True`表示操作成功。

在这个过程中，`SummaryChunkModel`是用于映射数据库中的摘要信息表的模型，它定义了如何存储知识库名称、总结文本、总结ID、文档ID列表和元数据等信息。

**注意**:
- 确保传入的`session`是一个有效的数据库会话实例，且在调用此函数之前已经正确配置。
- `summary_infos`列表中的每个字典都必须包含`summary_context`、`summary_id`、`doc_ids`和`metadata`键。
- `metadata`字段应以正确的JSON格式传入，以避免在序列化或反序列化时出现错误。
- 函数执行后，需要检查返回值确保总结信息已成功添加到数据库。

**输出示例**:
调用`add_summary_to_db`函数通常不直接返回具体的数据实例，而是返回一个布尔值`True`，表示所有总结信息已成功添加到数据库。
## FunctionDef count_summary_from_db(session, kb_name)
**count_summary_from_db**: 此函数的功能是统计指定知识库名称下的摘要信息数量。

**参数**:
- `session`: 数据库会话实例，用于执行数据库查询。
- `kb_name`: 字符串类型，指定要查询摘要数量的知识库名称。

**代码描述**:
`count_summary_from_db` 函数通过接收一个数据库会话实例和一个知识库名称作为参数，利用这个会话实例来查询 `SummaryChunkModel` 表中与给定知识库名称相匹配的摘要信息数量。在查询过程中，使用了 `ilike` 方法来实现不区分大小写的匹配，这意味着无论传入的知识库名称的大小写如何，都能正确地匹配到相应的记录。此函数返回一个整数，表示匹配到的摘要信息数量。

在项目的层次结构中，`count_summary_from_db` 函数属于 `knowledge_metadata_repository.py` 文件，该文件作为数据库仓库层的一部分，主要负责处理与知识库元数据相关的数据操作。`count_summary_from_db` 函数通过查询 `SummaryChunkModel`，与之关联的 `knowledge_metadata_model.py` 中定义的 `SummaryChunkModel` 类直接交互。`SummaryChunkModel` 类定义了摘要信息的数据模型，包括知识库名称、摘要文本等字段，是数据库中存储摘要信息的表结构映射。

**注意**:
- 在调用此函数时，确保传入的 `session` 参数是一个有效的数据库会话实例，且 `kb_name` 参数是一个非空字符串。
- 由于使用了 `ilike` 方法进行模糊匹配，调用此函数时应考虑性能影响，特别是在处理大量数据时。

**输出示例**:
假设数据库中有3条属于“技术文档”知识库的摘要信息，调用 `count_summary_from_db(session, "技术文档")` 将返回整数 `3`。
