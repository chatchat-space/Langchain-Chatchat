## FunctionDef search_knowledge_base_iter(database, query)
**search_knowledge_base_iter**: 该函数用于异步迭代地搜索知识库并获取相关信息。

**参数**:
- `database`: 字符串类型，指定要搜索的知识库名称。
- `query`: 字符串类型，用户的查询字符串。

**代码描述**:
`search_knowledge_base_iter` 函数是一个异步函数，它接受两个参数：`database` 和 `query`。这个函数主要通过调用 `knowledge_base_chat` 函数来实现与知识库的交互。在调用 `knowledge_base_chat` 时，会传入相关参数，包括知识库名称、查询字符串、模型名称、温度参数、历史记录、向量搜索的 top_k 值、最大 token 数、prompt 名称、分数阈值以及是否以流的形式输出。这些参数的具体值部分来自于全局变量或函数外部的变量。

函数内部通过异步迭代 `response.body_iterator` 来逐个处理返回的数据。每次迭代得到的数据是一个 JSON 字符串，包含了回答和相关文档信息。函数将这些回答累加起来，并在最后返回累加后的字符串。

**注意**:
- 该函数是异步的，因此在调用时需要使用 `await` 关键字。
- 函数内部处理了 JSON 数据，因此需要导入 `json` 模块。
- 在使用该函数之前，需要确保 `knowledge_base_chat` 函数及其所需的环境和参数已经正确配置和初始化。

**输出示例**:
调用 `search_knowledge_base_iter` 函数可能返回的字符串示例：
```
"这是根据您的查询生成的回答。出处 [1] [文档名称](文档链接) \n\n文档内容\n\n未找到相关文档,该回答为大模型自身能力解答！"
```
该字符串包含了所有回答的累加结果，如果有相关文档，还会包含文档的链接和内容。如果没有找到相关文档，会有相应的提示信息。
## FunctionDef search_knowledge_multiple(queries)
**search_knowledge_multiple**: 该函数用于异步地搜索多个知识库并获取相关信息。

**参数**:
- `queries`: 一个列表，包含多个元组，每个元组包含一个数据库名称和一个查询字符串。

**代码描述**:
`search_knowledge_multiple` 函数是一个异步函数，它接收一个包含多个（数据库名称，查询字符串）元组的列表作为参数。函数内部首先会为列表中的每个查询创建一个异步任务，这些任务是通过调用 `search_knowledge_base_iter` 函数实现的，该函数负责与指定的知识库进行交互并获取查询结果。之后，使用 `asyncio.gather` 函数并行执行这些异步任务，并等待所有任务完成，收集它们的结果。

对于每个查询的结果，函数会生成一个包含自定义消息和查询结果的字符串。这个自定义消息包括了知识库的名称，以及一个提示信息，表明这些信息是从哪个知识库查询到的。所有这些生成的字符串会被收集到一个列表中，并作为函数的返回值。

**注意**:
- 由于 `search_knowledge_multiple` 是一个异步函数，因此在调用它时需要使用 `await` 关键字。
- 函数的执行依赖于 `search_knowledge_base_iter` 函数，后者需要正确配置和初始化，包括知识库的访问设置和查询参数。
- 该函数的设计使得可以同时对多个知识库进行查询，提高了查询效率。

**输出示例**:
调用 `search_knowledge_multiple` 函数可能返回的列表示例：
```
[
    "\n查询到 database1 知识库的相关信息:\n这是根据您的查询生成的回答。出处 [1] [文档名称](文档链接) \n\n文档内容\n\n未找到相关文档,该回答为大模型自身能力解答！",
    "\n查询到 database2 知识库的相关信息:\n这是根据您的查询生成的回答。出处 [1] [文档名称](文档链接) \n\n文档内容\n\n未找到相关文档,该回答为大模型自身能力解答！"
]
```
该输出示例展示了当对两个不同的知识库进行查询时，每个查询结果前都会添加一个指明知识库来源的自定义消息，随后是查询到的具体信息。
## FunctionDef search_knowledge(queries)
Doc is waiting to be generated...
## ClassDef LLMKnowledgeChain
Doc is waiting to be generated...
### ClassDef Config
**Config**: Config 类的功能是定义一个严格的配置模式，用于pydantic对象。

