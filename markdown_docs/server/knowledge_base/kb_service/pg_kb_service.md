## ClassDef PGKBService
**PGKBService**: PGKBService 类是用于通过 PostgreSQL 实现知识库服务的具体类。

**属性**:
- `engine`: 通过 SQLAlchemy 创建的连接引擎，用于与 PostgreSQL 数据库进行交互。
- `pg_vector`: 用于存储和检索嵌入向量的 PGVector 实例。

**代码描述**:
PGKBService 类继承自 KBService 类，提供了与 PostgreSQL 数据库交互的具体实现。它使用 SQLAlchemy 作为 ORM 工具，通过 `engine` 属性与数据库建立连接。此类主要负责初始化向量存储、文档的增删查改、知识库的创建和删除等操作。

- `_load_pg_vector` 方法用于加载 PGVector 实例，该实例负责嵌入向量的存储和检索。
- `get_doc_by_ids` 方法通过文档 ID 获取文档内容和元数据。
- `del_doc_by_ids` 方法删除指定 ID 的文档，实际调用基类的同名方法。
- `do_init` 方法在类初始化时被调用，用于加载 PGVector 实例。
- `do_create_kb` 方法是创建知识库的具体实现，当前为空实现。
- `vs_type` 方法返回支持的向量存储类型，即 PostgreSQL。
- `do_drop_kb` 方法删除知识库，包括数据库中的相关记录和文件系统上的知识库路径。
- `do_search` 方法实现了基于查询的文档搜索功能，返回与查询最相关的文档列表。
- `do_add_doc` 方法向知识库添加文档，并返回添加的文档信息。
- `do_delete_doc` 方法从知识库删除指定的文档。
- `do_clear_vs` 方法清空向量存储中的所有内容，并重新创建集合。

**注意**:
- 使用 PGKBService 类之前，需要确保 PostgreSQL 数据库已经正确配置，并且 `kbs_config` 中的 `pg` 配置项包含了正确的数据库连接 URI。
- 在调用 `do_add_doc` 和 `do_delete_doc` 等方法修改数据库内容时，需要确保传入的参数符合预期格式，以避免执行错误或数据损坏。
- `do_drop_kb` 方法在删除知识库时会同时删除数据库中的记录和文件系统上的知识库路径，使用时需谨慎以防误删重要数据。

**输出示例**:
```python
# 假设调用 get_doc_by_ids 方法查询 ID 为 ['doc1', 'doc2'] 的文档
docs = pgkb_service.get_doc_by_ids(['doc1', 'doc2'])
# 可能的返回值为
[
    Document(page_content="文档1的内容", metadata={"author": "作者1"}),
    Document(page_content="文档2的内容", metadata={"author": "作者2"})
]
```
此示例展示了通过文档 ID 获取文档内容和元数据的过程及其可能的返回值。
### FunctionDef _load_pg_vector(self)
**_load_pg_vector**: 此函数的功能是加载PostgreSQL向量空间搜索引擎。

**参数**: 此函数没有显式参数，但它依赖于类实例的多个属性。

**代码描述**: `_load_pg_vector`函数负责初始化一个PGVector实例，该实例用于在PostgreSQL数据库中进行向量空间搜索。这个过程包括以下几个关键步骤：

1. 使用`EmbeddingsFunAdapter`类创建一个嵌入函数适配器。这个适配器基于类实例的`embed_model`属性，用于将文本转换为向量表示。`EmbeddingsFunAdapter`支持同步和异步两种文本嵌入方式，适用于不同的应用场景。

2. 指定向量空间搜索的集合名称，这里使用类实例的`kb_name`属性作为集合名称。

3. 设置距离策略为欧几里得距离（`DistanceStrategy.EUCLIDEAN`），用于计算向量之间的距离。

4. 使用`PGKBService.engine`作为数据库连接。这是一个类属性，表示与PostgreSQL数据库的连接引擎。

5. 通过`kbs_config.get("pg").get("connection_uri")`获取数据库连接字符串，这个字符串包含了数据库的地址、端口、用户名、密码等信息，用于建立数据库连接。

