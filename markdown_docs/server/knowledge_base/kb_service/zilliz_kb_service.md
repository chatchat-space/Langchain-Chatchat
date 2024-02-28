## ClassDef ZillizKBService
**ZillizKBService**: ZillizKBService 类是用于在 Zilliz 向量数据库中管理和操作知识库的服务。

**属性**:
- `zilliz`: Zilliz 实例，用于与 Zilliz 向量数据库进行交互。

**代码描述**:
ZillizKBService 类继承自 KBService 类，提供了一系列专门用于在 Zilliz 向量数据库中管理和操作知识库的方法。这些方法包括获取集合、通过 ID 获取文档、通过 ID 删除文档、搜索、创建知识库、初始化、删除知识库、添加文档、删除文档以及清除向量空间等。

- `get_collection` 静态方法用于获取指定名称的集合。
- `get_doc_by_ids` 方法根据提供的 ID 列表查询并返回文档列表。
- `del_doc_by_ids` 方法根据提供的 ID 列表删除文档。
- `search` 静态方法用于在指定的集合中搜索与给定内容相似的文档。
- `do_create_kb` 方法用于创建知识库，当前为空实现。
- `vs_type` 方法返回支持的向量存储类型，即 Zilliz。
- `_load_zilliz` 方法用于加载 Zilliz 实例。
- `do_init` 方法用于初始化服务，包括加载 Zilliz 实例。
- `do_drop_kb` 方法用于删除知识库。
- `do_search` 方法用于搜索知识库。
- `do_add_doc` 方法用于向知识库添加文档。
- `do_delete_doc` 方法用于从知识库删除指定的文档。
- `do_clear_vs` 方法用于清除向量空间。

**注意**:
- 在使用 ZillizKBService 之前，需要确保 Zilliz 向量数据库已正确配置并可用。
- 由于 ZillizKBService 继承自 KBService，部分方法的具体实现可能依赖于 KBService 类中定义的抽象方法。
- 在调用 `do_add_doc` 和 `do_delete_doc` 等方法时，需要注意传入的参数格式和类型。

**输出示例**:
```python
# 假设已经有一个 ZillizKBService 实例，名为 zilliz_service
# 搜索内容为 "example content" 的文档，限制返回结果为前3个
search_results = zilliz_service.search("example_collection", "example content", limit=3)
# 输出可能为：
[
    {"content": "文档1内容", "score": 0.95},
    {"content": "文档2内容", "score": 0.90},
    {"content": "文档3内容", "score": 0.85}
]
```
此输出示例展示了使用 `search` 方法进行内容搜索的可能结果，包括每个匹配文档的内容和相似度得分。
### FunctionDef get_collection(zilliz_name)
**get_collection**: 此函数的功能是获取指定名称的集合。

**参数**:
- **zilliz_name**: 集合的名称。

**代码描述**:
`get_collection` 函数是`ZillizKBService`类中的一个方法，它的主要作用是通过传入的集合名称`zilliz_name`，使用`pymilvus`库中的`Collection`类来获取对应的集合对象。这个方法简洁明了，只涉及到从`pymilvus`导入`Collection`类并返回一个集合对象的过程。

在项目中，`get_collection`方法被`search`方法调用。在`search`方法中，首先通过`get_collection`获取到了一个指定名称的集合对象，然后使用这个集合对象执行搜索操作。这表明`get_collection`方法是搜索功能实现的基础，它确保了搜索操作能够在正确的集合上执行。

**注意**:
- 确保在调用此函数之前，指定的集合名称`zilliz_name`已经存在于Milvus数据库中，否则会导致获取集合失败。
- 使用此函数需要安装并正确配置`pymilvus`库。

**输出示例**:
调用`get_collection("example_collection")`可能会返回一个`pymilvus`库中的`Collection`对象，这个对象代表了名为"example_collection"的集合。
***
### FunctionDef get_doc_by_ids(self, ids)
**get_doc_by_ids**: 此函数的功能是根据提供的ID列表从Zilliz的集合中检索文档。