**属性**:
- `extra`: 控制额外字段的处理方式。
- `arbitrary_types_allowed`: 允许使用任意类型的字段。

**代码描述**:
Config 类是一个配置类，专门用于在使用pydantic库时定义模型的配置。在这个类中，定义了两个重要的配置项：

1. `extra = Extra.forbid`：这个配置项用于指定当传入的数据包含模型未声明的字段时应如何处理。通过设置为`Extra.forbid`，表示禁止传入额外的字段，如果尝试传入未在模型中声明的字段，将会引发错误。这有助于确保数据的严格匹配和类型安全，避免因数据错误或不匹配而导致的问题。

2. `arbitrary_types_allowed = True`：这个配置项允许在模型中使用任意类型的字段。默认情况下，pydantic要求所有字段的类型都是预先定义好的，但开启这个选项后，可以使用任何类型的字段，包括自定义类型。这提供了更大的灵活性，允许开发者根据需要在模型中使用各种复杂或自定义的数据类型。

**注意**:
- 使用`extra = Extra.forbid`时，需要确保所有传入的数据严格匹配模型定义的字段，否则会引发错误。这要求开发者在设计模型和处理数据时需要更加小心和精确。
- 开启`arbitrary_types_allowed = True`可以提高模型的灵活性，但同时也需要开发者确保自定义类型的正确使用和处理，以避免类型错误或其他潜在问题。
***
### FunctionDef raise_deprecation(cls, values)
**raise_deprecation**: 此函数的功能是在使用已弃用方法实例化LLMKnowledgeChain时发出警告，并在适当的情况下自动转换为推荐的实例化方法。

**参数**:
- `cls`: 类方法的第一个参数，表示类本身。
- `values`: 一个字典，包含实例化LLMKnowledgeChain时传递的参数。

**代码描述**:
`raise_deprecation` 函数首先检查传入的 `values` 字典中是否包含键 `"llm"`。如果存在，这意味着尝试使用已弃用的方法直接通过 `llm` 参数实例化 `LLMKnowledgeChain`。此时，函数会发出一个警告，提示开发者这种实例化方法已弃用，并建议使用 `llm_chain` 参数或 `from_llm` 类方法作为替代。

如果在 `values` 中同时不存在 `"llm_chain"` 键，且 `"llm"` 键对应的值不为 `None`，函数会进一步处理。它会尝试从 `values` 中获取 `"prompt"` 键的值，如果不存在，则使用全局变量 `PROMPT` 的值。然后，利用 `llm` 和 `prompt` 的值创建一个 `LLMChain` 实例，并将这个实例赋值给 `values` 字典中的 `"llm_chain"` 键。

最后，函数返回更新后的 `values` 字典。

**注意**:
- 使用此函数时，应确保传入的 `values` 字典中的 `"llm"` 键（如果存在）对应的值是有效的，因为这将影响到 `LLMChain` 实例的创建。
- 应避免直接使用已弃用的实例化方法，以免在未来的版本中遇到兼容性问题。

**输出示例**:
假设传入的 `values` 字典为 `{"llm": some_llm_object}`，且 `PROMPT` 为默认提示文本，函数可能返回如下的字典：
```python
{
    "llm": some_llm_object,
    "llm_chain": LLMChain(llm=some_llm_object, prompt=默认提示文本)
}
```
这表明，即使最初尝试使用已弃用的方法实例化，函数也会自动调整，确保以推荐的方式实例化 `LLMKnowledgeChain`。
***
### FunctionDef input_keys(self)
**函数功能**: `input_keys` 的功能是返回期望的输入键列表。

**参数**: 此函数没有参数。

