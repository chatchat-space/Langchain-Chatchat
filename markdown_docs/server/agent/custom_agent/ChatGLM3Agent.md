## ClassDef StructuredChatOutputParserWithRetries
**StructuredChatOutputParserWithRetries**: 该类的功能是为结构化聊天代理提供带有重试机制的输出解析。

**属性**:
- base_parser: 使用的基础解析器。
- output_fixing_parser: 使用的输出修正解析器，可选。

**代码描述**:
StructuredChatOutputParserWithRetries 类继承自 AgentOutputParser，主要用于解析结构化聊天代理的输出。它通过定义两个主要属性——base_parser 和 output_fixing_parser 来实现其功能。base_parser 是一个 StructuredChatOutputParser 实例，用于基本的输出解析。output_fixing_parser 是一个可选的 OutputFixingParser 实例，用于在必要时修正输出。

该类的核心方法是 parse，它接受一个字符串 text 作为输入，并尝试解析这个字符串以生成一个代理动作（AgentAction）或代理完成信号（AgentFinish）。解析过程首先尝试找到特殊标记（如 "Action:" 或 "<|observation|>"）的位置，然后根据是否包含 "tool_call" 来决定如何处理文本。如果包含 "tool_call"，则进一步解析以提取动作和参数；否则，直接将文本作为最终答案处理。解析完成后，根据 output_fixing_parser 的存在与否，选择相应的解析器进行最终解析。

在项目中，StructuredChatOutputParserWithRetries 被 StructuredGLM3ChatAgent 类作为默认的输出解析器使用。通过 StructuredGLM3ChatAgent 类的 _get_default_output_parser 方法，可以看出 StructuredChatOutputParserWithRetries 被用于构建结构化聊天代理，以处理语言模型（LLM）的输出并将其转换为适合代理处理的格式。

**注意**:
- 在使用 StructuredChatOutputParserWithRetries 类时，需要确保传入的文本格式符合预期，特别是当涉及到特殊标记和工具调用格式时。
- 如果提供了 output_fixing_parser，它将用于在基础解析失败或需要修正时进行二次解析。

**输出示例**:
```json
Action:
```
{
  "action": "Final Answer",
  "action_input": "这是解析后的文本"
}
```
在这个示例中，假设传入的文本不包含 "tool_call"，则 parse 方法将直接将文本视为最终答案，并构建相应的 JSON 字符串作为输出。
### FunctionDef parse(self, text)
**parse**: 此函数的功能是解析文本并生成相应的动作或最终答案。

**参数**:
- `text`: 需要解析的文本，类型为字符串。

**代码描述**:
此函数首先定义了一个包含特殊标记的列表`special_tokens`，这些特殊标记用于在文本中查找特定的位置。接着，它会找到这些特殊标记中第一个出现的位置，并将文本截断到这个位置，以便进一步处理。

如果文本中包含"tool_call"，则认为这是一个需要执行的动作。函数会找到动作描述结束的位置（即"```"的位置），并提取出动作名称和参数。参数会被解析成键值对的形式，并存储在一个字典中。然后，这些信息会被组织成一个JSON对象，准备进行下一步的解析。

如果文本中不包含"tool_call"，则认为这是一个最终答案，直接将文本作为动作输入，动作名称设为"Final Answer"。

之后，函数会根据是否存在`output_fixing_parser`来决定使用哪个解析器进行解析。如果存在，就使用`output_fixing_parser`解析器，否则使用`base_parser`解析器。解析的结果会被返回。

**注意**:
- 在使用此函数时，需要确保传入的文本格式正确，特别是当文本中包含动作描述时，需要遵循特定的格式（例如，动作和参数的正确分隔）。
- 如果在解析过程中遇到任何异常，函数会抛出`OutputParserException`异常，异常信息中会包含无法解析的原始文本。

