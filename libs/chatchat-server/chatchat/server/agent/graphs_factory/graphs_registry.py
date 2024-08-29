from typing import Callable, Any, Dict, Type, Annotated, List, Optional, TypedDict
from abc import ABC, abstractmethod
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.pydantic_v1 import BaseModel

__all__ = ["regist_graph", "InputHandler", "EventHandler", "State", "Response", "serialize_content"]

_GRAPHS_REGISTRY: Dict[str, Dict[str, Any]] = {}


class State(TypedDict):
    """
    定义一个基础 State 供 各类 graph 继承, 其中:
    1. messages 为所有 graph 的核心信息队列, 所有聊天工作流均应该将关键信息补充到此队列中;
    2. history 为所有工作流单次启动时获取 history_len 的 messages 所用(节约成本, 及防止单轮对话 tokens 占用长度达到 llm 支持上限),
    history 中的信息理应是可以被丢弃的.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    history: Optional[List[BaseMessage]]


class Response(TypedDict):
    node: str
    content: Any


def serialize_content(content: Any) -> Any:
    if isinstance(content, BaseModel):
        return content.dict()
    elif isinstance(content, list):
        return [serialize_content(item) for item in content]
    elif isinstance(content, dict):
        return {key: serialize_content(value) for key, value in content.items()}
    return content


class Message(TypedDict):
    role: str
    content: str


class InputHandler(ABC):
    def __init__(self, query: str, metadata: Dict[str, Any]):
        self.query = query
        self.metadata = metadata  # 暂未使用

    def create_inputs(self) -> Dict[str, Any]:
        return {"messages": Message(role="user", content=self.query)}


class EventHandler(ABC):
    @abstractmethod
    def handle_event(self, node: str, events: Any) -> str:
        pass


def regist_graph(name: str, input_handler: Type[InputHandler], event_handler: Type[EventHandler]) -> Callable:
    """
    graph 注册工厂类
    :param name: graph 的名称
    :param input_handler: 输入数据结构
    :param event_handler: 输出数据结构
    :return: graph 实例
    """
    def wrapper(func: Callable) -> Callable:
        _GRAPHS_REGISTRY[name] = {
            "func": func,
            "input_handler": input_handler,
            "event_handler": event_handler
        }
        return func
    return wrapper
