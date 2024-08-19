from typing import Callable, Any, Dict, Optional, Type, Union
from abc import ABC, abstractmethod

__all__ = ["regist_graph", "InputHandler", "EventHandler"]

_GRAPHS_REGISTRY: Dict[str, Dict[str, Any]] = {}


class InputHandler(ABC):
    @abstractmethod
    def create_inputs(self, query: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        pass


class EventHandler(ABC):
    @abstractmethod
    def handle_event(self, event: Any) -> str:
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