**输出示例**:
假设文本内容为一个动作调用，解析后可能的返回值为：
```json
{
  "action": "tool_call_example",
  "action_input": {
    "param1": "value1",
    "param2": "value2"
  }
}
```
如果文本内容为最终答案，解析后可能的返回值为：
```json
{
  "action": "Final Answer",
  "action_input": "这是一个最终答案的示例文本。"
}
```
***
### FunctionDef _type(self)
**_type**: 该函数的功能是返回一个特定的字符串。

**参数**: 此函数没有参数。

**代码描述**: `_type` 函数是一个非常简单的方法，其主要目的是返回一个预定义的字符串。这个字符串代表了一个特定的类型标识，即 "structured_chat_ChatGLM3_6b_with_retries"。这个标识通常用于区分不同的处理逻辑或数据格式。在这个上下文中，它可能表示使用了特定配置或策略的聊天模型，特别是指一个结构化的聊天输出解析器，该解析器配置了重试机制。这种类型的标识对于维护代码的清晰度和可维护性非常重要，因为它允许开发者快速识别和理解代码块的用途和行为。

**注意**: 使用此函数时，需要注意它返回的字符串是硬编码的，这意味着如果未来需要更改类型标识，将需要直接修改此函数的返回值。因此，维护此部分代码时应谨慎，确保任何更改都不会影响依赖此标识的其他代码逻辑。

**输出示例**: 调用 `_type` 函数将返回以下字符串：
```
"structured_chat_ChatGLM3_6b_with_retries"
```
***
## ClassDef StructuredGLM3ChatAgent
**StructuredGLM3ChatAgent**: 该类的功能是实现一个结构化的聊天代理，用于处理和响应基于ChatGLM3-6B模型的对话。

**属性**:
- output_parser: 用于解析代理输出的解析器，默认为StructuredChatOutputParserWithRetries实例。
- observation_prefix: 用于在ChatGLM3-6B观察结果前添加的前缀字符串。
- llm_prefix: 用于在语言模型调用前添加的前缀字符串。

**代码描述**:
StructuredGLM3ChatAgent 类继承自 Agent 类，提供了结构化聊天代理的实现。它通过定义特定的属性和方法来处理与语言模型（LLM）的交互，生成提示（prompt），并解析LLM的输出。

- **属性定义**:
  - `output_parser` 属性指定了用于解析代理输出的解析器，其默认值为 StructuredChatOutputParserWithRetries 类的实例，该解析器提供了带有重试机制的输出解析功能。
  - `observation_prefix` 和 `llm_prefix` 属性分别定义了在观察结果和语言模型调用前添加的前缀字符串，用于格式化生成的提示。

- **方法分析**:
  - `_construct_scratchpad` 方法用于构建代理的草稿本，它基于中间步骤生成一个字符串，用于记录代理的工作过程。
  - `_get_default_output_parser` 类方法返回一个默认的输出解析器实例，用于解析语言模型的输出。
  - `create_prompt` 类方法用于根据提供的工具和输入变量生成提示模板，该方法将工具的信息和其他输入变量格式化为一个字符串模板，用于生成语言模型的输入。
  - `from_llm_and_tools` 类方法用于根据语言模型和工具集合构建一个StructuredGLM3ChatAgent实例，它通过组合语言模型、工具和其他参数来初始化代理。

**注意**:
- 在使用 StructuredGLM3ChatAgent 类时，需要确保提供的工具和语言模型与代理的目标任务相匹配。
- 输出解析器（output_parser）应该能够准确解析语言模型的输出，以便代理能够正确响应用户的输入。
- 在构建提示时，应注意格式化字符串模板，确保它们能够正确地被语言模型理解和处理。

**输出示例**:
假设代理接收到的输入是一个简单的问答任务，输出示例可能如下：
```
{
  "action": "Final Answer",
  "action_input": "这是代理基于语言模型输出解析后的回答"
}
```
在这个示例中，代理通过解析语言模型的输出，生成了一个包含最终回答的动作（Action）和相应输入（action_input）的JSON对象。
### FunctionDef observation_prefix(self)
**observation_prefix**: 此函数的功能是生成并返回ChatGLM3-6B观察的前缀字符串。

**参数**: 此函数不接受任何参数。