通过这些步骤，`_load_pg_vector`函数配置了一个用于向量空间搜索的PGVector实例，并将其保存在类实例的`pg_vector`属性中。这使得类的其他方法可以利用这个PGVector实例来执行向量空间搜索操作，例如查找与给定文本向量最相似的文档。

**注意**:
- 在调用`_load_pg_vector`函数之前，需要确保类实例的`embed_model`和`kb_name`属性已经被正确设置。这些属性对于初始化PGVector实例至关重要。
- `PGKBService.engine`需要预先配置好，确保能够成功连接到PostgreSQL数据库。
- 数据库连接字符串应该保密处理，避免泄露数据库的敏感信息。

此函数是在`do_init`方法中被调用的，`do_init`方法负责执行类的初始化操作，包括加载PostgreSQL向量空间搜索引擎。这表明`_load_pg_vector`函数是类初始化过程的一个重要组成部分，确保了向量空间搜索功能的可用性。
***
### FunctionDef get_doc_by_ids(self, ids)
**get_doc_by_ids**: 此函数的功能是根据提供的ID列表查询并返回相应的文档列表。

**参数**:
- ids: 一个字符串列表，包含需要查询的文档的ID。

**代码描述**:
`get_doc_by_ids` 函数接受一个字符串列表 `ids` 作为参数，这个列表包含了需要查询的文档的ID。函数内部首先使用 `Session` 上下文管理器创建一个会话，通过这个会话与数据库进行交互。接着，定义了一个SQL查询语句 `stmt`，这个语句用于从名为 `langchain_pg_embedding` 的表中选取 `document` 和 `cmetadata` 字段，条件是 `collection_id` 字段的值包含在参数 `ids` 提供的ID列表中。

通过执行这个查询语句并传入 `ids` 参数，函数会从数据库中检索出匹配的记录。每条记录都会被用来创建一个 `Document` 对象，这个对象包含了检索到的文档内容（`page_content`）和元数据（`metadata`）。所有这些 `Document` 对象随后被收集到一个列表中，并作为函数的返回值。

**注意**:
- 确保传入的ID列表 `ids` 不为空，且每个ID都是有效的，以确保查询能够正确执行。
- 此函数依赖于数据库表 `langchain_pg_embedding` 的结构，特别是它查询的字段。如果数据库结构发生变化，可能需要相应地更新此函数。

**输出示例**:
假设数据库中有两条记录的 `collection_id` 匹配给定的ID列表，函数可能返回如下的列表：
```python
[
    Document(page_content="文档内容1", metadata={"作者": "张三", "发布日期": "2023-01-01"}),
    Document(page_content="文档内容2", metadata={"作者": "李四", "发布日期": "2023-02-01"})
]
```
这个列表包含了两个 `Document` 对象，每个对象都包含了从数据库检索到的文档内容和元数据。
***
### FunctionDef del_doc_by_ids(self, ids)
**del_doc_by_ids**: 此函数的功能是根据提供的ID列表删除文档。

**参数**:
- ids: 一个字符串列表，包含要删除的文档的ID。

**代码描述**:
`del_doc_by_ids` 函数接受一个字符串列表 `ids` 作为参数，这个列表包含了需要从数据库中删除的文档的ID。函数通过调用其父类的 `del_doc_by_ids` 方法来实现删除操作，并将 `ids` 参数传递给该方法。这表明实际的删除逻辑被封装在父类的方法中，而当前函数主要负责将删除请求转发给父类处理。

**注意**:
- 确保传递给此函数的 `ids` 参数包含有效的文档ID，否则可能不会有任何文档被删除。
- 此函数返回一个布尔值，表示删除操作是否成功。但是，具体的成功与否依赖于父类方法的实现细节。
- 在使用此函数之前，应当了解父类中 `del_doc_by_ids` 方法的具体实现，以及它对于不同情况下删除操作的处理方式。

**输出示例**:
调用 `del_doc_by_ids(['doc1', 'doc2'])` 可能会返回 `True`，表示指定ID的文档已成功删除。如果操作失败，可能会返回 `False`。请注意，实际的返回值取决于父类方法的具体实现。
***
### FunctionDef do_init(self)
**do_init**: 此函数的功能是初始化PGKBService类的实例。

**参数**: 此函数没有参数。

