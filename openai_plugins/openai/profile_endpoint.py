import json
from typing import List

from loom_core.openai_plugins.core.adapter import LLMWorkerInfo
from loom_core.openai_plugins.core.profile_endpoint.core import ProfileEndpointAdapter

import os
import sys
import logging

logger = logging.getLogger(__name__)
# 为了能使用插件中的函数，需要将当前目录加入到sys.path中
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)


class OpenAIProfileEndpointAdapter(ProfileEndpointAdapter):
    """Adapter for the profile endpoint."""

    def __init__(self, cfg=None, state_dict: dict = None):
        self._cfg = cfg
        super().__init__(state_dict=state_dict)

    def class_name(self) -> str:
        """Get class name."""
        return self.__name__

    def list_running_models(self) -> List[LLMWorkerInfo]:
        """模型列表及其配置项"""
        list_worker = []
        list_worker.append(LLMWorkerInfo(worker_id="gpt-3.5-turbo",
                                         model_name="gpt-3.5-turbo",
                                         model_description="gpt-3.5-turbo",
                                         providers=["model", "embedding"],
                                         model_extra_info="{}"))
        list_worker.append(LLMWorkerInfo(worker_id="gpt-4",
                                         model_name="gpt-4",
                                         model_description="gpt-4",
                                         providers=["model", "embedding"],
                                         model_extra_info="{}"))
        list_worker.append(LLMWorkerInfo(worker_id="gpt-4-1106-preview",
                                         model_name="gpt-4-1106-preview",
                                         model_description="gpt-4-1106-preview",
                                         providers=["model", "embedding"],
                                         model_extra_info="{}"))
        list_worker.append(LLMWorkerInfo(worker_id="text-embedding-ada-002",
                                         model_name="text-embedding-ada-002",
                                         model_description="text-embedding-ada-002",
                                         providers=["embedding"],
                                         model_extra_info="{}"))
        return list_worker

    def list_llm_models(self) -> List[LLMWorkerInfo]:
        """获取已配置模型列表"""
        list_worker = []
        list_worker.append(LLMWorkerInfo(worker_id="gpt-3.5-turbo",
                                         model_name="gpt-3.5-turbo",
                                         model_description="gpt-3.5-turbo",
                                         providers=["model", "embedding"],
                                         model_extra_info="{}"))
        list_worker.append(LLMWorkerInfo(worker_id="gpt-4",
                                         model_name="gpt-4",
                                         model_description="gpt-4",
                                         providers=["model", "embedding"],
                                         model_extra_info="{}"))
        list_worker.append(LLMWorkerInfo(worker_id="gpt-4-1106-preview",
                                         model_name="gpt-4-1106-preview",
                                         model_description="gpt-4-1106-preview",
                                         providers=["model", "embedding"],
                                         model_extra_info="{}"))
        list_worker.append(LLMWorkerInfo(worker_id="text-embedding-ada-002",
                                         model_name="text-embedding-ada-002",
                                         model_description="text-embedding-ada-002",
                                         providers=["embedding"],
                                         model_extra_info="{}"))
        return list_worker

    def get_model_config(self, model_name) -> LLMWorkerInfo:

        '''
        获取LLM模型配置项（合并后的）
        '''

        info_obj = LLMWorkerInfo(worker_id=model_name,
                                 model_name=model_name,
                                 model_description="",
                                 providers=["model", "embedding"],
                                 model_extra_info="{}")

        return info_obj

    @classmethod
    def from_config(cls, cfg=None):
        _state_dict = {
            "profile_name": "openai",
            "profile_version": "0.0.1",
            "profile_description": "openai profile endpoint",
            "profile_author": "openai"
        }
        state_dict = cfg.get("state_dict", {})
        if state_dict is not None and _state_dict is not None:
            _state_dict = {**state_dict, **_state_dict}
        else:
            # 处理其中一个或两者都为 None 的情况
            _state_dict = state_dict or _state_dict or {}

        return cls(cfg=cfg, state_dict=_state_dict)
