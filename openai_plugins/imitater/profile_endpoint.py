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
from imitater_config import ImitaterCfg
import imitater_process_dict


class ImitaterProfileEndpointAdapter(ProfileEndpointAdapter):
    """Adapter for the profile endpoint."""

    def __init__(self, cfg=None, state_dict: dict = None):
        self._cfg = ImitaterCfg(cfg=cfg)
        super().__init__(state_dict=state_dict)

    def class_name(self) -> str:
        """Get class name."""
        return self.__name__

    def list_running_models(self) -> List[LLMWorkerInfo]:
        """模型列表及其配置项"""
        list_worker = []

        for worker_name, process in imitater_process_dict.processes.items():
            list_worker.append(self.get_model_config(worker_name))
        return list_worker

    def list_llm_models(self) -> List[LLMWorkerInfo]:
        """获取已配置模型列表"""
        list_worker = []
        workers_names = self._cfg.get_imitate_model_workers_names()
        for worker_name in workers_names:
            list_worker.append(self.get_model_config(worker_name))

        return list_worker

    def get_model_config(self, model_name) -> LLMWorkerInfo:

        '''
        获取LLM模型配置项（合并后的）
        '''

        worker_cfg = self._cfg.get_imitate_model_workers_by_name(model_name)

        info_obj = LLMWorkerInfo(worker_id=model_name,
                                 model_name=model_name,
                                 model_description="",
                                 providers=["model", "embedding"],
                                 model_extra_info=json.dumps(dict(worker_cfg), ensure_ascii=False, indent=4))
        return info_obj

    @classmethod
    def from_config(cls, cfg=None):
        _state_dict = {
            "profile_name": "Imitate",
            "profile_version": "0.0.1",
            "profile_description": "Imitate profile endpoint",
            "profile_author": "Imitate"
        }
        state_dict = cfg.get("state_dict", {})
        if state_dict is not None and _state_dict is not None:
            _state_dict = {**state_dict, **_state_dict}
        else:
            # 处理其中一个或两者都为 None 的情况
            _state_dict = state_dict or _state_dict or {}

        return cls(cfg=cfg, state_dict=_state_dict)