**代码描述**: `do_init`方法是PGKBService类的一个初始化方法，它通过调用`_load_pg_vector`方法来加载PostgreSQL向量空间搜索引擎。这个过程是类实例化过程中的一个重要步骤，确保了类的实例能够正确地进行向量空间搜索操作。

在`do_init`方法中，通过调用`_load_pg_vector`方法，完成了以下几个关键的初始化步骤：
1. 创建一个嵌入函数适配器`EmbeddingsFunAdapter`，该适配器基于类实例的`embed_model`属性，用于将文本转换为向量表示。
2. 指定向量空间搜索的集合名称，使用类实例的`kb_name`属性作为集合名称。
3. 设置距离策略为欧几里得距离，用于计算向量之间的距离。
4. 使用类属性`PGKBService.engine`作为数据库连接，这表示与PostgreSQL数据库的连接引擎。
5. 获取数据库连接字符串，用于建立数据库连接。

通过这些步骤，`_load_pg_vector`方法配置了一个用于向量空间搜索的PGVector实例，并将其保存在类实例的`pg_vector`属性中。这样，类的其他方法就可以利用这个PGVector实例来执行向量空间搜索操作，例如查找与给定文本向量最相似的文档。

**注意**:
- 在调用`do_init`方法之前，不需要进行特别的准备工作，因为它是类实例化过程中自动调用的初始化方法。
- 需要确保`embed_model`和`kb_name`属性在调用`_load_pg_vector`之前已经被正确设置，因为这些属性对于初始化PGVector实例至关重要。
- `PGKBService.engine`需要预先配置好，以确保能够成功连接到PostgreSQL数据库。
- 数据库连接字符串应该保密处理，避免泄露数据库的敏感信息。

总的来说，`do_init`方法通过调用`_load_pg_vector`方法，完成了PGKBService类实例的初始化，为后续的向量空间搜索操作做好了准备。
***
### FunctionDef do_create_kb(self)
**do_create_kb**: 此函数的功能是创建知识库。

**参数**: 此函数没有参数。

**代码描述**: `do_create_kb` 函数是 `PGKBService` 类的一个方法，负责创建知识库的具体逻辑。目前，此函数的实现为空（使用了 `pass` 语句），这意味着它不执行任何操作。在实际应用中，开发者需要在此函数中添加创建知识库的代码逻辑，例如连接数据库、执行数据库操作等。

**注意**: 虽然当前 `do_create_kb` 函数的实现为空，但在将来的开发中，当添加具体的实现逻辑时，需要确保数据库连接的正确性和操作的安全性。此外，考虑到知识库可能包含大量数据，还需要注意性能优化和错误处理。
***
### FunctionDef vs_type(self)
**vs_type**: vs_type函数的功能是返回当前知识库服务支持的向量存储类型。

**参数**: 该函数不接受任何参数。

**代码描述**: vs_type函数是PGKBService类的一个方法，它的主要作用是标识该知识库服务实例支持的向量存储类型。在这个具体实现中，vs_type方法通过返回SupportedVSType.PG，明确指出PostgreSQL（简称PG）是该服务实例使用的向量存储类型。SupportedVSType是一个枚举类，它定义了项目中支持的所有向量存储类型，包括但不限于FAISS、MILVUS、ZILLIZ、Elasticsearch（ES）、ChromaDB等，以及PG。通过返回SupportedVSType中的一个枚举值，vs_type方法为知识库服务的配置和实例化提供了必要的信息。这种设计使得知识库服务的管理和扩展更加灵活和方便，因为可以根据需要动态选择和切换不同的向量存储服务。

**注意**:
- 在使用PGKBService类及其vs_type方法时，应当了解SupportedVSType枚举类中定义的向量存储类型，以确保正确理解和使用该方法返回的向量存储类型信息。
- 由于vs_type方法返回的是一个枚举成员，因此在处理返回值时，应当注意枚举类型的使用方法，例如通过枚举成员的name或value属性获取具体的信息。

**输出示例**: 假设调用PGKBService实例的vs_type方法，可能的返回值为：
```
'pg'
```
这表示当前知识库服务实例使用PostgreSQL作为其向量存储服务。
***
### FunctionDef do_drop_kb(self)
**do_drop_kb**: 此函数的功能是删除与指定知识库名称相关联的数据库记录和文件系统中的知识库目录。

