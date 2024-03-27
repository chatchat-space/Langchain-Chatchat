## FunctionDef list_file_num_docs_id_by_kb_name_and_file_name(session, kb_name, file_name)
**list_file_num_docs_id_by_kb_name_and_file_name**: 此函数的功能是列出某知识库中某文件对应的所有文档ID。

**参数**:
- `session`: 数据库会话实例，用于执行数据库查询。
- `kb_name`: 字符串类型，指定知识库的名称。
- `file_name`: 字符串类型，指定文件的名称。

**代码描述**:
`list_file_num_docs_id_by_kb_name_and_file_name`函数通过接收数据库会话、知识库名称以及文件名称作为参数，利用这些参数对数据库中的`FileDocModel`表进行查询。查询的目的是找出所有与给定知识库名称和文件名称相匹配的文档ID。这些文档ID随后被转换为整数列表返回。此过程涉及到对`FileDocModel`模型的`doc_id`字段进行筛选，确保只有符合条件的记录被选中。最终，函数返回一个整数列表，包含了所有匹配文档的ID。

**注意**:
- 确保传入的`session`是一个有效的数据库会话实例，且已正确配置以连接到目标数据库。
- `kb_name`和`file_name`参数应准确无误，以匹配数据库中的记录。大小写敏感性取决于数据库配置。
- 返回的文档ID列表是基于数据库中实际存在的记录，如果没有找到匹配的记录，则返回空列表。

**输出示例**:
假设存在两个文档，它们的ID分别为1和2，且这两个文档都属于知识库"知识库A"中的"文件B.pdf"，那么调用此函数并传入相应的知识库名称和文件名称后，将返回列表`[1, 2]`。

通过此函数，可以方便地根据知识库名称和文件名称获取相关文档的ID，进而支持进行进一步的文档管理或操作，如在`MilvusKBService`的`do_delete_doc`方法中，使用此函数获取到的文档ID列表用于指定删除向量库中相应的文档记录。
## FunctionDef list_docs_from_db(session, kb_name, file_name, metadata)
**list_docs_from_db**: 此函数的功能是列出某知识库某文件对应的所有文档。

**参数**:
- `session`: 数据库会话实例，用于执行数据库查询。
- `kb_name`: 字符串类型，指定要查询的知识库名称。
- `file_name`: 字符串类型，可选参数，默认为None，指定要查询的文件名称。
- `metadata`: 字典类型，可选参数，默认为空字典，用于根据文档的元数据进行过滤查询。

**代码描述**:
该函数首先根据知识库名称`kb_name`对`FileDocModel`进行查询，如果提供了`file_name`参数，则进一步根据文件名称进行过滤。随后，遍历`metadata`字典中的每一项，根据元数据的键和值对查询结果进行过滤。最终，函数返回一个列表，列表中的每个元素都是一个字典，包含文档的ID(`id`)和元数据(`metadata`)。

在实现上，`list_docs_from_db`函数通过ORM模型`FileDocModel`与数据库交互，利用SQLAlchemy的查询接口进行数据检索。`FileDocModel.kb_name.ilike(kb_name)`和`FileDocModel.file_name.ilike(file_name)`使用了`ilike`方法进行不区分大小写的模糊匹配，增强了查询的灵活性。对于元数据的查询，通过`FileDocModel.meta_data[k].as_string() == str(v)`实现了对JSON类型字段的条件过滤。

**注意**:
- 在使用此函数时，应确保传入的`session`是一个有效的数据库会话实例。
- 由于`metadata`参数默认为一个空字典，修改此默认值可能会影响到函数的预期行为。建议在调用函数时显式传入所需的`metadata`参数，避免直接修改函数定义中的默认值。
- 在处理大量数据时，应考虑查询性能和优化，避免执行过多的过滤操作导致查询速度缓慢。

**输出示例**:
假设数据库中存在两条记录，其字段值分别为：
- id: 1, kb_name: "知识库A", file_name: "文件A.pdf", doc_id: "docA", metadata: {"author": "张三", "year": "2021"}
- id: 2, kb_name: "知识库A", file_name: "文件B.pdf", doc_id: "docB", metadata: {"author": "李四", "year": "2022"}

