from langchain_core.tools import BaseTool
from langgraph.graph.graph import CompiledGraph
from .graphs_registry import regist_graph
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai.chat_models import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Callable, Any, Dict, Optional, Type, Union


@regist_graph(name="base_graph")
def base_graph(llm: ChatOpenAI, tools: list[BaseTool]) -> CompiledGraph:
    if not isinstance(llm, ChatOpenAI):
        raise TypeError("llm must be an instance of ChatOpenAI")
    if not all(isinstance(tool, BaseTool) for tool in tools):
        raise TypeError("All items in tools must be instances of BaseTool")

    llm_with_tools = llm.bind_tools(tools)

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    def chatbot(state: State) -> Dict[str, Any]:
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    graph_builder = StateGraph(State)

    graph_builder.add_node("chatbot", chatbot)
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge(
        "tools",
        "chatbot")

    graph_builder.set_entry_point("chatbot")

    memory = SqliteSaver.from_conn_string(":memory:")

    graph = graph_builder.compile(checkpointer=memory)

    return graph
