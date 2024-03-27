## FunctionDef get_messages_history(history_len, content_in_expander)
**get_messages_history**: 此函数的功能是获取消息历史记录。

**参数**:
- `history_len`: 指定要获取的消息历史记录的长度。
- `content_in_expander`: 一个布尔值，控制是否返回expander元素中的内容，默认为False。

**代码描述**:
`get_messages_history`函数用于从聊天框中筛选并返回指定长度的消息历史记录。它接受两个参数：`history_len`和`content_in_expander`。`history_len`参数指定了需要获取的历史消息的数量，而`content_in_expander`参数控制是否包含expander元素中的内容。这个功能在导出消息历史时特别有用，因为用户可以选择是否需要expander中的额外信息。

函数内部，定义了一个名为`filter`的内部函数，用于筛选每条消息中符合条件的内容。它首先筛选出消息元素中输出方法为"markdown"或"text"的内容，然后根据`content_in_expander`参数的值决定是否包含在expander中的内容。最后，将筛选出的内容拼接成字符串，作为消息的内容返回。

`get_messages_history`函数通过调用`chat_box.filter_history`方法，并传入`history_len`和`filter`函数作为参数，返回经过筛选的消息历史记录。每条记录包含消息的角色（发送者）和内容。

在项目中，此函数被`dialogue_page`函数调用，用于在用户与系统进行交互时获取历史对话记录。这使得系统能够根据过去的交流提供更加个性化和上下文相关的回复。

**注意**:
- 当`content_in_expander`设置为True时，返回的消息历史将包含expander元素中的内容，这可能会增加返回数据的大小。
- 此函数依赖于`chat_box`对象的`filter_history`方法，因此需要确保`chat_box`对象已正确初始化并包含有效的消息历史数据。

**输出示例**:
```python
[
    {
        "role": "user",
        "content": "你好，我想了解更多关于AI的信息。"
    },
    {
        "role": "ai",
        "content": "当然，AI是人工智能的简称，它能够执行很多复杂的任务。"
    }
]
```
此示例展示了一个可能的输出，包含两条消息记录，一条来自用户，另一条来自AI，每条记录都包含发送者的角色和消息内容。
### FunctionDef filter(msg)
**filter**: 此函数的功能是过滤并整理消息内容。

**参数**:
- msg: 包含消息元素的字典，其中“elements”是一个列表，列表中的每个元素都是一个对象，这些对象包含消息的内容和输出方式等信息。

**代码描述**:
此函数首先遍历`msg["elements"]`列表，筛选出其中`_output_method`属性值为"markdown"或"text"的元素。这一步骤确保了只有以Markdown或纯文本形式输出的消息内容被选中。接着，如果`content_in_expander`变量不存在或其值为`False`（此处代码中未显示`content_in_expander`的定义，可能是外部变量或前文已定义），则进一步筛选出不在折叠区域（expander）内的消息内容。最后，将筛选出的元素中的内容（`x.content`）提取出来，组成一个新的列表。

函数返回一个字典，包含两个键值对：
- "role"：直接从输入的`msg`字典中获取其"role"值，表示消息的角色。
- "content"：将上述筛选并提取出的内容列表中的元素用两个换行符`\n\n`连接成一个字符串，表示最终整理好的消息内容。

**注意**:
- 确保输入的`msg`字典中包含"elements"键，且其值为一个列表，列表中的元素包含`_output_method`和`content`属性。
- 此函数未处理`content_in_expander`变量可能未定义的情况，使用时需确保该变量在上下文中有明确的定义和值。
- 函数的处理逻辑依赖于消息元素的属性，确保消息元素对象有`_output_method`、`_in_expander`和`content`属性。

**输出示例**:
假设输入的`msg`字典如下：
```python
{
    "role": "user",
    "elements": [
        {"_output_method": "markdown", "content": "Hello, world!", "_in_expander": False},
        {"_output_method": "text", "content": "How are you?", "_in_expander": True}
    ]
}
```
则函数的返回值可能为：
```python
{
    "role": "user",
    "content": "Hello, world!"
}
```
这表示经过筛选，只有不在折叠区域内且输出方式为markdown或text的消息内容被整理并返回。
***
## FunctionDef upload_temp_docs(files, _api)
**upload_temp_docs**: 该函数用于将文件上传到临时目录，用于文件对话，并返回临时向量库ID。

**参数**:
- `files`: 需要上传的文件列表。
- `_api`: ApiRequest 类的实例，用于执行与 API 服务器的交互。

