## FunctionDef document
**document**: 此函数的功能是重定向到文档页面。

**参数**: 此函数不接受任何参数。

**代码描述**: `document` 函数是一个异步函数，其主要作用是将用户的请求重定向到服务器上的文档页面。在这个项目中，当用户访问服务器的根路径("/")时，通过调用此函数实现自动跳转到文档页面。这是通过返回一个 `RedirectResponse` 对象实现的，该对象中包含了目标URL（即文档页面的URL）。在这个例子中，目标URL被硬编码为 "/docs"，意味着当此函数被触发时，用户的浏览器将会被重定向到服务器的 "/docs" 路径，通常这个路径下托管着API的交互式文档，如Swagger UI或Redoc。

此函数被 `mount_app_routes` 函数调用，作为FastAPI应用的一部分，用于在应用启动时设置路由。在 `mount_app_routes` 函数中，`document` 函数被注册为处理根路径("/")请求的处理器。这样，当用户访问应用的根路径时，他们会被自动重定向到API文档页面，从而提供了一种用户友好的方式来探索和测试API。

**注意**: 使用此函数时，需要确保 "/docs" 路径下确实存在文档页面。在FastAPI中，默认情况下，API文档通常是自动生成的，并且可以通过 "/docs"（Swagger UI）或 "/redoc"（Redoc）路径访问。如果你更改了文档页面的路径或使用了自定义文档页面，需要相应地更新此函数中的URL。

**输出示例**: 由于此函数的作用是进行页面重定向，因此它不直接产生可视化的输出。但在浏览器中，当访问根路径("/")时，浏览器的地址栏将会显示为 "/docs"，并展示相应的API文档页面。
## FunctionDef create_app(run_mode)
Doc is waiting to be generated...
## FunctionDef mount_app_routes(app, run_mode)
**mount_app_routes**: 该函数用于在FastAPI应用中挂载应用路由。

**参数**:
- `app`: FastAPI应用实例，用于注册路由。
- `run_mode`: 运行模式，用于区分应用的运行环境，例如开发环境或生产环境。

**代码描述**:
`mount_app_routes`函数主要负责在FastAPI应用实例中注册各种API路由。这些路由包括对话、搜索引擎对话、聊天记录反馈、知识库管理、LLM模型管理、服务器状态查询等功能的接口。通过调用`app.get`和`app.post`方法，将特定的URL路径与处理函数绑定，从而实现API的路由功能。此外，函数还调用了`mount_knowledge_routes`和`mount_filename_summary_routes`两个函数，分别用于挂载知识库相关和文件名摘要相关的路由。在注册路由的过程中，为每个API接口设置了标签（tags）、摘要（summary）等信息，以便于在API文档中进行分类和说明。

**注意**:
- 在使用`mount_app_routes`函数之前，需要确保已经创建了FastAPI应用实例，并且所有处理函数都已正确定义。
- 该函数是API路由注册的入口点，通过它可以将应用的各种功能接口集成到FastAPI应用中。
- 在实际部署和使用时，应注意API接口的安全性，避免未授权的访问和操作。
- `run_mode`参数可以用于根据不同的运行环境调整API的行为，例如在开发环境中启用调试模式，在生产环境中优化性能。

**输出示例**:
由于`mount_app_routes`函数的作用是注册路由而不直接返回数据，因此它没有直接的输出示例。函数执行成功后，FastAPI应用将能够响应对应路由的HTTP请求，并根据请求的URL路径调用相应的处理函数。例如，当用户通过HTTP POST请求访问`/chat/chat`路径时，FastAPI应用将调用`chat`函数处理该请求，并返回处理结果。
### FunctionDef get_server_prompt_template(type, name)
**get_server_prompt_template**: 该函数用于根据提供的类型和名称参数，动态加载并返回相应的模板内容。

**参数**：
- type: 字面量类型，可选值为"llm_chat"、"knowledge_base_chat"、"search_engine_chat"、"agent_chat"，用于指定模板的类型。默认值为"llm_chat"。
- name: 字符串类型，用于指定模板的名称。默认值为"default"。

**代码描述**：
`get_server_prompt_template`函数是API层面用于处理模板加载请求的入口。该函数接收两个参数：`type`和`name`，分别代表模板的类型和名称。函数内部调用了`get_prompt_template`函数，传入相同的`type`和`name`参数，以获取指定的模板内容。

`get_prompt_template`函数位于`server/utils.py`文件中，负责从配置中加载指定类型和名称的模板内容。它首先从`configs`模块导入`prompt_config`配置，然后使用`importlib.reload`方法重新加载`prompt_config`，以确保获取到最新的配置信息。通过`type`参数从`prompt_config.PROMPT_TEMPLATES`中索引到对应类型的模板字典，再使用`name`参数从该字典中获取具体的模板内容。如果指定的`name`在字典中不存在，则返回`None`。

在项目结构中，`get_server_prompt_template`函数位于`server/api.py/mount_app_routes`路径下，作为API接口的一部分，允许前端或其他服务通过HTTP请求动态获取不同类型和名称的模板内容，从而支持灵活的聊天模式或功能需求。

**注意**：
- 调用`get_server_prompt_template`函数时，需要确保`type`和`name`参数的值正确无误，并且所请求的模板已经在`prompt_config`中定义。
- 由于`get_prompt_template`函数依赖于外部的配置文件`prompt_config`，在修改配置文件后，可能需要重启服务或动态重新加载配置，以确保更改生效。