调用`list_docs_from_db(session, "知识库A")`将返回以下列表：
```python
[
    {"id": "docA", "metadata": {"author": "张三", "year": "2021"}},
    {"id": "docB", "metadata": {"author": "李四", "year": "2022"}}
]
```
此输出示例展示了函数如何根据指定的知识库名称返回该知识库下所有文档的ID和元数据。
## FunctionDef delete_docs_from_db(session, kb_name, file_name)
**delete_docs_from_db**: 此函数的功能是删除某知识库某文件对应的所有文档，并返回被删除的文档信息。

**参数**:
- `session`: 数据库会话实例，用于执行数据库操作。
- `kb_name`: 字符串类型，指定要删除文档的知识库名称。
- `file_name`: 字符串类型，可选参数，默认为None，指定要删除文档的文件名称。

**代码描述**:
`delete_docs_from_db`函数首先调用`list_docs_from_db`函数，根据知识库名称`kb_name`和文件名称`file_name`（如果提供）列出所有对应的文档。然后，构造一个查询对象，通过`session.query(FileDocModel)`获取`FileDocModel`的查询接口，并使用`filter`方法根据知识库名称进行过滤。如果提供了`file_name`参数，则进一步根据文件名称进行过滤。接下来，使用`query.delete(synchronize_session=False)`方法删除满足条件的所有文档记录，并通过`session.commit()`提交事务，确保更改被保存到数据库中。最后，函数返回之前通过`list_docs_from_db`获取的被删除文档的列表。

**注意**:
- 在调用此函数之前，应确保传入的`session`是一个有效的数据库会话实例，并且已经正确配置。
- 删除操作是不可逆的，因此在执行此函数之前，请确保确实需要删除这些文档。
- 由于此函数返回被删除的文档信息，可以用于记录日志或进行后续处理。

**输出示例**:
假设数据库中存在两条文档记录，其知识库名称为"知识库A"，文件名称分别为"文件A.pdf"和"文件B.pdf"，调用`delete_docs_from_db(session, "知识库A", "文件A.pdf")`后，函数可能返回以下列表：
```python
[
    {"id": "docA", "metadata": {"author": "张三", "year": "2021"}}
]
```
此输出示例展示了函数如何返回被删除的文档的ID和元数据信息。
## FunctionDef add_docs_to_db(session, kb_name, file_name, doc_infos)
**add_docs_to_db**: 此函数的功能是将某知识库某文件对应的所有Document信息添加到数据库中。

**参数**:
- `session`: 数据库会话实例，用于执行数据库操作。
- `kb_name`: 字符串类型，指定要添加文档信息的知识库名称。
- `file_name`: 字符串类型，指定要添加文档信息的文件名称。
- `doc_infos`: 文档信息列表，每个元素是一个字典，包含文档的ID和元数据。

**代码描述**:
`add_docs_to_db`函数主要用于将文档信息批量添加到数据库中。它接收一个数据库会话、知识库名称、文件名称以及文档信息列表作为参数。文档信息列表`doc_infos`的格式为`[{"id": str, "metadata": dict}, ...]`，其中每个字典代表一个文档的信息，包括文档的ID和元数据。

函数首先检查`doc_infos`是否为`None`，如果是，则打印一条错误信息，并返回`False`表示添加失败。这是为了处理可能的错误情况，确保函数的健壮性。

接下来，函数遍历`doc_infos`列表，对于列表中的每个文档信息，创建一个`FileDocModel`实例。`FileDocModel`是一个ORM模型，用于映射数据库中的`file_doc`表，它包含了文档的基本信息字段，如知识库名称、文件名称、文档ID以及元数据。创建`FileDocModel`实例时，会将当前遍历到的文档信息填充到相应的字段中。

然后，使用`session.add(obj)`将`FileDocModel`实例添加到数据库会话中，这样就可以将文档信息保存到数据库中。遍历完成后，函数返回`True`表示所有文档信息已成功添加到数据库。

**注意**:
- 确保传入的`session`是有效的数据库会话实例，且已正确配置数据库连接。
- `doc_infos`参数不能为空，且其内部的字典需要包含`id`和`metadata`键。
- 在实际应用中，可能需要处理`session.add(obj)`操作可能引发的异常，例如数据库约束违反等。