**代码描述**:
`upload_temp_docs` 函数接收一个文件列表和一个 ApiRequest 类的实例作为参数。它通过调用 `_api` 实例的 `upload_temp_docs` 方法来上传文件到服务器的临时目录，并用于后续的文件对话处理。上传成功后，服务器会返回一个包含临时向量库ID的响应。该函数通过链式调用 `.get("data", {}).get("id")` 来从响应中提取临时向量库ID，并将其返回。

在项目中，`upload_temp_docs` 函数被 `dialogue_page` 函数调用，用于实现文件对话功能。用户可以通过上传文件，将文件内容作为知识库的一部分，进而在对话中引用文件内容进行问答。这在处理需要引用大量文档内容的对话场景中非常有用。

**注意**:
- 确保 `_api` 参数是一个有效的 ApiRequest 实例，且已正确配置 API 服务器的基础 URL。
- 上传的文件列表 `files` 应包含有效的文件路径或文件对象，以便函数能够正确处理并上传文件。

**输出示例**:
假设上传文件成功，服务器返回的响应如下：
```json
{
  "code": 200,
  "msg": "成功",
  "data": {
    "id": "temp_vector_library_id_123456"
  }
}
```
则该函数的返回值将是字符串 `"temp_vector_library_id_123456"`，表示临时向量库的ID。
## FunctionDef parse_command(text, modal)
**parse_command**: 此函数用于解析用户输入的自定义命令，并根据命令执行相应的操作。

**参数**:
- text: 用户输入的文本，类型为字符串。
- modal: 一个Modal对象，用于在需要时展示模态对话框。

**代码描述**:
`parse_command`函数主要负责处理用户在对话界面中输入的特定命令。这些命令包括创建新会话(`/new`)、删除会话(`/del`)、清除会话内容(`/clear`)以及查看帮助信息(`/help`)。函数首先通过正则表达式匹配用户输入的命令格式，如果匹配成功，则根据命令类型执行相应的操作。

- `/help`命令会触发模态对话框的打开，展示可用命令的帮助信息。
- `/new`命令用于创建一个新的会话。如果用户没有指定会话名称，则自动生成一个默认名称。如果指定的会话名称已存在，则显示错误信息。
- `/del`命令用于删除一个指定的会话。如果没有指定会话名称，则默认删除当前会话。如果是最后一个会话或指定的会话不存在，则显示错误信息。
- `/clear`命令用于清除指定会话的聊天历史。如果没有指定会话名称，则默认清除当前会话的聊天历史。

该函数与项目中的`dialogue_page`函数紧密相关。在`dialogue_page`函数中，用户的输入首先通过`parse_command`函数进行处理，以判断是否为自定义命令。如果是，根据命令执行相应操作并重新渲染页面；如果不是自定义命令，则按照正常的对话流程继续处理用户的输入。

**注意**:
- 在使用此函数时，需要确保`modal`对象已正确初始化，以便在需要时能够展示帮助信息等模态对话框。
- 函数依赖于全局状态（如`st.session_state`）来管理会话信息，因此在调用此函数之前应确保相关状态已正确设置。

**输出示例**:
假设用户输入了`/help`命令，函数将返回`True`，并触发帮助信息的模态对话框展示。如果用户输入的是非命令文本，如“你好”，函数将返回`False`。
## FunctionDef dialogue_page(api, is_lite)
**dialogue_page**: 此函数用于处理对话页面的逻辑，包括初始化会话、处理用户输入、展示对话历史等。

**参数**:
- `api`: ApiRequest 类的实例，用于执行与 API 服务器的交互。
- `is_lite`: 布尔类型，默认为False，指示是否为轻量级模式。

**代码描述**:
`dialogue_page`函数是对话系统的核心，负责处理用户与系统的交互。函数首先初始化会话状态，包括会话ID和文件聊天ID。然后，根据是否为首次访问，展示欢迎信息并初始化聊天框。接着，函数处理自定义命令的帮助信息，并在侧边栏中提供对话模式、LLM模型选择、Prompt模板选择等配置选项。

函数中还包含了对不同对话模式（如LLM对话、知识库问答、文件对话等）的处理逻辑，以及对用户输入的处理。用户输入的文本首先检查是否为自定义命令，如果是，则执行相应的命令；如果不是，则根据当前的对话模式调用相应的API进行处理，并展示回复。

此外，函数还处理了对话历史的展示、反馈的收集以及对话记录的导出等功能。在处理完所有逻辑后，如果需要，函数会触发页面的重新渲染。

