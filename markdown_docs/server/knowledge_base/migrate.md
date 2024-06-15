## FunctionDef create_tables
**create_tables**: 此函数的功能是创建数据库表。

**参数**: 此函数不接受任何参数。

**代码描述**: `create_tables` 函数是在数据库迁移过程中使用的关键函数，用于创建数据库中定义的所有表。它通过调用 `Base.metadata.create_all` 方法并将 `engine` 作为绑定参数来实现。这里的 `Base` 是一个ORM声明基类，它存储了所有模型（即表）的元数据，而 `engine` 是SQLAlchemy的连接引擎，用于执行对数据库的实际操作。

在项目中，`create_tables` 函数被多个对象调用，显示了其在不同场景下的重要性：
- 在初始化数据库（`init_database.py`）、服务器启动（`startup.py`）时，确保所需的表结构已经创建。
- 在重置表（`server/knowledge_base/migrate.py/reset_tables`）时，先删除所有表，然后重新调用此函数来创建表，用于测试或重置数据库环境。
- 在各种测试场景中（如`tests/kb_vector_db/test_faiss_kb.py/test_init`、`tests/kb_vector_db/test_milvus_db.py/test_init`、`tests/kb_vector_db/test_pg_db.py/test_init`），确保测试前数据库表结构正确设置。

**注意**: 使用此函数时，需要确保`Base`和`engine`已经正确初始化，且所有的表模型都已经通过`Base`定义。此外，调用此函数将会创建所有未存在的表，如果表已经存在，则不会对其进行修改，这意味着它不会更新或修改现有表结构。因此，在生产环境中使用时应谨慎，以避免数据丢失。
## FunctionDef reset_tables
**reset_tables**: 此函数的功能是重置数据库表。

**参数**: 此函数不接受任何参数。

**代码描述**: `reset_tables` 函数是数据库迁移过程中的一个重要环节，用于重置数据库环境。它首先调用 `Base.metadata.drop_all` 方法删除所有现有的表结构，然后通过调用 `create_tables` 函数重新创建表结构。这个过程通常用于测试或者在需要彻底清理数据库并重新设置表结构的场景下。

在这个函数中，`Base.metadata.drop_all(bind=engine)` 负责删除所有表，其中 `Base` 是ORM声明基类，存储了所有模型（即表）的元数据，`engine` 是SQLAlchemy的连接引擎，用于执行对数据库的实际操作。紧接着，`create_tables()` 被调用以重新创建数据库中定义的所有表。这确保了数据库环境可以被重置到一个干净的初始状态。

**注意**: 在调用 `reset_tables` 函数时，需要确保 `Base` 和 `engine` 已经被正确初始化，并且所有的表模型都已经通过 `Base` 定义。此外，由于此函数会删除所有现有的表并重新创建，因此在生产环境中使用时应格外小心，以避免不必要的数据丢失。在测试或开发环境中使用此函数可以帮助快速重置数据库状态，便于进行环境的清理和重建。
## FunctionDef import_from_db(sqlite_path)
**import_from_db**: 该函数的功能是从备份数据库中导入数据到 info.db。

**参数**:
- `sqlite_path`: 字符串类型，指定 SQLite 数据库的路径。默认为 None。

**代码描述**:
`import_from_db` 函数主要用于在知识库与向量库无变化的情况下，从备份的 SQLite 数据库中导入数据到当前的 info.db 数据库中。这种情况通常出现在版本升级时，info.db 的结构发生了变化，但数据本身不需要重新向量化处理。函数开始时，会导入必要的模块，包括 `sqlite3` 用于操作 SQLite 数据库，以及 `pprint` 用于打印数据。

函数内部首先获取数据库模型列表，然后尝试连接到指定的 SQLite 数据库。通过查询 SQLite 的 `sqlite_master` 表，获取并遍历所有表名。对于每一个模型对应的表，如果表存在于数据库中，则会进一步读取该表的所有数据。对于每一行数据，函数会根据模型定义的列名过滤出需要的字段，并特别处理 `create_time` 字段，将其解析为正确的时间格式。之后，使用 `session_scope` 上下文管理器自动管理数据库会话，将过滤并处理后的数据添加到会话中，最终提交到数据库。