**参数**: 此函数没有显式参数，但它依赖于`self.kb_name`和`self.kb_path`这两个实例变量。

**代码描述**:
`do_drop_kb`函数是`PGKBService`类的一个方法，用于删除特定知识库相关的数据。该方法首先通过SQL语句删除数据库中与知识库相关联的记录，然后删除文件系统中对应的知识库目录。具体步骤如下：

1. 使用`Session`上下文管理器创建一个数据库会话，确保数据库操作在一个会话中完成，并且在操作结束后自动关闭会话。
2. 在会话中执行SQL删除操作。首先，删除`langchain_pg_embedding`表中所有`collection_id`与`langchain_pg_collection`表中`name`字段匹配`self.kb_name`的记录的`uuid`相匹配的记录。这意味着，所有与指定知识库名称相关联的嵌入信息将被删除。
3. 接着，删除`langchain_pg_collection`表中`name`字段与`self.kb_name`匹配的记录。这一步骤将删除知识库的集合记录。
4. 执行`session.commit()`提交数据库事务，确保上述删除操作被保存到数据库中。
5. 使用`shutil.rmtree`函数删除文件系统中的知识库目录。`self.kb_path`变量指定了知识库目录的路径，该函数将递归删除该目录及其所有内容。

**注意**:
- 在执行此函数之前，确保`self.kb_name`和`self.kb_path`已经正确设置，分别指向要删除的知识库的名称和路径。
- 该操作不可逆，一旦执行，相关的数据库记录和文件系统中的目录将被永久删除。因此，在调用此函数之前，请确保已经做好相应的备份或确认不再需要这些数据。
- 由于直接操作数据库和文件系统，确保执行此操作的用户具有相应的权限。
***
### FunctionDef do_search(self, query, top_k, score_threshold)
**do_search**: 此函数的功能是执行文本查询，并根据给定的分数阈值和返回的文档数量上限筛选出相似度最高的文档。

**参数**:
- `query`: 需要查询的文本，数据类型为字符串。
- `top_k`: 返回的文档数量上限，数据类型为整数。
- `score_threshold`: 分数阈值，用于筛选相似度高于此阈值的文档，数据类型为浮点数。

**代码描述**:
`do_search`函数首先通过`EmbeddingsFunAdapter`类的实例`embed_func`，调用`embed_query`方法将查询文本`query`转换为嵌入向量。这一步骤是通过将文本转换为向量化表示，以便后续进行相似度搜索。

接着，函数使用`self.pg_vector`的`similarity_search_with_score_by_vector`方法，传入上一步得到的嵌入向量和`top_k`参数，执行相似度搜索。此方法返回一个包含文档及其相似度分数的列表，列表中的文档是根据与查询向量的相似度排序的。

最后，函数调用`score_threshold_process`方法，传入`score_threshold`、`top_k`和相似度搜索的结果，根据分数阈值筛选出符合条件的文档，并返回前`top_k`个文档。这一步骤确保了返回的文档不仅与查询文本相似度高，而且其相似度分数超过了指定的阈值。

**注意**:
- 确保传入的`query`是有效的字符串，`top_k`是正整数，`score_threshold`是非负浮点数。
- `EmbeddingsFunAdapter`和`score_threshold_process`是此函数依赖的关键组件，确保它们的实现与预期一致。
- 此函数的性能和准确性依赖于嵌入模型的质量和相似度搜索算法的效率。

**输出示例**:
假设调用`do_search`函数，传入查询文本"示例查询"，`top_k`为3，`score_threshold`为0.5，可能的返回值为：
```
[("文档1", 0.8), ("文档3", 0.7), ("文档5", 0.6)]
```
这表示在所有文档中，有三个文档的相似度分数满足大于等于0.5的条件，并且是相似度最高的前三个文档。
***
### FunctionDef do_add_doc(self, docs)
**do_add_doc**: 此函数的功能是向数据库中添加文档，并返回包含文档ID和元数据的信息列表。

**参数**:
- `docs`: 需要添加到数据库中的文档列表，每个文档都是一个`Document`对象。
- `**kwargs`: 接受可变数量的关键字参数，这些参数可以根据需要传递给底层数据库操作。