**输出示例**：
假设存在以下模板配置：
```python
PROMPT_TEMPLATES = {
    "llm_chat": {
        "default": "你好，请问有什么可以帮助你的？"
    }
}
```
当调用`get_server_prompt_template(type="llm_chat", name="default")`时，将返回字符串`"你好，请问有什么可以帮助你的？"`。
***
## FunctionDef mount_knowledge_routes(app)
**mount_knowledge_routes**: 该函数的功能是在FastAPI应用中挂载知识库相关的路由。

**参数**: 该函数接受一个参数：
- `app`: FastAPI应用实例，用于注册路由。

**代码描述**: `mount_knowledge_routes` 函数主要负责将知识库管理和操作相关的API接口注册到FastAPI应用中。通过导入不同的处理函数，如`knowledge_base_chat`、`upload_temp_docs`、`file_chat`、`agent_chat`等，并使用`app.post`或`app.get`方法将这些处理函数与特定的URL路径绑定，从而实现API的路由功能。此外，函数还为每个API接口设置了标签（tags）、摘要（summary）等信息，以便于在API文档中进行分类和说明。

该函数涵盖了知识库的创建、删除、文件上传、文件删除、文档搜索、文档更新、下载文档、重建向量库等多个功能。每个功能都通过特定的URL路径进行访问，例如，通过`/knowledge_base/create_knowledge_base`路径可以访问创建知识库的接口。

**注意**:
- 在使用`mount_knowledge_routes`函数之前，需要确保已经创建了FastAPI应用实例，并且所有处理函数都已正确定义。
- 该函数是知识库管理功能在FastAPI框架中的入口点，通过它可以将知识库相关的操作集成到FastAPI应用中。
- 在实际部署和使用时，应注意API接口的安全性，避免未授权的访问和操作。
## FunctionDef mount_filename_summary_routes(app)
**mount_filename_summary_routes**: 此函数的功能是在FastAPI应用中挂载处理文件名摘要的路由。

**参数**:
- `app`: FastAPI应用实例，用于注册路由。

**代码描述**:
`mount_filename_summary_routes`函数主要负责在FastAPI应用中注册三个与文件名摘要相关的POST路由。这些路由分别用于处理单个知识库根据文件名称摘要、根据doc_ids摘要以及重建单个知识库文件摘要的请求。

1. `/knowledge_base/kb_summary_api/summary_file_to_vector_store`路由用于处理根据文件名称对单个知识库进行摘要，并将摘要结果存储到向量存储中。此路由使用`summary_file_to_vector_store`函数处理请求。

2. `/knowledge_base/kb_summary_api/summary_doc_ids_to_vector_store`路由用于处理根据文档ID列表生成单个知识库的文档摘要，并将摘要信息存储到向量存储中。此路由使用`summary_doc_ids_to_vector_store`函数处理请求，并指定`response_model`为`BaseResponse`，以规范化响应格式。

3. `/knowledge_base/kb_summary_api/recreate_summary_vector_store`路由用于处理重建单个知识库文件摘要的请求。此路由使用`recreate_summary_vector_store`函数处理请求。

每个路由都通过`app.post`方法注册，并指定了路由的路径、处理函数、标签（tags）和摘要（summary）。这些信息有助于生成自动化的API文档，提高API的可发现性和可理解性。

**注意**:
- 在使用这些API接口之前，确保相关的处理函数已经正确实现，并且知识库服务已经配置妥当。
- 通过指定`response_model`为`BaseResponse`，可以统一API的响应格式，使得响应数据更加规范化，便于客户端处理。
- 这些路由主要用于处理知识库文件摘要的生成和管理，因此在调用这些API时，需要提供正确的知识库名称、文件名称或文档ID列表等信息。
- 在项目中，`mount_filename_summary_routes`函数被`mount_app_routes`函数调用，意味着这些文件名摘要相关的路由是作为应用的一部分被自动挂载和注册的。这有助于保持路由注册的集中管理和应用结构的清晰。
## FunctionDef run_api(host, port)
**run_api**: 此函数的功能是启动API服务。

**参数**:
- **host**: 服务器的主机名或IP地址。
- **port**: 服务器监听的端口号。
- **kwargs**: 关键字参数，可选，用于提供SSL证书文件路径。

**代码描述**:
`run_api`函数负责启动API服务。它接受三个参数：`host`、`port`以及可选的关键字参数`kwargs`。这些参数用于指定服务器的监听地址和端口，以及配置SSL加密连接所需的证书文件路径。

函数首先检查`kwargs`中是否提供了`ssl_keyfile`和`ssl_certfile`这两个关键字参数。如果这两个参数都被提供，函数将使用这些证书文件启动一个支持SSL加密的API服务。这是通过调用`uvicorn.run`函数并传入相应的参数来实现的，包括应用实例`app`、主机名`host`、端口号`port`、SSL密钥文件路径`ssl_keyfile`和SSL证书文件路径`ssl_certfile`。

如果`kwargs`中没有提供SSL相关的参数，`run_api`函数将启动一个不使用SSL加密的API服务。这同样是通过调用`uvicorn.run`函数实现的，但此时只传入应用实例`app`、主机名`host`和端口号`port`作为参数。

**注意**:
- 确保在启动支持SSL的API服务之前，已经正确生成并指定了SSL证书文件和密钥文件的路径。
- 在没有提供SSL证书文件路径的情况下，API服务将以非加密模式运行，这可能不适合生产环境中处理敏感信息。
- `uvicorn.run`是Uvicorn库的一部分，Uvicorn是一个轻量级、超快的ASGI服务器，用于Python异步web应用。确保在使用`run_api`函数之前已经安装了Uvicorn库。