**代码描述**: `input_keys` 函数是 `LLMKnowledgeChain` 类的一个方法，它的主要作用是返回一个包含单个元素的列表，这个元素是该实例的 `input_key` 属性。这个方法被标记为私有，意味着它仅在 `LLMKnowledgeChain` 类的内部使用，不建议在类的外部直接调用这个方法。这种设计通常用于封装和隐藏类的内部实现细节，确保类的公共接口的简洁性和稳定性。

**注意**: 由于 `input_keys` 方法被标记为私有（通过 `:meta private:` 注释指示），在使用 `LLMKnowledgeChain` 类时，应避免直接调用此方法。相反，应通过类提供的其他公共方法来间接访问或修改 `input_key` 的值。

**输出示例**:
```python
["example_input_key"]
```
在这个示例中，假设 `LLMKnowledgeChain` 实例的 `input_key` 属性值为 `"example_input_key"`，那么调用 `input_keys` 方法将返回一个包含这个字符串的列表。这表明该实例期望的输入键仅有一个，即 `"example_input_key"`。
***
### FunctionDef output_keys(self)
**output_keys**: 此函数的功能是返回一个包含输出键的列表。

**参数**: 此函数没有参数。

**代码描述**: `output_keys` 函数是 `LLMKnowledgeChain` 类的一个成员方法，它的作用是返回一个列表，这个列表中包含了一个元素，即 `self.output_key`。这里的 `self.output_key` 是 `LLMKnowledgeChain` 实例的一个属性，代表了某种输出的关键字。此函数被标记为私有方法（通过 `:meta private:` 注释），这意味着它主要供类内部其他方法调用，而不是设计给外部使用。

**注意**: 由于此函数被标记为私有，因此在使用 `LLMKnowledgeChain` 类时，应避免直接调用 `output_keys` 方法，而是通过类提供的其他公共接口来间接获取所需的输出键信息。

**输出示例**:
```python
['desired_output_key']
```
在这个示例中，`'desired_output_key'` 是 `self.output_key` 的值，表示此实例期望得到的输出键。返回值是一个列表，即使只有一个输出键，也会以列表的形式返回，这样做可以保持接口的一致性和扩展性。
***
### FunctionDef _evaluate_expression(self, queries)
Doc is waiting to be generated...
***
### FunctionDef _process_llm_result(self, llm_output, run_manager)
Doc is waiting to be generated...
***
### FunctionDef _aprocess_llm_result(self, llm_output, run_manager)
Doc is waiting to be generated...
***
### FunctionDef _call(self, inputs, run_manager)
Doc is waiting to be generated...
***
### FunctionDef _acall(self, inputs, run_manager)
Doc is waiting to be generated...
***
### FunctionDef _chain_type(self)
**函数名**: _chain_type

**函数功能**: 返回链类型的字符串表示。

**参数**: 此函数没有参数。

**代码描述**: `_chain_type`函数是`LLMKnowledgeChain`类的一个私有方法，用于返回表示链类型的字符串。在这个上下文中，链类型被固定定义为`"llm_knowledge_chain"`，这意味着该函数返回的字符串用于标识或表示一个基于长期记忆模型（Long-term Language Model，简称LLM）的知识链。这个标识符可以被用来在处理不同类型的知识链时，区分出是基于LLM的知识链。由于这是一个私有方法，它主要被类内部的其他方法调用，而不是被类的外部直接调用。

**注意**: 由于`_chain_type`是一个私有方法，它应该只在`LLMKnowledgeChain`类的内部被使用。尝试从类的外部直接调用这个方法可能会导致访问控制错误或不被期待的行为。

**输出示例**: 
```python
"llm_knowledge_chain"
```
此输出示例展示了调用`_chain_type`方法时会返回的字符串。这个字符串可以被视为一个标识符，用于在可能存在多种类型的知识链时，识别出特定的基于LLM的知识链。
***
### FunctionDef from_llm(cls, llm, prompt)
**from_llm**: 此函数的功能是从语言模型创建一个知识链对象。