**代码描述**:
`do_add_doc`函数首先调用`pg_vector`对象的`add_documents`方法，将`docs`列表中的文档添加到数据库中。`add_documents`方法返回一个包含每个文档ID的列表。然后，函数遍历这些ID和原始的`docs`列表，使用列表推导式创建一个新的列表`doc_infos`。这个新列表的每个元素都是一个字典，包含两个键：`id`和`metadata`。`id`键对应于文档的ID，`metadata`键对应于文档的元数据。最后，函数返回`doc_infos`列表。

**注意**:
- 确保传递给`do_add_doc`函数的`docs`参数是一个`Document`对象的列表，且每个`Document`对象都应该有有效的元数据。
- 传递给`**kwargs`的关键字参数将直接影响底层数据库操作，因此请谨慎使用，确保了解这些参数的影响。

**输出示例**:
假设我们向`do_add_doc`函数传递了两个文档，且这两个文档成功添加到数据库中，函数可能返回如下列表：
```python
[
    {"id": "doc1_id", "metadata": {"title": "Document 1 Title", "author": "Author Name"}},
    {"id": "doc2_id", "metadata": {"title": "Document 2 Title", "author": "Another Author Name"}}
]
```
这个列表包含了每个文档的ID和元数据，可以用于进一步的处理或显示。
***
### FunctionDef do_delete_doc(self, kb_file)
**do_delete_doc**: 此函数用于从数据库中删除与指定知识文件相关联的文档向量。

**参数**:
- `kb_file`: KnowledgeFile对象，代表需要删除其文档向量的知识库文件。
- `**kwargs`: 接收额外的关键字参数，以便在未来的版本中扩展功能而不影响现有接口。

**代码描述**:
`do_delete_doc`函数首先通过`kb_file`参数获取知识库文件的完整路径。为了确保数据库查询语句中的文件路径字符串格式正确，它将路径中的所有反斜杠(`\`)替换为双反斜杠(`\\`)。这是因为在SQL查询中，反斜杠是一个特殊字符，需要进行转义。

接着，函数使用`Session`上下文管理器创建一个数据库会话，并执行一个SQL `DELETE`语句。这个`DELETE`语句的目的是从`langchain_pg_embedding`表中删除所有`cmetadata`字段（以JSONB格式存储）中`source`键对应的值与给定文件路径匹配的记录。这里，`cmetadata::jsonb @> '{"source": "filepath"}'::jsonb`是一个PostgreSQL的JSONB查询表达式，用于查找`cmetadata`中包含特定`source`键值对的记录。

在执行删除操作后，函数通过`session.commit()`提交更改，确保删除操作被保存到数据库中。

**注意**:
- 使用此函数时，需要确保传入的`kb_file`对象有效，且其`filepath`属性正确反映了文件在磁盘上的位置。
- 此函数直接操作数据库，执行删除操作。因此，在调用此函数之前，应确保已经对要删除的数据进行了适当的备份或确认，以防意外数据丢失。
- 由于此函数涉及数据库操作，其执行效率和影响范围可能会受到数据库当前状态和配置的影响。在处理大量数据或高负载情况下，建议监控数据库性能，以避免潜在的性能问题。
***
### FunctionDef do_clear_vs(self)
**do_clear_vs**: 此函数的功能是清除并重新创建向量空间。

**参数**: 此函数不接受任何参数。

**代码描述**: `do_clear_vs` 函数是 `PGKBService` 类的一个方法，用于管理向量空间的清除和重建过程。在这个函数中，首先调用 `self.pg_vector.delete_collection()` 方法来删除当前的向量空间集合。这一步骤是为了清除所有现有的数据，确保向量空间是空的。紧接着，通过调用 `self.pg_vector.create_collection()` 方法来重新创建一个新的向量空间集合。这样做的目的是为了在删除旧数据之后，提供一个全新的环境以便后续的数据插入和管理。

**注意**: 使用 `do_clear_vs` 函数时需要谨慎，因为这会导致所有现有的向量空间数据被永久删除，无法恢复。因此，在执行此操作之前，请确保已经做好了充分的数据备份或确认不再需要这些数据。此外，重新创建向量空间集合后，需要重新配置任何相关的设置或索引，以确保向量空间的正常使用和性能优化。
***
