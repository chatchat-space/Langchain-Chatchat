from typing import Annotated, Callable, Any, Dict, Optional, Type, Union
from typing_extensions import TypedDict

from langchain_core.tools import BaseTool
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

from .graphs_registry import regist_graph, InputHandler, EventHandler


class BaseGraphInputHandler(InputHandler):
    def create_inputs(self, query: str, metadata: dict) -> Dict[str, Any]:
        return {"messages": ("user", query)}


class BaseGraphEventHandler(EventHandler):
    def handle_event(self, event: Dict[str, Any]) -> str:
        res_content = ""
        messages = event.get('messages', [])
        for message in messages:
            content = getattr(message, "content", "")
            message_type = getattr(message, "type", "")
            name = getattr(message, "name", "")
            tool_calls = getattr(message, "tool_calls", [])

            if isinstance(content, list):
                content = "  \n".join([f"- {item}" for item in content])

            if tool_calls:
                tool_calls_content = "tool_calls:  \n"
                for tool_call in tool_calls:
                    tool_calls_content += f"  - type: {tool_call.get('type')}  \n"
                    tool_calls_content += f"    name: {tool_call.get('name')}  \n"
                    tool_calls_content += f"    args: {tool_call.get('args')}  \n"
                    content += f"{tool_calls_content}"

            if name:
                res = (f"node: {message_type}  \n"
                       f"name: {name}  \n"
                       f"content: {content}  \n")
            else:
                res = (f"node: {message_type}  \n"
                       f"content: {content}  \n")

            res_content += f"{res}  \n"
        return res_content


@regist_graph(name="base_graph",
              input_handler=BaseGraphInputHandler,
              event_handler=BaseGraphEventHandler)
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
