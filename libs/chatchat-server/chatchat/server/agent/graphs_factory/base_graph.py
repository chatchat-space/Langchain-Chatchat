from typing import Annotated, Any, Dict
from typing_extensions import TypedDict

from langchain_openai.chat_models import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.messages import (
    AIMessage,
    ToolMessage,
    filter_messages,
)
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from chatchat.server.utils import get_agent_memory, build_logger
from .graphs_registry import regist_graph, InputHandler, EventHandler

logger = build_logger()


class BaseGraphInputHandler(InputHandler):
    def create_inputs(self, query: str, metadata: dict) -> Dict[str, Any]:
        return {"messages": ("user", query)}


class BaseGraphEventHandler(EventHandler):
    def handle_event(self, event: Dict[str, Any]) -> str:
        res_content = ""
        messages = event.get('messages', [])
        if messages:
            # 只处理最后一条 message，即当前的 input 和 output
            message = messages[-1]
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
def base_graph(llm: ChatOpenAI, tools: list[BaseTool], history_len: int) -> CompiledGraph:
    if not isinstance(llm, ChatOpenAI):
        raise TypeError("llm must be an instance of ChatOpenAI")
    if not all(isinstance(tool, BaseTool) for tool in tools):
        raise TypeError("All items in tools must be instances of BaseTool")

    memory = get_agent_memory()

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    graph_builder = StateGraph(State)

    llm_with_tools = llm.bind_tools(tools)

    def memory_manager(state: State) -> Dict[str, Any]:
        try:
            # 考虑到成本, 默认将 Function Calling 相关内容过滤掉
            filtered_messages = []
            for message in filter_messages(state["messages"], exclude_types=[ToolMessage]):
                if isinstance(message, AIMessage) and message.tool_calls:
                    continue
                filtered_messages.append(message)
            print(f"history_len: {history_len}")
            # 更新 state 中的 messages
            state["messages"] = filtered_messages[-history_len:]

            return {"messages": state["messages"]}
        except Exception as e:
            raise Exception(f"filtering messages error: {e}")

    def chatbot(state: State) -> Dict[str, Any]:
        a = state["messages"]
        print(f"✅ ❌ current chatbot messages: {a}")
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    tool_node = ToolNode(tools=tools)

    graph_builder.add_node("memory_manager", memory_manager)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("memory_manager", "chatbot")
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.set_entry_point("memory_manager")
    graph = graph_builder.compile(checkpointer=memory)

    return graph