**参数**:
- `ids`: 一个字符串列表，包含要检索的文档的ID。

**代码描述**:
`get_doc_by_ids`函数接受一个ID列表作为参数，返回一个文档列表。这个函数首先检查`self.zilliz.col`是否存在，这是一个对Zilliz集合的引用。如果这个集合存在，函数将继续执行查询操作。

查询是通过调用`self.zilliz.col.query`方法实现的，该方法的`expr`参数设置为`'pk in {ids}'`，其中`{ids}`是传入的ID列表。这意味着函数将查询主键（pk）在给定ID列表中的所有记录。`output_fields=["*"]`参数指示查询返回所有字段的数据。

对于查询结果中的每条数据，函数将从数据中提取`text`字段，并将其余字段作为元数据。然后，它使用这些信息创建一个`Document`对象，其中`page_content`设置为提取的文本，`metadata`设置为剩余的数据字段。这些`Document`对象被收集到一个列表中，最后返回这个列表。

**注意**:
- 确保传入的ID列表中的ID是存在于Zilliz集合中的有效ID，否则查询将不会返回任何结果。
- 此函数依赖于`self.zilliz.col`的存在，这意味着在调用此函数之前，必须正确初始化并设置对应的Zilliz集合引用。

**输出示例**:
假设有两个文档的ID分别为"123"和"456"，并且这些文档在Zilliz集合中存在。调用`get_doc_by_ids(['123', '456'])`可能会返回如下列表：

```python
[
    Document(page_content="这是文档123的内容", metadata={'id': '123', 'title': '文档123标题', 'date': '2023-01-01'}),
    Document(page_content="这是文档456的内容", metadata={'id': '456', 'title': '文档456标题', 'date': '2023-01-02'})
]
```

这个列表包含两个`Document`对象，每个对象都包含了从Zilliz集合中检索到的文档的内容和元数据。
***
### FunctionDef del_doc_by_ids(self, ids)
**del_doc_by_ids**: 此函数的功能是根据提供的ID列表删除对应的文档。

**参数**:
- ids: 一个字符串列表，包含需要删除的文档的ID。

**代码描述**:
`del_doc_by_ids`函数是`ZillizKBService`类的一个方法，用于从Zilliz的知识库服务中删除指定ID的文档。此函数接受一个参数`ids`，这是一个字符串列表，每个字符串代表一个需要删除的文档的ID。函数内部，通过调用`self.zilliz.col.delete`方法来执行删除操作，其中`expr=f'pk in {ids}'`是一个表达式，用于指定需要删除的文档的ID条件。这里`pk`代表文档的主键，`in {ids}`表示主键在提供的ID列表中的文档将被删除。

**注意**:
- 确保传入的ID列表中的每个ID都是有效的，并且对应于知识库中实际存在的文档。如果列表中包含无效或不存在的ID，这些ID将被忽略，不会影响其他有效ID的删除操作。
- 删除操作一旦执行，被删除的文档将无法恢复，请在执行删除操作前仔细确认。
- 此函数返回一个布尔值，表示删除操作是否成功执行。然而，具体的代码实现中没有明确返回值，这可能需要根据实际的业务逻辑进行相应的调整或补充。
***
### FunctionDef search(zilliz_name, content, limit)
**search**: 此函数的功能是在指定的集合中执行基于内容的搜索操作。

**参数**:
- **zilliz_name**: 指定的集合名称。
- **content**: 搜索的内容。
- **limit**: 返回的结果数量上限，默认值为3。

**代码描述**:
`search` 函数是`ZillizKBService`类中的一个方法，它用于在指定的集合中执行基于内容的搜索操作。首先，该函数定义了搜索参数`search_params`，其中包括度量类型（"IP"）和其他搜索相关的参数。接着，通过调用`get_collection`方法获取到指定名称的集合对象。最后，使用集合对象的`search`方法执行搜索操作，该操作基于`content`参数进行，搜索范围限定在"embeddings"字段中，同时指定了搜索参数`search_params`和结果数量上限`limit`。此外，还通过`output_fields`参数指定了搜索结果中需要包含的字段，本例中为["content"]。