如果在数据导入过程中遇到任何异常，函数会打印错误信息，并返回 False 表示导入失败。否则，在成功处理所有数据后关闭数据库连接，并返回 True 表示导入成功。

**注意**:
- 请确保传入的 `sqlite_path` 是正确的 SQLite 数据库文件路径。
- 确保备份数据库中的表名和字段名与当前数据库模型一致。
- 该函数目前仅支持 SQLite 数据库。
- 使用该函数导入数据时，应确保没有其他操作正在访问目标数据库，以避免数据冲突。

**输出示例**:
- 成功导入数据时，函数返回 `True`。
- 如果无法读取备份数据库或遇到其他错误，函数返回 `False`。
## FunctionDef file_to_kbfile(kb_name, files)
**file_to_kbfile**: 该函数的功能是将文件列表转换为KnowledgeFile对象列表。

**参数**:
- `kb_name`: 字符串类型，表示知识库的名称。
- `files`: 字符串列表，包含需要转换的文件名。

**代码描述**: `file_to_kbfile`函数接收知识库名称和文件名列表作为输入参数，遍历文件列表，为每个文件创建一个`KnowledgeFile`实例。在实例化`KnowledgeFile`过程中，如果遇到任何异常，该文件会被跳过，并且异常信息会被记录到日志中。函数最终返回一个`KnowledgeFile`对象的列表，这些对象包含了文件与知识库名称的关联信息以及其他由`KnowledgeFile`类提供的文件处理功能。

**注意**:
- 在调用此函数之前，需要确保传入的文件列表中的文件都存在于磁盘上。
- 如果文件格式不被支持，或者在创建`KnowledgeFile`实例的过程中出现其他问题，相关文件将被跳过，错误信息会被记录。
- 日志记录的详细程度取决于全局日志配置中`log_verbose`的设置。

**输出示例**:
假设有一个文件列表`["document1.md", "document2.txt"]`和知识库名称`"demo_kb"`，调用`file_to_kbfile("demo_kb", ["document1.md", "document2.txt"])`可能会返回如下`KnowledgeFile`对象列表（具体内容取决于文件内容和`KnowledgeFile`类的实现）:
```python
[
    KnowledgeFile(filename="document1.md", knowledge_base_name="demo_kb"),
    KnowledgeFile(filename="document2.txt", knowledge_base_name="demo_kb")
]
```
这个列表中的每个`KnowledgeFile`对象都代表了一个与知识库`demo_kb`关联的文件，可以进一步用于知识库的文件处理、文档加载和文本分割等操作。

在项目中，`file_to_kbfile`函数被用于多个场景，包括但不限于将本地文件夹中的文件转换为知识库文件、更新知识库中的文件、从知识库中删除文件等。例如，在`folder2db`函数中，它被用来将指定文件夹中的文件转换为`KnowledgeFile`对象，然后这些对象可以用于向量库的创建或更新；在`prune_db_docs`函数中，它用于识别并删除那些在本地文件夹中已经不存在的知识库文件。
## FunctionDef folder2db(kb_names, mode, vs_type, embed_model, chunk_size, chunk_overlap, zh_title_enhance)
**folder2db**: 此函数的功能是使用本地文件夹中的现有文件来填充数据库和/或向量存储。

**参数**:
- `kb_names`: 知识库名称列表，类型为 `List[str]`。
- `mode`: 迁移模式，可选值为 `"recreate_vs"`, `"update_in_db"`, `"increment"`，类型为 `Literal["recreate_vs", "update_in_db", "increment"]`。
- `vs_type`: 向量存储类型，可选值为 `"faiss"`, `"milvus"`, `"pg"`, `"chromadb"`，默认值为 `DEFAULT_VS_TYPE`，类型为 `Literal["faiss", "milvus", "pg", "chromadb"]`。
- `embed_model`: 嵌入模型名称，默认值为 `EMBEDDING_MODEL`，类型为 `str`。
- `chunk_size`: 分块大小，默认值为 `CHUNK_SIZE`，类型为 `int`。
- `chunk_overlap`: 分块重叠大小，默认值为 `OVERLAP_SIZE`，类型为 `int`。
- `zh_title_enhance`: 是否增强中文标题，默认值为 `ZH_TITLE_ENHANCE`，类型为 `bool`。

