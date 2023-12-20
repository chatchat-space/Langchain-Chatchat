from server.agent.tool_retriever_agent_executor.custom_loads.prompt_template import CustomPromptTemplate
from server.agent.tool_retriever_agent_executor.custom_loads.prompt_parse import CustomOutputParser
from langchain.chains import LLMChain
from langchain_core.language_models.base import BaseLanguageModel
from langchain.agents import (
    AgentExecutor,
    LLMSingleActionAgent,
)

# Set up the base template
TEMPLATE = """Answer the following questions as best you can, but speaking as a pirate might speak. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin! Remember to speak as a pirate when giving your final answer. Use lots of "Arg"s

Question: {input}
{agent_scratchpad}"""


class RetrievalToolExecutor:
    """Executor for the tools."""
    toolkits_dict = {}
    retriever = None

    def __init__(self, retriever, toolkits_dict):
        """初始化 RetrievalToolExecutor相关构件."""

        self.retriever = retriever
        self.toolkits_dict = toolkits_dict

    @classmethod
    def from_retriever_and_toolkits_dict(cls, retriever, toolkits_dict):
        """加载 RetrievalToolExecutor相关构件."""

        return cls(retriever, toolkits_dict)

    def get_tools(self, query):
        # Get documents, which contain the Plugins to use
        docs = self.retriever.get_relevant_documents(query)
        # Get the toolkits, one for each plugin
        tool_kits = [self.toolkits_dict[d.metadata["plugin_name"]] for d in docs]
        # Get the tools: a separate NLAChain for each endpoint
        tools = []
        for tk in tool_kits:
            tools.extend(tk.nla_tools)
        return tools

    def build_executor(self, query_with_tool: str, llm: BaseLanguageModel, template=TEMPLATE) -> AgentExecutor:
        prompt = CustomPromptTemplate(
            template=template,
            tools_getter=self.get_tools,
            # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated
            # dynamically This includes the `intermediate_steps` variable because that is needed
            input_variables=["input", "intermediate_steps"],
        )

        output_parser = CustomOutputParser()
        """构建 AgentExecutor."""
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        tools = self.get_tools(query_with_tool)
        tool_names = [tool.name for tool in tools]
        agent = LLMSingleActionAgent(
            llm_chain=llm_chain,
            output_parser=output_parser,
            stop=["\nObservation:"],
            allowed_tools=tool_names,
        )
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True
        )
        return agent_executor