**输出示例**:
此函数没有直接的输出示例，因为它的主要作用是影响数据库状态。但在成功执行后，可以预期数据库中的`file_doc`表将新增相应的记录，记录的字段值将反映函数调用时提供的参数值。
## FunctionDef count_files_from_db(session, kb_name)
**count_files_from_db**: 此函数的功能是统计指定知识库中的文件数量。

**参数**:
- `session`: 数据库会话实例，用于执行数据库查询。
- `kb_name`: 字符串类型，指定要统计文件数量的知识库名称。

**代码描述**:
`count_files_from_db`函数通过接收一个数据库会话实例和一个知识库名称作为参数，利用ORM模型`KnowledgeFileModel`来查询指定知识库中的文件数量。在这个过程中，函数首先构造一个查询，该查询针对`KnowledgeFileModel`模型，使用`filter`方法根据知识库名称（`kb_name`）进行筛选，这里使用`ilike`方法实现不区分大小写的匹配，以增强查询的灵活性。最后，使用`count`方法计算并返回符合条件的记录数，即指定知识库中的文件数量。

**注意**:
- 在调用此函数时，确保传入的`session`参数是一个有效的数据库会话实例，且`kb_name`参数正确指定了目标知识库的名称。
- 由于使用了`ilike`方法进行模糊匹配，可以灵活匹配知识库名称，但在使用时应注意名称的准确性，以避免错误的统计结果。

**输出示例**:
如果指定知识库名称为"DefaultKB"，并且该知识库中有10个文件，调用`count_files_from_db(session, "DefaultKB")`将返回整数`10`，表示"DefaultKB"知识库中的文件数量为10。

此函数在项目中的应用场景包括，但不限于，知识库服务（如`KBService`类中的`count_files`方法）调用此函数来获取特定知识库中的文件总数，以支持知识库管理和数据分析等功能。
## FunctionDef list_files_from_db(session, kb_name)
**list_files_from_db**: 此函数的功能是从数据库中列出属于特定知识库的所有文件名。

**参数**:
- `session`: 数据库会话对象，用于执行数据库查询。
- `kb_name`: 知识库的名称，用于筛选特定知识库的文件。

**代码描述**:
`list_files_from_db`函数通过接收一个数据库会话对象和一个知识库名称作为参数，利用这个会话对象执行一个查询操作。这个查询是基于`KnowledgeFileModel`模型，筛选出`kb_name`字段与传入的知识库名称相匹配的所有记录。这里使用了`ilike`方法，它允许在比较时不区分大小写，增加了查询的灵活性。查询结果是`KnowledgeFileModel`的实例列表，代表找到的所有文件。然后，函数遍历这个列表，提取每个实例的`file_name`属性，即文件名，将这些文件名收集到一个列表中。最后，返回这个列表，包含了所有符合条件的文件名。

**注意**:
- 确保传入的`session`对象是有效的数据库会话实例，且已正确配置与数据库的连接。
- 传入的知识库名称`kb_name`应确保其准确性，因为查询结果直接依赖于此参数。
- 查询使用了`ilike`方法，对大小写不敏感，但这可能会影响查询性能，特别是在大型数据库中。

**输出示例**:
如果数据库中存在属于名为"GeneralKB"的知识库的文件，且这些文件名分别为"document1.pdf"、"report2.docx"，那么调用`list_files_from_db(session, "GeneralKB")`将返回以下列表：
```
["document1.pdf", "report2.docx"]
```
## FunctionDef add_file_to_db(session, kb_file, docs_count, custom_docs, doc_infos)
**add_file_to_db**: 此函数的功能是将文件信息添加到数据库中，如果文件已存在，则更新该文件的信息和版本号。

**参数**:
- `session`: 数据库会话实例，用于执行数据库操作。
- `kb_file`: `KnowledgeFile` 类型，表示要添加到数据库的知识文件。
- `docs_count`: 整型，默认为0，表示文件中包含的文档数量。
- `custom_docs`: 布尔型，默认为False，表示文件中的文档是否为自定义文档。
- `doc_infos`: 文档信息列表，每个元素是一个字典，格式为`[{"id": str, "metadata": dict}, ...]`，包含文档的ID和元数据。