从功能角度看，`get_collection`方法为`search`方法提供了执行搜索所需的集合对象，确保搜索操作能够在正确的集合上进行。这种设计体现了模块化和功能分离的原则，便于代码的维护和扩展。

**注意**:
- 在使用`search`函数之前，确保`zilliz_name`指定的集合已经存在，并且集合中的数据已经按照需要进行了索引。
- `limit`参数应根据实际需求调整，以平衡搜索结果的全面性和性能开销。
- 确保`pymilvus`库已正确安装并配置，因为`search`函数的实现依赖于此库。

**输出示例**:
调用`search("example_collection", "some search content")`可能会返回如下格式的搜索结果：
```python
[
    {"content": "匹配的内容1"},
    {"content": "匹配的内容2"},
    {"content": "匹配的内容3"}
]
```
这个示例展示了当搜索限制为返回最多3个结果时，可能得到的搜索结果。每个结果包含了指定的输出字段"content"，其中包含了与搜索内容匹配的集合中的数据。
***
### FunctionDef do_create_kb(self)
**do_create_kb**: 此函数的功能是创建知识库。

**参数**: 此函数没有参数。

**代码描述**: `do_create_kb` 函数是 `ZillizKBService` 类的一个方法，用于创建知识库。在当前的代码实现中，此函数体内没有具体的执行代码，仅包含一个 `pass` 语句。这意味着，此函数作为一个框架或者是占位符存在，等待后续的实现。在实际应用中，开发者需要根据具体需求，填充此函数以实现知识库的创建逻辑，比如初始化数据库连接、设置知识库的结构、数据导入等操作。

**注意**: 虽然当前 `do_create_kb` 函数没有实现具体的功能，但在将来的版本中，开发者可能会添加具体的实现代码。因此，在使用此函数时，需要关注其最新的实现状态和文档说明，以确保正确使用。同时，考虑到此函数的目的是创建知识库，开发者在实现时应确保有充分的权限和正确的配置信息，以避免潜在的权限问题或配置错误。
***
### FunctionDef vs_type(self)
**vs_type**: vs_type函数的功能是返回当前知识库服务支持的向量存储类型。

**参数**: 此函数没有参数。

**代码描述**: vs_type函数是ZillizKBService类的一个方法，它的作用是标识该知识库服务实例支持的向量存储类型。在这个具体实现中，vs_type方法通过返回SupportedVSType.ZILLIZ来明确指出，当前的知识库服务使用的是ZILLIZ作为其向量存储解决方案。SupportedVSType是一个枚举类，其中定义了项目支持的所有向量存储类型，包括但不限于FAISS、MILVUS、ZILLIZ等。ZILLIZ在这里被选定，意味着ZillizKBService专门为与ZILLIZ向量存储服务交互而设计。这种设计方式便于在知识库服务工厂（KBServiceFactory）中根据需要动态选择和实例化具体的知识库服务实现，从而提高了项目的灵活性和可扩展性。

**注意**: 
- 在使用ZillizKBService类时，开发者应当了解其背后的向量存储类型是ZILLIZ，这对于理解如何配置和使用该服务至关重要。
- 如果项目需要支持其他类型的向量存储服务，应在SupportedVSType枚举类中添加相应的类型，并在知识库服务工厂中实现相应的逻辑以支持新的服务类型。

**输出示例**: 该函数调用将返回一个字符串值："zilliz"。
***
### FunctionDef _load_zilliz(self)
**_load_zilliz**: 此函数的功能是加载Zilliz服务。

**参数**: 此函数没有显式参数，它通过类实例访问成员变量。