**注意**:
- 确保传入的`api`参数是有效的ApiRequest实例，且已正确配置API服务器的地址。
- 函数依赖于多个全局变量和函数，如`chat_box`、`get_messages_history`等，需要确保这些依赖在调用`dialogue_page`之前已正确初始化。
- 函数中的模态对话框、侧边栏配置和对话历史展示等UI元素的实现依赖于Streamlit库，确保在使用此函数时已正确设置Streamlit环境。

**输出示例**:
由于`dialogue_page`函数主要负责处理页面逻辑并直接与用户交互，而不直接返回数据，因此没有具体的返回值示例。函数执行的结果是在Web UI上展示对话界面，处理用户输入，并根据不同的对话模式和用户操作展示相应的回复或执行相应的命令。
### FunctionDef on_feedback(feedback, message_id, history_index)
**on_feedback**: 此函数用于处理用户的反馈信息。

**参数**:
- `feedback`: 用户反馈的内容，是一个字典，其中至少包含`text`键，表示反馈的原因。
- `message_id`: 字符串类型，默认为空字符串，指定需要反馈的消息ID。
- `history_index`: 整型，默认为-1，表示在聊天历史中的索引位置。

**代码描述**:
`on_feedback`函数主要负责处理用户对聊天对话的反馈。它首先从`feedback`参数中提取用户的反馈原因，存储在变量`reason`中。然后，调用`chat_box.set_feedback`方法，将用户的反馈内容和历史索引作为参数传递，此方法返回一个整数`score_int`，代表反馈的评分。接下来，函数利用`api.chat_feedback`方法，将`message_id`、`score_int`（评分）和`reason`（反馈原因）作为参数提交给服务器。此过程中，`api.chat_feedback`方法的作用是向服务器发送POST请求，提交用户的反馈信息，具体包括消息ID、评分和评分原因。最后，函数设置`st.session_state["need_rerun"]`为`True`，这是为了通知系统需要重新运行，以便更新用户界面或执行其他必要的更新操作。

**注意**:
- 确保`feedback`参数中包含有效的反馈原因。
- `message_id`和`history_index`参数虽然有默认值，但在实际使用中应根据需要提供具体值，以确保反馈能准确关联到特定的消息。
- 此函数的执行会触发与服务器的交互，因此需要注意网络状态和服务器响应。
- 设置`st.session_state["need_rerun"]`为`True`是为了确保用户界面能够根据最新的反馈信息进行更新，开发者在使用此函数时应考虑到这一点。
***
### FunctionDef on_mode_change
**on_mode_change**: 此函数用于处理对话模式变更时的响应逻辑。

**参数**: 此函数不接受任何参数。

**代码描述**: `on_mode_change` 函数首先从 `st.session_state` 中获取当前对话模式 (`dialogue_mode`)，并根据这个模式生成一条提示信息。如果当前模式是 "知识库问答"，函数会进一步检查是否已选择了知识库 (`selected_kb`)。如果已选择知识库，提示信息会包含当前选中的知识库名称。最后，使用 `st.toast` 方法显示这条提示信息。

具体来说，函数执行的步骤如下：
1. 从 `st.session_state` 中获取 `dialogue_mode` 的值，这代表了当前的对话模式。
2. 根据获取的模式，生成基本的提示信息，格式为 "已切换到 {mode} 模式。"。
3. 如果当前模式为 "知识库问答"，则尝试从 `st.session_state` 中获取 `selected_kb` 的值，即当前选中的知识库。
4. 如果存在选中的知识库，提示信息会追加 "当前知识库：`{cur_kb}`。"，以告知用户当前正在使用的知识库。
5. 使用 `st.toast` 方法显示最终的提示信息。

**注意**: 
- 此函数依赖于 `st.session_state` 来获取当前对话模式和选中的知识库，因此在调用此函数之前，确保 `dialogue_mode` 和 `selected_kb`（如果在知识库问答模式下）已经被正确设置。
- `st.toast` 方法用于在界面上显示临时消息，这意味着提示信息会在短时间后自动消失，不会干扰用户的正常操作。
***
### FunctionDef on_llm_change
**on_llm_change**: 此函数用于处理语言模型变更事件。

**参数**: 此函数不接受任何参数。

**代码描述**: 当语言模型（Large Language Model，简称LLM）发生变更时，`on_llm_change`函数首先检查当前选中的模型（`llm_model`）是否存在。如果存在，它会通过调用`api.get_model_config(llm_model)`获取该模型的配置信息。此处的`api.get_model_config`函数是从`webui_pages/utils.py/ApiRequest/get_model_config`中调用的，其主要功能是获取服务器上指定模型的配置信息。