**代码描述**: `observation_prefix`函数是`StructuredGLM3ChatAgent`类的一个方法，它的主要作用是为ChatGLM3-6B模型的观察提供一个统一的前缀。这个前缀用于在处理聊天或对话数据时，标识出哪些内容是观察到的信息。在这个函数中，返回的字符串是"Observation:"，这意味着所有通过此方法处理的观察数据将以"Observation:"作为开头。这有助于模型识别和处理输入数据，确保数据格式的一致性和准确性。

**注意**: 使用此函数时，需要注意它返回的前缀字符串是固定的。如果在不同的上下文或应用中需要不同的前缀，可能需要对此函数进行相应的修改或扩展。

**输出示例**: 调用`observation_prefix`函数将返回以下字符串：
```
Observation:
```
***
### FunctionDef llm_prefix(self)
**llm_prefix函数功能**: 该函数的功能是生成并返回一个用于在调用大型语言模型(llm)时附加的前缀字符串。

**参数**: 该函数没有参数。

**代码描述**: `llm_prefix`函数定义在`StructuredGLM3ChatAgent`类中，是一个简单的成员函数，不接受任何参数，并且返回一个固定的字符串`"Thought:"`。这个字符串作为前缀，其目的是在向大型语言模型(llm)发起调用时，附加到实际的查询或命令之前，以此来可能影响或指定模型的回应方式。这种做法在与大型语言模型交互时很常见，用于引导模型的回应更加符合期望的上下文或风格。

**注意**: 使用`llm_prefix`函数时，需要注意的是，返回的前缀字符串`"Thought:"`是硬编码的，这意味着在不同的应用场景下，如果需要不同的前缀来引导大型语言模型的回应，可能需要修改这个函数的返回值。此外，这个前缀的有效性和适用性可能会随着大型语言模型的不同或者模型训练数据的更新而变化，因此在实际应用中需要根据模型的具体表现来调整。

**输出示例**: 调用`llm_prefix`函数将返回字符串`"Thought:"`。

通过上述分析，开发者和初学者可以了解到`llm_prefix`函数的作用、使用方法以及需要注意的事项。这有助于在使用`StructuredGLM3ChatAgent`类与大型语言模型进行交互时，能够更有效地引导模型的回应，从而提高交互的质量和效果。
***
### FunctionDef _construct_scratchpad(self, intermediate_steps)
**_construct_scratchpad**: 此函数的功能是构建并返回一个代表中间步骤的字符串。

**参数**:
- **intermediate_steps**: 一个列表，包含元组，每个元组由AgentAction和字符串组成，代表中间的操作步骤。

**代码描述**:
`_construct_scratchpad` 函数首先调用其父类的 `_construct_scratchpad` 方法，传入中间步骤的数据（`intermediate_steps`），并接收返回的字符串（`agent_scratchpad`）。此字符串代表了到目前为止的工作进展。函数接着检查 `agent_scratchpad` 是否为字符串类型，如果不是，则抛出 `ValueError` 异常，确保后续操作的数据类型正确性。

如果 `agent_scratchpad` 非空，函数将返回一个格式化的字符串，该字符串以一种友好的方式向用户展示之前的工作成果，即使实际上这个函数并没有直接访问到这些成果，只是通过参数传递得到的信息。如果 `agent_scratchpad` 为空，则直接返回该空字符串。

**注意**:
- 确保传入的 `intermediate_steps` 参数格式正确，即列表中包含的元素为元组，且元组包含的是 `AgentAction` 和字符串。
- 此函数假设父类的 `_construct_scratchpad` 方法已正确实现并能返回一个字符串。如果父类方法的实现发生变化，可能需要相应地调整此函数。

**输出示例**:
如果 `intermediate_steps` 包含了一系列的操作步骤，且父类方法返回了这些步骤的字符串表示，例如 "Step 1: Do something; Step 2: Do something else;"，那么此函数可能返回的字符串示例为：