**代码描述**: `_load_zilliz`函数首先从配置中获取名为`zilliz`的参数，这些参数用于配置Zilliz服务的连接。然后，它创建一个`Zilliz`实例，该实例负责处理嵌入向量的存储和搜索。在创建`Zilliz`实例时，它使用`EmbeddingsFunAdapter`类将当前对象的`embed_model`属性作为嵌入函数传递给`Zilliz`。`EmbeddingsFunAdapter`是一个适配器类，用于将文本转换为嵌入向量，支持同步和异步两种方式。此外，`Zilliz`实例还接收知识库的名称(`kb_name`)和连接参数(`zilliz_args`)。这意味着，每当需要初始化或执行搜索操作时，都会通过`Zilliz`实例与Zilliz服务进行交互，以便处理嵌入向量的存储和相似度搜索。

**注意**: 
- 在调用`_load_zilliz`函数之前，需要确保`kbs_config`中已经正确配置了`zilliz`参数，包括Zilliz服务的连接信息。
- `EmbeddingsFunAdapter`类的使用依赖于有效的嵌入模型名称(`embed_model`)，该名称应指向一个预先训练好的模型，用于文本嵌入转换。
- `_load_zilliz`函数通常在知识库服务的初始化(`do_init`)和搜索(`do_search`)过程中被调用，以确保Zilliz服务的连接和配置在进行操作前已经就绪。

通过这种方式，`_load_zilliz`函数为知识库服务提供了一个核心功能，即配置和初始化与Zilliz服务的连接，这对于后续的文本嵌入存储和相似度搜索操作至关重要。
***
### FunctionDef do_init(self)
**do_init**: 此函数的功能是初始化Zilliz知识库服务。

**参数**: 此函数没有显式参数。

**代码描述**: `do_init`函数是`ZillizKBService`类的一个方法，用于初始化Zilliz知识库服务。它通过调用`_load_zilliz`方法来加载和配置Zilliz服务。`_load_zilliz`方法负责创建一个Zilliz实例，这个实例用于处理嵌入向量的存储和搜索。这一过程包括从配置中获取Zilliz服务的连接参数，以及使用`EmbeddingsFunAdapter`类将当前对象的`embed_model`属性作为嵌入函数传递给Zilliz实例。这确保了Zilliz服务能够根据预先训练好的模型将文本转换为嵌入向量，并进行存储和相似度搜索操作。

**注意**:
- 在调用`do_init`方法之前，应确保已经在`kbs_config`中正确配置了Zilliz服务的连接信息。
- `do_init`方法通常在知识库服务需要重新初始化时调用，例如在`do_clear_vs`方法中，如果检测到知识库集合已存在，则会先删除现有集合，然后通过调用`do_init`来重新初始化Zilliz服务。
- 此方法的成功执行对于后续的知识库操作（如文本嵌入存储和相似度搜索）是必要的，因为它确保了Zilliz服务的连接和配置已经就绪。

通过`do_init`方法，`ZillizKBService`类能够确保Zilliz知识库服务的正确初始化和配置，为后续的操作提供了基础。
***
### FunctionDef do_drop_kb(self)
**do_drop_kb**: 此函数的功能是释放并删除当前的知识库集合。

**参数**: 此函数不接受任何参数。

**代码描述**: `do_drop_kb` 函数是`ZillizKBService`类的一个方法，用于处理知识库集合的释放和删除操作。当`ZillizKBService`实例中的`zilliz.col`属性存在时，此方法首先调用`release`方法来释放集合，随后调用`drop`方法来删除集合。这个过程确保了知识库的集合被正确地清理，避免了资源泄露或是不必要的存储占用。

在项目中，`do_drop_kb`方法被`do_clear_vs`方法调用。`do_clear_vs`方法的目的是清理视图状态，在清理过程中，它首先调用`do_drop_kb`来释放并删除知识库集合，然后通过调用`do_init`方法重新初始化状态。这表明`do_drop_kb`在知识库管理流程中扮演着重要的角色，确保了知识库的集合在不再需要时能够被正确地处理。

**注意**: 使用`do_drop_kb`方法时，需要确保`zilliz.col`属性已经正确初始化，并且在调用此方法后，相关的集合资源将被释放和删除。因此，在调用此方法之前，应当确保不再需要对该集合进行任何操作。
***
### FunctionDef do_search(self, query, top_k, score_threshold)
**do_search**: 此函数的功能是执行文本查询的搜索操作，并返回符合条件的文档列表。

