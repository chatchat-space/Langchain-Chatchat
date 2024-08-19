from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Annotated, Union, Optional
from typing_extensions import TypedDict

from langchain_openai.chat_models import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    ToolMessage,
    filter_messages,
)
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from chatchat.server.utils import get_graph_memory, build_logger
from .graphs_registry import regist_graph, InputHandler, EventHandler

logger = build_logger()


@dataclass
class Message:
    role: str
    content: str


class BaseGraphInputHandler(InputHandler):
    def __init__(self):
        self.query = None
        self.metadata = None

    def create_inputs(self, query: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        self.query = query
        self.metadata = metadata
        return {"messages": asdict(Message(role="user", content=self.query))}


@dataclass
class Event:
    messages: List[BaseMessage]
    history: Optional[List[BaseMessage]] = None


class BaseGraphEventHandler(EventHandler):
    def __init__(self):
        self.event = None

    def handle_event(self, event_data: Union[Event, Dict[str, Any]]) -> BaseMessage:
        '''
        event example:
        {
            'messages': [HumanMessage(
                            content='The youtube video of Xiao Yixian in Fights Break Sphere?',
                            id='b9c5468a-7340-425b-ae6f-2f584a961014')],
            'history': [HumanMessage(
                            content='The youtube video of Xiao Yixian in Fights Break Sphere?',
                            id='b9c5468a-7340-425b-ae6f-2f584a961014')]
        }
        '''
        if isinstance(event_data, dict):
            event = Event(
                messages=[BaseMessage(**msg.__dict__) for msg in event_data['messages']],
                history=[BaseMessage(**msg.__dict__) for msg in event_data.get('history', [])]
            )
        else:
            event = event_data
        return event.messages[0]


@regist_graph(name="base_graph",
              input_handler=BaseGraphInputHandler,
              event_handler=BaseGraphEventHandler)
def base_graph(llm: ChatOpenAI, tools: list[BaseTool], history_len: int) -> CompiledGraph:
    if not isinstance(llm, ChatOpenAI):
        raise TypeError("llm must be an instance of ChatOpenAI")
    if not all(isinstance(tool, BaseTool) for tool in tools):
        raise TypeError("All items in tools must be instances of BaseTool")

    memory = get_graph_memory()

    class State(TypedDict):
        messages: Annotated[list, add_messages]
        history: list[BaseMessage]

    graph_builder = StateGraph(State)

    llm_with_tools = llm.bind_tools(tools)

    def history_manager(state: State) -> Dict[str, list[BaseMessage]]:
        try:
            # 目的: 降本. 做法: 给 llm 传递历史上下文时, 把 Function Calling 相关内容过滤, 只保留 history_len 长度的历史上下文.
            # todo: """目前 history_len 直接截取了 messages 长度, 希望通过 对话轮数 来限制.
            #  原因: 一轮对话会追加数个 message, 但是目前没有从 snapshot(graph.get_state) 中找到很好的办法来获取一轮对话."""
            filtered_messages = []
            for message in filter_messages(state["messages"], exclude_types=[ToolMessage]):
                if isinstance(message, AIMessage) and message.tool_calls:
                    continue
                filtered_messages.append(message)
            state["history"] = filtered_messages[-history_len-1:]
            return state
        except Exception as e:
            raise Exception(f"filtering messages error: {e}")

    def chatbot(state: State) -> Dict[str, list[BaseMessage]]:
        # ToolMessage 默认 return {"messages": outputs}, 需要在 history 中追加 ToolMessage 结果, 否则报错
        if isinstance(state["messages"][-1], ToolMessage):
            state["history"].append(state["messages"][-1])

        messages = llm_with_tools.invoke(state["history"])
        state["messages"] = [messages]
        state["history"].append(messages)
        return state

    tool_node = ToolNode(tools=tools)

    graph_builder.add_node("history_manager", history_manager)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)

    graph_builder.set_entry_point("history_manager")
    graph_builder.add_edge("history_manager", "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("tools", "chatbot")

    graph = graph_builder.compile(checkpointer=memory)

    return graph
