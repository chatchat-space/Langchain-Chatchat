from typing import List

from loom_core.openai_plugins.core.adapter import LLMWorkerInfo
from loom_core.openai_plugins.core.profile_endpoint.core import ProfileEndpointAdapter

import os
import sys
import logging

logger = logging.getLogger(__name__)

root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)


class ZhipuAIProfileEndpointAdapter(ProfileEndpointAdapter):
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
        list_worker.append(LLMWorkerInfo(worker_id="glm-4",
                                         model_name="glm-4",
                                         model_description="glm-4",
                                         providers=["model", "embedding"],
                                         model_extra_info="{}"))
        list_worker.append(LLMWorkerInfo(worker_id="glm-3-turbo",
                                         model_name="glm-3-turbo",
                                         model_description="glm-3-turbo",
                                         providers=["model", "embedding"],
                                         model_extra_info="{}"))
        list_worker.append(LLMWorkerInfo(worker_id="embedding-2",
                                         model_name="embedding-2",
                                         model_description="embedding-2",
                                         providers=["embedding"],
                                         model_extra_info="{}"))
        return list_worker

    def list_llm_models(self) -> List[LLMWorkerInfo]:
        """获取已配置模型列表"""
        list_worker = []
        list_worker.append(LLMWorkerInfo(worker_id="glm-4",
                                         model_name="glm-4",
                                         model_description="glm-4",
                                         providers=["model", "embedding"],
                                         model_extra_info="{}"))
        list_worker.append(LLMWorkerInfo(worker_id="glm-3-turbo",
                                         model_name="glm-3-turbo",
                                         model_description="glm-3-turbo",
                                         providers=["model", "embedding"],
                                         model_extra_info="{}"))
        list_worker.append(LLMWorkerInfo(worker_id="embedding-2",
                                         model_name="embedding-2",
                                         model_description="embedding-2",
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
            "profile_name": "zhipuai",
            "profile_version": "0.0.1",
            "profile_description": "zhipuai profile endpoint",
            "profile_author": "zhipuai"
        }
        state_dict = cfg.get("state_dict", {})
        if state_dict is not None and _state_dict is not None:
            _state_dict = {**state_dict, **_state_dict}
        else:
            # 处理其中一个或两者都为 None 的情况
            _state_dict = state_dict or _state_dict or {}

        return cls(cfg=cfg, state_dict=_state_dict)