**参数**:
- `query`: 需要进行搜索的查询文本，数据类型为字符串。
- `top_k`: 返回的文档数量上限，数据类型为整数。
- `score_threshold`: 分数阈值，用于筛选相似度高于此阈值的文档，数据类型为浮点数。

**代码描述**:
`do_search`函数首先调用`_load_zilliz`方法来加载Zilliz服务，这一步骤确保了与Zilliz服务的连接已经建立，并且相关配置已经就绪。接下来，函数创建了一个`EmbeddingsFunAdapter`实例，该实例使用类中的`embed_model`属性作为嵌入模型。通过`EmbeddingsFunAdapter`的`embed_query`方法，将输入的查询文本`query`转换为嵌入向量。

得到嵌入向量后，函数调用`zilliz`实例的`similarity_search_with_score_by_vector`方法，执行相似度搜索操作。此方法接收嵌入向量、`top_k`参数，并返回一个包含文档及其相似度分数的列表。

最后，函数调用`score_threshold_process`方法，根据`score_threshold`参数筛选出相似度分数高于阈值的文档，并限制返回的文档数量不超过`top_k`。这一步骤确保了返回的文档列表既符合相似度要求，又满足数量上限的要求。

**注意**:
- 在调用`do_search`函数之前，需要确保`embed_model`已经正确配置，且指向一个有效的预训练嵌入模型。
- `score_threshold`参数允许调用者根据需要筛选相似度较高的文档，如果设置为较低的值，可能会返回更多的文档；如果设置为较高的值，则可能会返回较少的文档。
- `top_k`参数控制返回的文档数量上限，应根据实际需求合理设置。

**输出示例**:
假设输入查询文本为"人工智能"，`top_k`为3，`score_threshold`为0.5，且相似度搜索返回的文档及其相似度分数列表为[("doc1", 0.6), ("doc2", 0.4), ("doc3", 0.7), ("doc4", 0.5)]。经过`score_threshold_process`处理后，最终返回的文档列表可能为[("doc1", 0.6), ("doc3", 0.7), ("doc4", 0.5)]，表示这三个文档的相似度分数满足大于等于0.5的条件，并且数量不超过3。
***
### FunctionDef do_add_doc(self, docs)
**do_add_doc**: 此函数的功能是将文档添加到知识库中，并返回包含文档ID和元数据的列表。

**参数**:
- `docs`: 需要添加到知识库中的文档列表，每个文档都是一个Document对象。
- `**kwargs`: 接收额外的关键字参数，用于扩展或自定义功能。

**代码描述**:
此函数首先遍历传入的文档列表`docs`。对于每个文档，它会遍历文档的元数据`metadata`，将所有元数据的值转换为字符串格式。接着，它会检查是否有缺失的字段，如果有，则为这些字段设置默认的空字符串值。此外，函数会从元数据中移除特定的字段，这些字段通常是用于文本和向量表示的字段，由`self.zilliz._text_field`和`self.zilliz._vector_field`指定。

在处理完所有文档的元数据后，函数调用`self.zilliz.add_documents(docs)`方法将文档添加到知识库中，并接收返回的文档ID列表。最后，函数构造一个包含文档ID和更新后的元数据的列表，并将其返回。

**注意**:
- 确保传入的文档列表中的每个文档都有`metadata`属性，且其值为字典类型。
- 此函数不处理文本和向量字段的添加，确保在调用此函数之前已经正确设置了这些字段。
- 传入的文档对象应该是已经准备好添加到知识库的，包括所有必要的元数据和内容。

**输出示例**:
```python
[
    {"id": "123", "metadata": {"title": "文档标题1", "author": "作者1"}},
    {"id": "456", "metadata": {"title": "文档标题2", "author": "作者2"}}
]
```
此示例展示了函数返回值的可能形式，包含了每个文档的ID和更新后的元数据。
***
### FunctionDef do_delete_doc(self, kb_file)
**do_delete_doc**: 此函数用于从知识库中删除指定文件的文档。