**代码描述**:
`add_file_to_db` 函数首先查询数据库中是否存在指定的知识库，如果存在，则继续检查该知识库中是否已有同名文件。如果文件已存在，函数将更新该文件的最后修改时间、文件大小、文档数量、是否为自定义文档标志以及文件版本号。如果文件不存在，则创建一个新的 `KnowledgeFileModel` 实例，并设置相应的文件信息，包括文件名、文件扩展名、所属知识库名称、文档加载器名称、文本分割器名称、文件修改时间、文件大小、文档数量和自定义文档标志。然后，将新文件实例添加到数据库会话中，并增加知识库的文件计数。无论文件是否已存在，都会调用 `add_docs_to_db` 函数，将文件对应的所有文档信息添加到数据库中。

**注意**:
- 确保传入的 `session` 是有效的数据库会话实例。
- `kb_file` 参数必须是 `KnowledgeFile` 类型的实例，且其属性应正确设置以反映文件的实际信息。
- `doc_infos` 参数中的每个字典必须包含 `id` 和 `metadata` 键。
- 在实际应用中，可能需要处理数据库操作可能引发的异常，例如违反唯一性约束等。

**输出示例**:
此函数没有直接的输出示例，因为它的主要作用是影响数据库状态。但在成功执行后，可以预期数据库中的 `knowledge_file` 表将新增或更新相应的记录，记录的字段值将反映函数调用时提供的参数值。
## FunctionDef delete_file_from_db(session, kb_file)
**delete_file_from_db**: 此函数的功能是从数据库中删除指定的知识文件，并更新相关知识库的文件计数。

**参数**:
- `session`: 数据库会话实例，用于执行数据库操作。
- `kb_file`: `KnowledgeFile`类型的对象，表示需要从数据库中删除的知识文件。

**代码描述**:
`delete_file_from_db`函数首先通过传入的`session`和`kb_file`对象构造查询条件，查询目标知识文件是否存在于`KnowledgeFileModel`表中。如果存在，函数将执行以下操作：
1. 使用`session.delete(existing_file)`方法从数据库中删除找到的文件记录。
2. 调用`delete_docs_from_db`函数，根据知识文件的名称和所属知识库名称删除该文件对应的所有文档记录。
3. 提交数据库事务，确保上述删除操作被保存到数据库中。
4. 查询`KnowledgeBaseModel`表，找到该知识文件所属的知识库记录，并将该知识库的`file_count`（文件计数）减1，再次提交数据库事务以保存更改。

**注意**:
- 在执行删除操作前，请确保传入的`session`是一个有效的数据库会话实例，并且已经正确配置。
- 删除操作是不可逆的，因此在执行此函数之前，请确保确实需要删除指定的知识文件及其相关文档。
- 函数在成功删除文件和相关文档后，会更新知识库的文件计数。这一步骤对于维护知识库的准确性非常重要。

**输出示例**:
该函数没有直接的输出示例，因为它主要执行数据库的删除操作。函数执行成功后，会返回`True`，表示知识文件及其相关文档已被成功删除，并且相关知识库的文件计数已更新。如果需要验证操作结果，可以通过查询数据库来确认指定的知识文件和文档是否已被删除，以及相应知识库的文件计数是否已减少。
## FunctionDef delete_files_from_db(session, knowledge_base_name)
**delete_files_from_db**: 该函数的功能是从数据库中删除指定知识库的所有文件记录。

**参数**:
- `session`: 数据库会话实例，用于执行数据库操作。
- `knowledge_base_name`: 字符串类型，指定要删除文件的知识库名称。

**代码描述**:
`delete_files_from_db` 函数首先查询 `KnowledgeFileModel` 表，删除与指定知识库名称匹配的所有文件记录。接着，该函数查询 `FileDocModel` 表，同样删除与指定知识库名称匹配的所有文档记录。这两个操作都使用了 `ilike` 方法来进行不区分大小写的匹配，确保能够匹配到所有相关记录。之后，函数查询 `KnowledgeBaseModel` 表，找到对应的知识库实例，如果找到了，就将该知识库的文件计数设置为0，表示知识库中不再包含任何文件。最后，函数提交所有更改到数据库，并返回 `True`，表示操作成功完成。

**注意**:
- 在调用此函数之前，确保传入的 `session` 是有效的数据库会话实例，并且已经正确配置。
- 该函数会永久删除指定知识库中的所有文件记录，此操作不可逆，请谨慎使用。
- 在删除文件记录之后，相关联的知识库的文件计数会被重置为0，这意味着知识库将不再包含任何文件。