```
"This was your previous work (but I haven't seen any of it! I only see what you return as final answer):
Step 1: Do something; Step 2: Do something else;"
```
***
### FunctionDef _get_default_output_parser(cls, llm)
**_get_default_output_parser**: 该函数的功能是获取默认的输出解析器。

**参数**:
- `llm`: 可选参数，类型为 `BaseLanguageModel`，表示基础语言模型。
- `**kwargs`: 接受任意数量的关键字参数。

**代码描述**: `_get_default_output_parser` 函数是 `StructuredGLM3ChatAgent` 类的一个类方法，用于获取默认的输出解析器。该方法接受一个可选的语言模型实例 `llm` 和任意数量的关键字参数 `**kwargs`。函数体内部，它创建并返回一个 `StructuredChatOutputParserWithRetries` 实例，将 `llm` 作为参数传递给该实例。`StructuredChatOutputParserWithRetries` 类是专门为结构化聊天代理设计的输出解析器，具有重试机制，能够处理语言模型的输出并将其转换为适合代理处理的格式。

在项目中，`_get_default_output_parser` 方法被 `from_llm_and_tools` 方法调用，以获取默认的输出解析器实例。如果在创建 `StructuredGLM3ChatAgent` 实例时没有明确指定输出解析器，则会通过调用 `_get_default_output_parser` 方法来获取默认的输出解析器实例，并将其用于处理语言模型的输出。

**注意**:
- 在使用 `_get_default_output_parser` 方法时，需要确保传入的 `llm` 参数（如果有）是一个有效的语言模型实例。
- 该方法设计为灵活接受任意数量的关键字参数 `**kwargs`，但在当前实现中并未直接使用这些额外的参数。开发者在扩展或修改方法时可以根据需要利用这些参数。

**输出示例**: 由于 `_get_default_output_parser` 方法返回的是一个 `StructuredChatOutputParserWithRetries` 实例，因此输出示例将依赖于该实例的具体实现。假设 `llm` 参数为 `None`，调用 `_get_default_output_parser` 方法将返回一个不带语言模型实例的 `StructuredChatOutputParserWithRetries` 实例。
***
### FunctionDef _stop(self)
**_stop函数的功能**: `_stop`函数的目的是结束当前的会话并返回一个特定的标记列表。

**参数**: 此函数没有参数。

**代码描述**: `_stop`函数是`StructuredGLM3ChatAgent`类的一个私有方法，用于在聊天代理的会话中标记结束点。当调用此函数时，它会返回一个包含单个字符串元素`"<|observation|>"`的列表。这个返回值通常用于指示聊天模型的会话已经结束，或者需要进行某种形式的重置或观察。在聊天代理的上下文中，这个特定的字符串可能被用作一个信号或标记，以触发特定的行为或处理逻辑。

**注意**: 虽然`_stop`函数的实现看起来简单，但它在聊天代理的逻辑中可能扮演着关键角色。使用时需要确保聊天模型或处理逻辑能够正确识别并处理返回的`"<|observation|>"`标记。此外，由于`_stop`是一个私有方法，它仅在`StructuredGLM3ChatAgent`类的内部被调用，不应该直接从类的实例外部访问或调用。

**输出示例**: 调用`_stop`函数可能会返回如下列表：
```python
["<|observation|>"]
```
这个列表包含一个字符串元素，即`"<|observation|>"`，用于表示聊天会话的结束或需要进行观察的状态。
***
### FunctionDef create_prompt(cls, tools, prompt, input_variables, memory_prompts)
**create_prompt**: 此函数的功能是基于提供的工具和模板参数构建聊天提示模板。

**参数**:
- `tools`: 一个实现了BaseTool接口的对象序列，代表聊天代理可以使用的工具。
- `prompt`: 一个字符串模板，用于格式化最终的提示信息。
- `input_variables`: 一个字符串列表，指定输入变量的名称，默认为None。
- `memory_prompts`: 一个BasePromptTemplate对象的列表，用于提供记忆提示，默认为None。

