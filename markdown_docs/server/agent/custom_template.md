## ClassDef CustomPromptTemplate
**CustomPromptTemplate**: CustomPromptTemplate类的功能是根据提供的模板和工具列表，格式化生成一个定制化的提示字符串。

**属性**:
- `template`: 字符串类型，用于定义提示信息的模板。
- `tools`: Tool对象的列表，每个Tool对象包含工具的名称和描述。

**代码描述**:
CustomPromptTemplate类继承自StringPromptTemplate，主要用于生成定制化的提示信息。它通过`format`方法接收关键字参数，其中`intermediate_steps`是一个列表，包含了动作和观察的元组。该方法首先将`intermediate_steps`中的信息格式化为字符串，然后将其以及工具的名称和描述添加到模板中，最后返回格式化后的字符串。

在项目中，CustomPromptTemplate类被用于`server/chat/agent_chat.py/agent_chat/agent_chat_iterator`中，以生成与用户交互的提示信息。通过提供的模板和工具列表，CustomPromptTemplate能够生成包含工具使用说明和中间步骤描述的提示信息，这对于指导用户如何与代理进行交互是非常有用的。特别是在异步的聊天环境中，准确和详细的提示信息能够极大地提升用户体验。

**注意**:
- 在使用CustomPromptTemplate时，需要确保传递给`format`方法的`intermediate_steps`参数格式正确，即包含动作和观察的元组列表。
- 工具列表`tools`应包含所有可能会在提示信息中提及的工具，每个工具都应有名称和描述。

**输出示例**:
假设有以下模板和工具列表：
- 模板：`"请使用以下工具：{tools}\n{agent_scratchpad}"`
- 工具列表：`[Tool(name="Tool1", description="This is tool 1"), Tool(name="Tool2", description="This is tool 2")]`
- `intermediate_steps`：`[("action1", "observation1"), ("action2", "observation2")]`

调用`format`方法后，可能返回的字符串为：
```
请使用以下工具：
Tool1: This is tool 1
Tool2: This is tool 2
action1
Observation: observation1
Thought: action2
Observation: observation2
Thought: 
```
### FunctionDef format(self)
**功能**: `format` 函数的功能是根据提供的参数和内部逻辑，格式化并返回一个字符串。

**参数**:
- `**kwargs`: 关键字参数，可以接受多个命名参数，用于动态传递给模板和内部逻辑处理。

**代码描述**:
该函数首先从传入的关键字参数（`kwargs`）中提取出`intermediate_steps`参数。`intermediate_steps`应该是一个包含动作和观察结果的元组列表。函数遍历这个列表，将每个动作的日志和对应的观察结果格式化为字符串，并拼接到`thoughts`字符串中。

接下来，函数将`thoughts`字符串添加到`kwargs`字典中，键名为`agent_scratchpad`。此外，还会处理`self.tools`，这是一个工具对象列表。函数将每个工具的名称和描述格式化为字符串，并将这些字符串以换行符连接，结果赋值给`kwargs`字典中的`tools`键。同时，将所有工具的名称提取出来，以逗号和空格连接成一个字符串，赋值给`kwargs`字典中的`tool_names`键。

最后，函数使用`self.template.format(**kwargs)`语句，将处理好的`kwargs`字典作为参数，传递给模板的`format`方法，并返回格式化后的字符串。

**注意**:
- 确保传入的`kwargs`中包含`intermediate_steps`键，且其值格式正确。
- `self.tools`应该是一个包含有`name`和`description`属性的对象列表。
- 该函数依赖于`self.template`的`format`方法，确保`self.template`已正确初始化并可以接受`kwargs`作为参数。

**输出示例**:
```plaintext
Action: Move Forward
Observation: Wall detected
Thought: 
Tool1: Used for cutting
Tool2: Used for digging
Tool Names: Tool1, Tool2
```
***
## ClassDef CustomOutputParser
**CustomOutputParser**: CustomOutputParser类的功能是解析大模型输出，并根据输出内容决定下一步操作。

**属性**:
- `begin`: 一个布尔值，用于指示解析过程是否应该开始或停止。

**代码描述**:
CustomOutputParser类继承自AgentOutputParser，是一个专门用于解析大模型输出的解析器。它通过分析模型的输出内容，来决定是继续执行某些操作，还是结束会话。具体来说，它会检查模型输出中是否包含特定的关键词或短语，如"Final Answer:"或"Action:"，并据此返回相应的操作指令。