**参数**:
- `cls`: 类方法的第一个参数，指代当前类，用于创建类的实例。
- `llm`: BaseLanguageModel的实例，代表要使用的语言模型。
- `prompt`: BasePromptTemplate的实例，默认为PROMPT，用于生成查询时的提示模板。
- `**kwargs`: 接受任意数量的关键字参数，这些参数将传递给LLMKnowledgeChain的构造函数。

**代码描述**:
`from_llm`是一个类方法，它接受一个语言模型实例和可选的提示模板，以及其他任意关键字参数。此方法首先创建一个`LLMChain`实例，该实例封装了语言模型和提示模板的细节。然后，它使用这个`LLMChain`实例和任何其他提供的关键字参数来创建并返回一个`LLMKnowledgeChain`实例。这个过程允许将语言模型和相关配置封装为一个可用于执行复杂知识搜索任务的链式对象。

在项目中，`from_llm`方法被`search_knowledgebase_complex`函数调用。在这个调用中，它使用从模型容器中获取的模型实例和一个`verbose`关键字参数来创建一个`LLMKnowledgeChain`实例。然后，这个实例被用来对一个查询执行运行操作，以获取答案。这展示了`from_llm`方法如何允许灵活地构建知识链，以便在复杂的知识搜索任务中使用。

**注意**:
- 确保传递给`from_llm`的`llm`参数是一个有效的`BaseLanguageModel`实例，因为它是执行知识搜索所必需的。
- `prompt`参数虽然是可选的，但正确设置它可以显著影响知识搜索的效果，因此建议根据具体的应用场景进行适当配置。
- 通过`**kwargs`传递的任何额外参数应该与`LLMKnowledgeChain`的构造函数兼容，以确保它们可以正确地被使用。

**输出示例**:
假设`from_llm`方法被正确调用，它可能返回如下的`LLMKnowledgeChain`实例：
```
LLMKnowledgeChain(llm_chain=LLMChain(llm=<BaseLanguageModel实例>, prompt=<BasePromptTemplate实例>), verbose=True)
```
这个实例随后可以用于执行具体的知识搜索任务。
***
## FunctionDef search_knowledgebase_complex(query)
Doc is waiting to be generated...
## ClassDef KnowledgeSearchInput
**KnowledgeSearchInput**: KnowledgeSearchInput类的功能是定义一个用于搜索知识库的输入模型。

**属性**:
- location: 用于搜索的查询字符串。

**代码描述**:
KnowledgeSearchInput类继承自BaseModel，这表明它是一个模型类，用于定义数据结构和类型。在这个类中，定义了一个名为`location`的属性，该属性被标记为一个字符串类型。通过使用`Field`函数，为`location`属性提供了额外的描述信息，即“要被搜索的查询”。这样的设计使得KnowledgeSearchInput类不仅仅是一个数据容器，还通过属性描述增强了代码的可读性和易用性。

在项目中，虽然`server/agent/tools/__init__.py`和`server/agent/tools_select.py`这两个对象中没有直接提到KnowledgeSearchInput类的使用，但可以推断，KnowledgeSearchInput类作为一个数据模型，可能会被项目中负责搜索知识库功能的部分调用。具体来说，它可能被用于封装用户输入的搜索查询，然后这个封装好的查询被传递给执行搜索的函数或方法，以便根据`location`属性中的值来检索相关的知识库条目。

**注意**:
- 在使用KnowledgeSearchInput类时，需要确保传递给`location`属性的值是一个合法的字符串，因为这将直接影响到搜索的结果。
- 由于KnowledgeSearchInput类继承自BaseModel，因此可以利用Pydantic库提供的数据验证功能来确保输入数据的有效性。这意味着在实例化KnowledgeSearchInput对象时，如果传递的数据类型不符合预期，将会抛出错误，从而帮助开发者及早发现并修正问题。