**代码描述**:
此函数根据提供的参数，从本地文件夹中读取文件，并根据指定的迁移模式将文件信息填充到数据库和/或向量存储中。支持的迁移模式包括：
- `recreate_vs`：重新创建所有向量存储，并使用本地文件夹中的现有文件填充数据库信息。
- `update_in_db`：使用数据库中已存在的本地文件更新向量存储和数据库信息。
- `increment`：为数据库中不存在的本地文件创建向量存储和数据库信息。

函数首先检查是否提供了知识库名称列表，如果没有，则调用 `list_kbs_from_folder` 函数获取所有知识库目录名称。然后，根据指定的向量存储类型和嵌入模型名称，通过 `KBServiceFactory.get_service` 方法获取相应的知识库服务实例。根据迁移模式的不同，函数执行相应的操作，如清除向量存储、创建知识库、更新向量存储等。

**注意**:
- 在使用此函数之前，确保本地文件夹中存在目标知识库的相关文件。
- 根据迁移模式的不同，操作可能会涉及到重建向量存储或更新数据库信息，这可能会对现有数据产生影响，请谨慎操作。
- 函数内部通过调用多个辅助函数和服务实例方法来完成具体的操作，确保这些辅助函数和方法已正确实现并可用。

在项目中，`folder2db` 函数被用于初始化数据库 (`init_database.py`) 和测试迁移功能 (`tests/test_migrate.py`)，包括测试重新创建向量存储 (`test_recreate_vs`) 和增量更新 (`test_increment`)。这些调用情况表明，`folder2db` 函数是知识库迁移和管理流程中的关键组件，用于根据本地文件夹中的文件更新或重建数据库和向量存储。
### FunctionDef files2vs(kb_name, kb_files)
**files2vs**: 此函数的功能是将文件批量转换并添加到向量库中。

**参数**:
- `kb_name`: 字符串类型，表示知识库的名称。
- `kb_files`: `KnowledgeFile`对象的列表，表示要处理并添加到向量库的文件列表。

**代码描述**:
`files2vs`函数主要负责将给定的文件列表（`kb_files`）批量处理并添加到指定的知识库（`kb_name`）中。这个过程涉及以下几个步骤：

1. 调用`files2docs_in_thread`函数，该函数使用多线程将文件列表中的每个文件转换成文档列表。这个过程中，会根据文件的内容和一系列参数（如文档分块大小`chunk_size`、分块重叠大小`chunk_overlap`、是否增强中文标题`zh_title_enhance`等）进行处理。

2. 对于`files2docs_in_thread`函数的每个返回结果，首先检查转换是否成功。如果成功，会获取转换后的文件名和文档列表。

3. 对于每个成功转换的文件，创建一个新的`KnowledgeFile`实例，并将文件名、知识库名称以及分割处理后的文档列表（`splited_docs`）设置给这个实例。

4. 调用`KBService`的`add_doc`方法，将上一步创建的`KnowledgeFile`实例添加到知识库中。在这个过程中，不刷新向量库缓存（`not_refresh_vs_cache=True`）。

5. 如果转换失败，则打印错误信息。

此函数通过上述步骤，实现了将文件内容批量转换并添加到知识库的向量库中，以支持后续的搜索和检索功能。

**注意**:
- 在使用`files2vs`函数时，需要确保传入的`kb_name`和`kb_files`参数正确且有效。`kb_files`中的每个`KnowledgeFile`对象都应该是可以被正确处理的文件。
- `files2docs_in_thread`函数的多线程处理可以提高文件转换的效率，但在使用时也需要注意线程安全问题。
- `add_doc`方法的调用不刷新向量库缓存，这意味着在添加大量文档后，可能需要手动刷新缓存以确保向量库的数据是最新的。
***
## FunctionDef prune_db_docs(kb_names)
**prune_db_docs**: 此函数的功能是删除数据库中不存在于本地文件夹中的文档。