如果获取到的模型配置信息中`"online_api"`字段不存在，即判断为只有本地的`model_worker`可以切换模型，那么函数会将当前模型名称`llm_model`保存到`st.session_state["prev_llm_model"]`中，以便记录上一个模型。无论模型是否可以切换，当前选中的模型名称都会被保存到`st.session_state["cur_llm_model"]`中，这样可以确保系统记录了用户的最新选择。

**注意**:
- 本函数依赖于`st.session_state`来存储和跟踪语言模型的变更状态，因此需要确保在调用此函数之前已正确初始化`st.session_state`。
- 函数的执行依赖于外部API的响应，因此网络状况和服务器状态可能会影响到函数的执行结果。
- 由于函数内部没有直接的错误处理逻辑，如果`api.get_model_config`调用失败或返回的配置信息不符合预期，可能需要在调用此函数的上层逻辑中进行相应的错误处理。
***
### FunctionDef llm_model_format_func(x)
**llm_model_format_func**: 此函数的功能是格式化模型名称，如果模型正在运行中，则在模型名称后添加 "(Running)" 标记。

**参数**:
- **x**: 字符串类型，代表模型的名称。

**代码描述**:
`llm_model_format_func` 函数接收一个参数 `x`，这个参数是一个字符串，代表了模型的名称。函数首先会检查这个名称是否存在于 `running_models` 列表中，这个列表包含了当前正在运行的模型名称。如果 `x` 存在于 `running_models` 中，函数会返回模型名称后追加 " (Running)" 的字符串，以此来表示该模型当前正在运行。如果 `x` 不在 `running_models` 列表中，函数则直接返回传入的模型名称。

**注意**:
- 确保在调用此函数之前，`running_models` 列表已经被正确初始化并包含了所有当前正在运行的模型名称。
- 此函数的返回值依赖于 `running_models` 列表的当前状态，因此在使用此函数格式化模型名称前，请确保 `running_models` 列表是最新的。

**输出示例**:
- 假设 `running_models` 包含 "Model_A"，调用 `llm_model_format_func("Model_A")` 将返回 "Model_A (Running)"。
- 如果 `running_models` 不包含 "Model_B"，调用 `llm_model_format_func("Model_B")` 将返回 "Model_B"。
***
### FunctionDef prompt_change
**prompt_change**: 此函数的功能是显示一个提示信息，通知用户已经成功切换到了指定的模板。

**参数**: 此函数没有参数。

**代码描述**: `prompt_change` 函数首先定义了一个文本变量 `text`，该变量包含了一条格式化的消息，指出了当前已切换到的模板名称。这里使用了一个未在代码段中直接定义的变量 `prompt_template_name`，该变量应该在函数调用前被定义，且包含了模板的名称。接着，函数使用 `st.toast` 方法显示了一个短暂的通知，其内容为 `text` 变量中的消息。`st.toast` 方法是用于在界面上显示临时消息的一种方式，常用于反馈操作结果给用户。

**注意**: 在使用 `prompt_change` 函数之前，确保变量 `prompt_template_name` 已经被正确定义并且包含了有效的模板名称。此外，此函数依赖于 `st.toast` 方法，该方法是 Streamlit 库的一部分，因此确保你的项目中已经正确安装并导入了 Streamlit。此函数适用于需要向用户反馈模板切换操作结果的场景。
***
### FunctionDef on_kb_change
**on_kb_change**: 此函数的功能是在知识库更改时显示一个通知。

**参数**: 此函数不接受任何参数。

**代码描述**: `on_kb_change` 函数是一个没有参数的函数，用于在用户界面上显示一个临时通知。当知识库（Knowledge Base，简称KB）发生变化时，此函数被触发。它使用 `st.toast` 方法来显示一个通知，通知内容包括“已加载知识库：”以及当前选中的知识库名称。这里的 `st.session_state.selected_kb` 是一个会话状态变量，用于存储当前选中的知识库名称。`st.toast` 方法是一个简单而有效的方式，用于在用户界面上向用户提供即时反馈。

**注意**: 使用此函数时，需要确保 `st.session_state` 中有 `selected_kb` 这一项，并且其值为当前选中的知识库名称。此外，考虑到 `st.toast` 显示的通知是临时的，确保这种反馈方式适合您的应用场景。如果需要更持久的通知方式，可能需要考虑其他UI元素。
***
