from loom_core.openai_plugins.core.adapter import ProcessesInfo
from loom_core.openai_plugins.core.application import ApplicationAdapter

import os
import sys
import logging

logger = logging.getLogger(__name__)
# 为了能使用插件中的函数，需要将当前目录加入到sys.path中
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)


class OpenAIApplicationAdapter(ApplicationAdapter):

    def __init__(self, cfg=None, state_dict: dict = None):
        self.processesInfo = None
        self._cfg = cfg
        super().__init__(state_dict=state_dict)

    def class_name(self) -> str:
        """Get class name."""
        return self.__name__

    @classmethod
    def from_config(cls, cfg=None):
        _state_dict = {
            "application_name": "openai",
            "application_version": "0.0.1",
            "application_description": "openai application",
            "application_author": "openai"
        }
        state_dict = cfg.get("state_dict", {})
        if state_dict is not None and _state_dict is not None:
            _state_dict = {**state_dict, **_state_dict}
        else:
            # 处理其中一个或两者都为 None 的情况
            _state_dict = state_dict or _state_dict or {}
        return cls(cfg=cfg, state_dict=_state_dict)

    def init_processes(self, processesInfo: ProcessesInfo):

        self.processesInfo = processesInfo

    def start(self):
        pass

    def stop(self):
        pass