**输出示例**:
由于该函数的返回值是布尔类型，所以在成功执行删除操作后，它会返回 `True`。例如：
```
操作成功完成后返回值: True
```
## FunctionDef file_exists_in_db(session, kb_file)
**file_exists_in_db**: 该函数用于检查指定的文件是否已存在于数据库中。

**参数**:
- `session`: 数据库会话实例，用于执行数据库查询。
- `kb_file`: `KnowledgeFile` 类型的对象，表示要检查的知识库文件。

**代码描述**:
`file_exists_in_db` 函数通过接收一个数据库会话 (`session`) 和一个 `KnowledgeFile` 对象 (`kb_file`) 作为参数，来检查指定的文件是否已经存在于数据库中。它首先使用 `session.query` 方法构造一个查询，该查询针对 `KnowledgeFileModel` 表进行，通过 `filter` 方法筛选出文件名 (`file_name`) 和知识库名称 (`kb_name`) 与传入的 `kb_file` 对象相匹配的记录。这里使用了 `ilike` 方法来进行不区分大小写的匹配。如果查询的结果中存在至少一条记录，即 `first()` 方法返回非空值，则认为文件已存在于数据库中，函数返回 `True`；否则，返回 `False`。

**注意**:
- 确保传入的 `session` 参数是一个有效的数据库会话实例，且已正确配置数据库连接。
- 传入的 `kb_file` 对象应包含有效的 `filename` 和 `kb_name` 属性，这两个属性将用于数据库查询中的匹配条件。
- 该函数不对数据库进行任何修改操作，仅用于检查文件的存在性。

**输出示例**:
假设数据库中已存在文件名为 "example.pdf"，知识库名称为 "DefaultKB" 的记录，当传入一个 `kb_file` 对象，其 `filename` 属性值为 "example.pdf"，`kb_name` 属性值为 "DefaultKB" 时，函数将返回 `True`。如果数据库中不存在满足条件的记录，函数将返回 `False`。
## FunctionDef get_file_detail(session, kb_name, filename)
**get_file_detail**: 此函数用于获取指定知识库中特定文件的详细信息。

**参数**:
- `session`: 数据库会话实例，用于执行数据库查询。
- `kb_name`: 字符串类型，指定要查询的知识库名称。
- `filename`: 字符串类型，指定要查询的文件名。

**代码描述**:
`get_file_detail`函数首先通过传入的`session`参数，使用SQLAlchemy的查询接口，根据`kb_name`（知识库名称）和`filename`（文件名）作为过滤条件，查询`KnowledgeFileModel`模型。查询条件使用了`ilike`方法，这意味着查询是大小写不敏感的，提高了查询的灵活性。如果查询到了指定的文件，函数将从查询结果中提取文件的详细信息，并以字典形式返回。这些信息包括知识库名称、文件名、文件扩展名、文件版本、文档加载器名称、文本分割器名称、创建时间、文件的最后修改时间、文件大小、是否为自定义文档、文档数量等。如果没有查询到指定的文件，函数将返回一个空字典。

**注意**:
- 在使用此函数时，需要确保传入的`session`是一个有效的数据库会话实例。
- 查询条件`kb_name`和`filename`是大小写不敏感的，这意味着无论传入的是大写还是小写，都可以正确查询到结果。
- 返回的字典中包含了文件的多个属性，这些属性的值直接来源于数据库中的记录，因此在使用这些值时应注意它们的数据类型和含义。

**输出示例**:
```json
{
  "kb_name": "SampleKB",
  "file_name": "example.pdf",
  "file_ext": ".pdf",
  "file_version": 1,
  "document_loader": "PDFLoader",
  "text_splitter": "SpacyTextSplitter",
  "create_time": "2023-04-01 12:00:00",
  "file_mtime": 1617184000,
  "file_size": 1024,
  "custom_docs": false,
  "docs_count": 10
}
```
此示例展示了当查询到文件时，`get_file_detail`函数返回的信息字典。包含了文件所属的知识库名称、文件名、文件扩展名、文件版本、文档加载器名称、文本分割器名称、文件的创建时间、最后修改时间、文件大小、是否为自定义文档以及文档数量等信息。