**参数**:
- `kb_file`: KnowledgeFile对象，代表需要删除的知识库文件。
- `**kwargs`: 接收可变数量的关键字参数，用于扩展或自定义功能。

**代码描述**:
`do_delete_doc`函数是`ZillizKBService`类的一个方法，负责删除知识库中与指定文件相关的文档。首先，该函数检查`zilliz`对象的`col`属性是否存在，`col`属性代表当前操作的数据库集合。如果集合存在，则继续执行删除操作。

函数通过`kb_file`参数接收一个`KnowledgeFile`对象，该对象包含了知识库文件的详细信息，如文件路径等。为了确保文件路径在数据库查询中正确使用，函数首先将文件路径中的反斜杠(`\`)替换为双反斜杠(`\\`)，以适应数据库查询语法。

接着，函数使用`self.zilliz.col.query`方法查询与指定文件路径匹配的所有文档，并从查询结果中提取文档的主键(`pk`)列表。这一步是为了找出需要删除的文档的唯一标识符。

最后，函数通过`self.zilliz.col.delete`方法，使用提取的主键列表构造删除表达式，从数据库集合中删除这些文档。删除操作的表达式形式为`'pk in {delete_list}'`，其中`{delete_list}`是需要删除的文档主键的列表。

**注意**:
- 使用`do_delete_doc`函数时，需要确保传入的`kb_file`对象有效，并且该文件已经在知识库中注册。
- 删除操作依赖于`zilliz`对象的`col`属性，该属性必须指向一个有效的数据库集合。
- 文件路径的处理是为了适应数据库查询语法，确保查询和删除操作能够正确执行。
- 删除操作是基于文档的主键(`pk`)执行的，因此需要确保数据库中的文档有唯一的主键标识。

此函数与`KnowledgeFile`对象紧密相关，因为它使用`KnowledgeFile`对象提供的文件路径信息来定位和删除知识库中的文档。通过这种方式，`do_delete_doc`函数支持高效地管理知识库内容，允许用户根据文件信息快速删除相关文档，从而维护知识库的准确性和清洁度。
***
### FunctionDef do_clear_vs(self)
**do_clear_vs**: 此函数的功能是清理Zilliz知识库服务的视图状态。

**参数**: 此函数不接受任何参数。

**代码描述**: `do_clear_vs`函数是`ZillizKBService`类中的一个方法，用于在特定情况下清理Zilliz知识库服务的视图状态。该方法首先检查`ZillizKBService`实例的`zilliz.col`属性是否存在，这个属性代表当前的知识库集合。如果该属性存在，说明当前有一个活跃的知识库集合，那么`do_clear_vs`方法会进行两个步骤的操作：首先，调用`do_drop_kb`方法来释放并删除当前的知识库集合；其次，调用`do_init`方法来重新初始化Zilliz知识库服务。

`do_drop_kb`方法负责释放并删除知识库集合，确保在重新初始化之前，当前的集合资源被正确地清理。而`do_init`方法则用于重新加载和配置Zilliz服务，包括创建新的知识库集合和配置嵌入向量的处理。这一系列操作确保了Zilliz知识库服务可以在清理现有状态后，以正确的配置重新开始服务。

**注意**:
- 在调用`do_clear_vs`方法之前，应确保`ZillizKBService`实例已经正确初始化，特别是`zilliz.col`属性，它代表了当前的知识库集合。
- `do_clear_vs`方法的调用场景通常是在需要重置知识库服务状态时，例如在测试过程中或者在知识库数据结构需要更新时。
- 由于此方法会删除当前的知识库集合，因此在调用之前应确保不再需要集合中的数据，或者已经做好了数据备份。
- 此方法的执行会影响Zilliz知识库服务的状态，因此建议在知识库服务的使用低峰时段进行，以避免对正常服务造成影响。
***