**代码描述**:
`create_prompt`函数首先遍历`tools`参数中的每个工具，提取其名称、描述和参数模式，并将这些信息格式化为一个简化的JSON结构。这个结构包括工具的名称、描述和参数。接着，函数将这些工具信息格式化为一个字符串，其中每个工具的信息占据一行，包括其名称、描述和参数。这个格式化的字符串以及其他提供的模板参数（如工具名称列表、历史记录、输入和代理草稿板）被用来填充`prompt`模板字符串。

如果`input_variables`未指定，则默认为`["input", "agent_scratchpad"]`。`memory_prompts`参数允许将额外的提示信息加入到最终的提示模板中，这些信息可以是之前的对话历史或其他重要信息。

最后，函数使用格式化后的提示信息和输入变量列表创建一个`ChatPromptTemplate`对象，并将其返回。这个返回的对象可以直接用于生成聊天代理的提示信息。

在项目中，`create_prompt`函数被`from_llm_and_tools`方法调用，用于根据语言模型（LLM）和工具集合构建一个聊天代理。这表明`create_prompt`函数在构建聊天代理的初始化过程中起着核心作用，特别是在准备聊天代理的提示模板方面。

**注意**:
- 确保`prompt`参数提供的模板字符串正确地使用了所有预期的变量，以避免格式化时出现错误。
- `tools`参数中的工具对象需要实现`BaseTool`接口，确保它们具有`name`、`description`和`args_schema`属性。

**输出示例**:
假设有两个工具，分别为"Calculator"和"Translator"，且`prompt`参数为"Available tools: {tools}\nInput: {input}"，则函数可能返回的`ChatPromptTemplate`对象中的`messages`属性可能包含以下字符串：

```
Available tools:
Calculator: A simple calculator, args: {'number1': 'Number', 'number2': 'Number'}
Translator: Translates text from one language to another, args: {'text': 'String', 'target_language': 'String'}
Input: {input}
```
***
### FunctionDef from_llm_and_tools(cls, llm, tools, prompt, callback_manager, output_parser, human_message_template, input_variables, memory_prompts)
**from_llm_and_tools**: 该函数的功能是从语言模型(LLM)和工具集合构建一个聊天代理。

**参数**:
- `cls`: 类方法的第一个参数，指代当前类。
- `llm`: `BaseLanguageModel`的实例，表示基础语言模型。
- `tools`: 实现了`BaseTool`接口的对象序列，代表聊天代理可以使用的工具。
- `prompt`: 字符串类型，用于格式化最终的提示信息，默认为None。
- `callback_manager`: `BaseCallbackManager`的实例，用于管理回调函数，默认为None。
- `output_parser`: `AgentOutputParser`的实例，用于解析代理输出，默认为None。
- `human_message_template`: 字符串类型，表示人类消息模板，默认为`HUMAN_MESSAGE_TEMPLATE`。
- `input_variables`: 字符串列表，指定输入变量的名称，默认为None。
- `memory_prompts`: `BasePromptTemplate`对象的列表，用于提供记忆提示，默认为None。
- `**kwargs`: 接受任意数量的关键字参数。

**代码描述**:
`from_llm_and_tools`函数首先验证提供的工具集合是否有效。然后，它调用`create_prompt`方法来创建聊天提示模板，该模板基于提供的工具、提示、输入变量和记忆提示。接着，使用`llm`、生成的`prompt`和`callback_manager`创建一个`LLMChain`实例。此外，函数从工具集合中提取工具名称，并尝试获取默认的输出解析器，如果未提供`output_parser`参数，则调用`_get_default_output_parser`方法获取默认解析器。最后，使用这些组件构建并返回一个`StructuredGLM3ChatAgent`实例。

**注意**:
- 确保提供的`llm`和`tools`参数是有效的实例，且`tools`中的每个工具都实现了`BaseTool`接口。
- 如果在调用时未指定`output_parser`，则会自动使用默认的输出解析器。
- `**kwargs`参数提供了额外的灵活性，允许在创建代理时传递额外的配置选项。