**参数**:
- `kb_names`: 字符串列表，包含需要进行清理操作的知识库名称。

**代码描述**: `prune_db_docs` 函数通过遍历传入的知识库名称列表 `kb_names`，对每一个知识库执行以下操作：
1. 使用 `KBServiceFactory.get_service_by_name` 方法根据知识库名称获取对应的知识库服务实例。如果该实例存在，则继续执行；如果不存在，则跳过当前知识库。
2. 调用知识库服务实例的 `list_files` 方法获取数据库中的文件列表。
3. 调用 `list_files_from_folder` 函数获取本地文件夹中的文件列表。
4. 计算出存在于数据库中但不在本地文件夹中的文件列表。
5. 使用 `file_to_kbfile` 函数将步骤4中得到的文件列表转换为 `KnowledgeFile` 对象列表。
6. 遍历 `KnowledgeFile` 对象列表，对每个对象调用知识库服务实例的 `delete_doc` 方法删除数据库中的文档，并打印成功删除的文档信息。
7. 调用知识库服务实例的 `save_vector_store` 方法保存向量库的状态。

**注意**:
- 确保在调用此函数之前，传入的知识库名称列表 `kb_names` 中的每个知识库都已经在数据库中注册并正确配置。
- 此函数用于同步本地文件夹和数据库中的文档状态，特别适用于用户在文件浏览器中删除了某些文档文件后，需要从数据库中也删除这些文档的场景。
- 在删除数据库中的文档时，`delete_doc` 方法的 `not_refresh_vs_cache` 参数被设置为 `True`，这意味着在删除操作后不立即刷新向量库缓存。向量库的状态将在所有删除操作完成后通过 `save_vector_store` 方法统一保存。
- 函数执行过程中，会打印每个成功删除的文档的信息，包括知识库名称和文件名，以便于跟踪操作结果。

通过以上步骤，`prune_db_docs` 函数能够有效地从数据库中删除那些已经不再存在于本地文件夹中的文档，从而保持数据库内容的准确性和最新性。
## FunctionDef prune_folder_files(kb_names)
**prune_folder_files**: 此函数的功能是删除本地文件夹中不存在于数据库中的文档文件，用于通过删除未使用的文档文件释放本地磁盘空间。

**参数**:
- `kb_names`: 一个字符串列表，表示需要处理的知识库的名称。

**代码描述**:
`prune_folder_files` 函数接收一个包含知识库名称的列表作为参数。对于列表中的每一个知识库名称，函数首先使用 `KBServiceFactory.get_service_by_name` 方法尝试获取对应的知识库服务实例。如果成功获取到服务实例，则继续执行以下步骤：

1. 调用知识库服务实例的 `list_files` 方法获取数据库中存储的文件列表。
2. 使用 `list_files_from_folder` 函数获取本地文件夹中的文件列表。
3. 通过集合运算找出存在于本地文件夹中但不在数据库文件列表中的文件，这些文件被认为是未使用的文件。
4. 对于每一个未使用的文件，使用 `os.remove` 方法删除该文件，并打印删除成功的消息。

此过程确保了本地存储空间不会被数据库中已经不存在的文件占用，从而优化了存储资源的使用。

**注意**:
- 在调用此函数之前，需要确保提供的知识库名称列表中的每个名称都是有效的，并且对应的知识库服务实例可以成功获取。
- 该函数依赖于 `KBServiceFactory.get_service_by_name`、`list_files_from_folder` 和 `get_file_path` 函数，因此需要确保这些依赖函数能够正常工作。
- 删除文件操作是不可逆的，因此在执行此函数之前应确保已经正确备份了重要数据。
- 函数执行过程中会打印每个被删除文件的信息，可以通过这些信息跟踪删除操作的执行情况。
