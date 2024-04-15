## ClassDef History
**History**: History 类用于表示对话历史记录。

**属性**:
- `role`: 表示发言角色，类型为字符串。
- `content`: 表示发言内容，类型为字符串。

**代码描述**:
History 类继承自 BaseModel，用于封装对话中的单条历史记录，包括发言角色和发言内容。它提供了将历史记录转换为消息元组的方法 `to_msg_tuple`，以及将历史记录转换为消息模板的方法 `to_msg_template`。此外，还提供了一个类方法 `from_data`，用于从不同类型的数据结构（列表、元组、字典）创建 History 实例。

在项目中，History 类被广泛用于处理和存储对话历史记录。例如，在 `agent_chat` 和 `chat` 等功能中，通过将用户输入和历史对话记录作为参数传递给模型，以生成相应的回复。这些历史记录通过 History 类的实例来管理和传递，确保了数据的一致性和易用性。

**注意**:
- 在使用 `to_msg_tuple` 方法时，如果 `role` 属性为 "assistant"，则返回的元组中角色部分为 "ai"，否则为 "human"，这有助于在处理对话时区分用户和助手的发言。
- `to_msg_template` 方法支持根据是否需要原始内容（`is_raw` 参数）来调整内容的格式，这在需要对内容进行特定格式处理时非常有用。
- `from_data` 类方法提供了灵活的数据转换功能，允许从多种数据源创建 History 实例，增加了代码的通用性和灵活性。

**输出示例**:
假设有以下历史记录数据：
```python
data = {"role": "user", "content": "你好"}
```
使用 History 类创建实例并转换为消息元组：
```python
h = History.from_data(data)
print(h.to_msg_tuple())
```
可能的输出为：
```
('human', '你好')
```
转换为消息模板时，假设不需要原始内容处理：
```python
print(h.to_msg_template(is_raw=False))
```
输出将根据实际的模板格式化内容，其中角色和内容将被相应地替换和处理。
### FunctionDef to_msg_tuple(self)
**to_msg_tuple**: 此函数的功能是将消息对象转换为一个包含角色和内容的元组。

**参数**: 此函数没有显式参数，但隐式使用了self参数，代表调用此函数的History对象实例。

**代码描述**: `to_msg_tuple`函数是History类的一个方法，用于将消息对象的角色和内容转换成一个元组。此函数首先检查消息对象的`role`属性。如果`role`属性值为"assistant"，则元组的第一个元素为字符串"ai"；否则，第一个元素为字符串"human"。元组的第二个元素是消息对象的`content`属性值，即消息的内容。这样，通过`to_msg_tuple`方法可以快速地获取消息的角色和内容信息，便于后续处理或显示。

**注意**: 使用此函数时，需要确保调用它的History对象实例已经正确设置了`role`和`content`属性，否则可能会遇到属性不存在的错误。

**输出示例**: 假设一个History对象实例的`role`属性为"assistant"，`content`属性为"你好，我是AI助手。"，那么调用`to_msg_tuple`方法的返回值将会是：

```python
("ai", "你好，我是AI助手。")
```

如果`role`属性为其他值，比如"user"，并且`content`属性为"这是一个用户消息。"，那么返回值将会是：

```python
("human", "这是一个用户消息。")
```

这种方式使得消息的角色和内容可以被快速地识别和使用，对于消息处理和展示非常有用。
***
### FunctionDef to_msg_template(self, is_raw)
**to_msg_template**: 该函数的功能是将历史消息转换为特定的消息模板格式。

**参数**:
- `is_raw`: 布尔值，指示是否将消息内容作为原始文本处理。默认为True。

**代码描述**:
`to_msg_template`函数是`History`类的一个方法，用于将历史消息转换为`ChatMessagePromptTemplate`格式，以便进一步处理和使用。该函数首先定义了一个角色映射字典`role_maps`，将"ai"映射为"assistant"，将"human"映射为"user"。然后，根据`History`对象的`role`属性查找相应的角色，如果找不到，则使用`role`属性的原始值。

根据`is_raw`参数的值，函数决定是否将消息内容包裹在"{% raw %}"和"{% endraw %}"标签中。这主要用于处理消息内容中可能包含的Jinja2模板标签，以避免在后续处理中被错误地解释或执行。如果`is_raw`为True，则消息内容被包裹；否则，保持原样不变。

最后，函数使用`ChatMessagePromptTemplate.from_template`方法，将处理后的内容、"jinja2"字符串（表示使用的模板类型）和角色作为参数，创建并返回一个`ChatMessagePromptTemplate`对象。

在项目中，`to_msg_template`方法被多个异步迭代器函数调用，这些函数负责处理不同类型的聊天会话，如`chat_iterator`、`knowledge_base_chat_iterator`和`search_engine_chat_iterator`等。在这些函数中，`to_msg_template`方法用于将历史消息或用户输入转换为适合模型处理的格式，进而生成聊天提示或查询模板。

**注意**:
- 当使用`to_msg_template`方法时，需要注意`is_raw`参数的使用场景。如果消息内容中包含需要保留的模板标签，则应将`is_raw`设置为True。
- 该方法依赖于`ChatMessagePromptTemplate.from_template`方法，因此需要确保`ChatMessagePromptTemplate`类及其方法的正确实现。

**输出示例**:
假设有一个`History`对象，其`role`为"human"，`content`为"Hello, AI!"，调用`to_msg_template(False)`可能会返回如下`ChatMessagePromptTemplate`对象：
```python
ChatMessagePromptTemplate(content="Hello, AI!", template_type="jinja2", role="user")
```
***
### FunctionDef from_data(cls, h)
**from_data**: 该函数用于根据提供的数据创建一个History对象。

**参数**:
- `h`: 可以是列表、元组或字典类型，用于初始化History对象的数据。

**代码描述**:
`from_data`函数是一个类方法，用于根据不同类型的输入数据创建一个History对象。该函数接受一个参数`h`，这个参数可以是列表、元组或字典类型。如果`h`是列表或元组，并且长度至少为2，那么会使用列表或元组的前两个元素作为History对象的`role`和`content`属性进行初始化。如果`h`是字典类型，那么会将字典中的键值对作为参数通过解包的方式传递给History类的构造函数，从而创建History对象。无论输入数据的类型如何，该函数最终都会返回一个History对象。

在项目中，`from_data`函数被多个地方调用，用于将用户的输入或历史对话数据转换为History对象，以便后续处理。例如，在`agent_chat`、`chat_iterator`、`file_chat`、`knowledge_base_chat`和`search_engine_chat`等函数中，都可以看到`from_data`函数的调用，它们通过这个函数将传入的历史对话列表转换为History对象列表，以便进行进一步的处理和分析。

**注意**:
- 当输入参数`h`为列表或元组时，至少需要包含两个元素，分别代表角色和内容，否则无法正确创建History对象。
- 当输入参数`h`为字典时，需要确保字典中包含的键与History类的构造函数参数相匹配，以便正确初始化对象。

**输出示例**:
假设输入参数`h`为列表`["user", "今天天气怎么样？"]`，则函数返回的History对象将具有属性`role="user"`和`content="今天天气怎么样？"`。如果输入参数`h`为字典`{"role": "assistant", "content": "今天是晴天。"}`，则返回的History对象将具有相同的属性值。
***