**输出示例**:
由于`from_llm_and_tools`函数返回的是一个`StructuredGLM3ChatAgent`实例，因此输出示例将依赖于该实例的具体实现。例如，如果使用默认参数调用此函数，将返回一个配置了基础语言模型、指定工具集合和默认输出解析器的`StructuredGLM3ChatAgent`实例。这个实例可以直接用于处理聊天对话，执行工具命令，并解析语言模型的输出。
***
### FunctionDef _agent_type(self)
**_agent_type**: 该函数的功能是抛出一个 ValueError 异常。

**参数**: 此函数不接受任何参数。

**代码描述**: `_agent_type` 函数是 `StructuredGLM3ChatAgent` 类的一个私有方法，其设计初衷是为了在子类中被重写，用以指定或返回特定的代理类型字符串。在其原始形态中，此函数直接抛出一个 `ValueError` 异常，这表明如果直接调用此方法而没有在子类中进行适当的重写，则会明确地指出这一点。这是一种常见的编程模式，用于强制要求子类实现特定的方法。

**注意**: 在使用 `StructuredGLM3ChatAgent` 类或其任何子类时，开发者需要确保 `_agent_type` 方法被正确重写以避免运行时错误。此方法的存在强调了一个设计原则，即某些方法是专门设计给子类来实现的，而不是直接在父类中使用。因此，如果你在开发过程中遇到了 `ValueError`，这可能是因为你尝试调用了一个应该被子类重写的方法，但是没有这样做。
***
## FunctionDef initialize_glm3_agent(tools, llm, prompt, memory, agent_kwargs)
**initialize_glm3_agent**: 该函数的功能是初始化一个基于GLM3模型的聊天代理。

**参数**:
- `tools`: 实现了`BaseTool`接口的对象序列，代表聊天代理可以使用的工具。
- `llm`: `BaseLanguageModel`的实例，表示基础语言模型。
- `prompt`: 字符串类型，用于格式化最终的提示信息，默认为None。
- `memory`: `ConversationBufferWindowMemory`的实例，用于存储聊天历史，默认为None。
- `agent_kwargs`: 字典类型，包含创建聊天代理时需要的额外参数，默认为None。
- `tags`: 字符串序列，用于标记或分类代理，默认为None。
- `**kwargs`: 接受任意数量的关键字参数，提供额外的配置选项。

**代码描述**:
`initialize_glm3_agent`函数首先检查是否提供了`tags`参数，并将其转换为列表形式。然后，检查`agent_kwargs`参数是否为None，如果是，则将其初始化为空字典。接下来，使用`StructuredGLM3ChatAgent.from_llm_and_tools`类方法创建一个`StructuredGLM3ChatAgent`实例，该实例基于提供的语言模型、工具集合、提示信息以及`agent_kwargs`中的其他参数。最后，使用`AgentExecutor.from_agent_and_tools`方法创建并返回一个`AgentExecutor`实例，该实例包含了刚刚创建的聊天代理、工具集合、聊天历史以及标签。

**注意**:
- 在使用`initialize_glm3_agent`函数时，确保提供的`tools`和`llm`参数是有效的实例，且`tools`中的每个工具都实现了`BaseTool`接口。
- `prompt`参数允许自定义聊天代理的提示信息，可以根据需要提供。
- `memory`参数用于存储和管理聊天历史，有助于实现更连贯的对话。
- `agent_kwargs`和`**kwargs`提供了额外的灵活性，允许在创建聊天代理时传递额外的配置选项。

**输出示例**:
假设调用`initialize_glm3_agent`函数并提供了必要的参数，可能会返回如下的`AgentExecutor`实例：
```
AgentExecutor(
    agent=StructuredGLM3ChatAgent(...),
    tools=[...],
    memory=ConversationBufferWindowMemory(...),
    tags=['example_tag']
)
```
在这个示例中，`AgentExecutor`实例包含了一个配置好的`StructuredGLM3ChatAgent`聊天代理，以及相关的工具集合、聊天历史和标签。这个实例可以直接用于处理聊天对话，执行工具命令，并解析语言模型的输出。