在初始化时，`begin`属性被设置为True，表示解析器准备开始解析输出。在`parse`方法中，首先检查是否所有支持的代理模型都不在模型容器中，并且`begin`为True。如果条件满足，它会查找输出中的停止词（如"Observation:"），并根据这些停止词截断输出，以准备进一步的解析。

如果输出中包含"Final Answer:"，则表示大模型已经给出了最终答案，解析器将重置`begin`为True，并返回一个包含最终答案的AgentFinish对象。如果输出中包含"Action:"，则解析器会解析出相应的操作和输入，尝试执行该操作，并返回一个AgentAction对象。如果解析过程中遇到异常，或者输出不符合预期的格式，解析器将返回一个包含错误信息的AgentFinish对象。

**注意**:
- 在使用CustomOutputParser时，需要确保大模型的输出格式与解析器预期的格式相匹配，否则可能无法正确解析出操作指令。
- 解析器依赖于输出中的特定关键词或短语来决定操作，因此在设计大模型的输出格式时，需要考虑这一点。

**输出示例**:
假设大模型的输出为"Final Answer: 42"，CustomOutputParser解析后可能返回的对象为：
```
AgentFinish(return_values={"output": "42"}, log="Final Answer: 42")
```
如果大模型的输出为"Action: Calculate Action Input: 42 + 1"，解析后可能返回的对象为：
```
AgentAction(tool="Calculate", tool_input="42 + 1", log="Action: Calculate Action Input: 42 + 1")
```

在项目中，CustomOutputParser被用于解析大模型在与用户交互过程中的输出，以决定是否需要调用特定的工具或服务来辅助完成用户的请求。这使得整个系统能够更加智能和灵活地处理各种不同的用户需求。
### FunctionDef __init__(self)
**__init__**: 该函数用于初始化CustomOutputParser对象。

**参数**: 该函数不接受任何外部参数。

**代码描述**: 在CustomOutputParser类的__init__方法中，首先通过`super().__init__()`调用父类的构造函数来确保父类被正确初始化。接着，该方法设置了一个实例变量`self.begin`并将其初始化为True。这个变量可能用于标记解析开始，或者用于控制某些只在初始化时需要执行的操作。

**注意**: 在使用CustomOutputParser类时，不需要手动传递任何参数给__init__方法。创建对象后，可以根据实际需求修改`self.begin`的值，但通常情况下，该变量的初始值True已足够满足大多数使用场景。此外，如果CustomOutputParser类继承自一个具有复杂初始化逻辑的父类，`super().__init__()`确保了这些逻辑不会被遗漏。
***
### FunctionDef parse(self, llm_output)
**parse**: 此函数的功能是解析从大型语言模型（LLM）输出的文本，并根据输出内容决定下一步的操作。

**参数**:
- `llm_output`: 字符串类型，代表从大型语言模型（LLM）接收到的输出文本。

**代码描述**:
此函数首先检查是否有支持的代理模型存在于`model_container.MODEL`中，并且是否是开始解析。如果是开始解析且没有支持的代理模型，它会查找输出中的停止词（例如"Observation:"），并截取至第一个停止词之前的文本作为新的输出文本。

如果输出文本中包含"Final Answer:"，则表示大型语言模型已经给出了最终答案。此时，函数会将"Final Answer:"之后的文本作为输出，并标记为解析结束。

如果输出文本中包含"Action:"，则表示需要执行特定的动作。函数会解析出动作名称和动作输入，然后尝试执行该动作。如果执行成功，会返回一个`AgentAction`对象，包含动作名称、动作输入和原始日志。

如果上述条件都不满足，或者在解析动作时遇到异常，函数会返回一个`AgentFinish`对象，表示解析结束，同时包含错误信息或大模型自身的回答。

**注意**:
- 在使用此函数时，需要确保`model_container.MODEL`和`SUPPORT_AGENT_MODEL`已正确设置，以便函数能够正确判断是否有支持的代理模型。
- 函数的返回值类型可能是`AgentFinish`、`tuple[dict[str, str], str]`或`AgentAction`，调用者需要根据返回值类型进行相应的处理。

**输出示例**:
假设`llm_output`为"Final Answer: 42"，则函数可能返回的示例为：
```python
AgentFinish(return_values={"output": "42"}, log="Final Answer: 42")
```

如果`llm_output`为"Action: Email Action Input: john.doe@example.com"，则函数可能返回的示例为：
```python
AgentAction(tool="Email", tool_input="john.doe@example.com", log="Action: Email Action Input: john.doe@example.com")
```
***
