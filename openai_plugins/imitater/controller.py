import time
from multiprocessing import Process

from loom_core.openai_plugins.core.control import ControlAdapter

import os
import sys
import logging

logger = logging.getLogger(__name__)
# 为了能使用插件中的函数，需要将当前目录加入到sys.path中
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)

import imitater_process_dict

from imitater_wrapper import run_imitater
from imitater_config import ImitaterCfg


class ImitaterControlAdapter(ControlAdapter):

    def __init__(self, cfg=None, state_dict: dict = None):
        self._cfg = ImitaterCfg(cfg=cfg)
        super().__init__(state_dict=state_dict)

    def class_name(self) -> str:
        """Get class name."""
        return self.__name__

    def start_model(self, new_model_name):

        imitater_process_dict.stop()

        logger.info(f"准备启动新进程：{new_model_name}")
        e = imitater_process_dict.mp_manager.Event()
        process = Process(
            target=run_imitater,
            name=f"model_worker - {new_model_name}",
            kwargs=dict(cfg=self._cfg,
                        worker_name=new_model_name,
                        started_event=e),
            daemon=True,
        )
        process.start()
        process.name = f"{process.name} ({process.pid})"
        imitater_process_dict.processes[new_model_name] = process
        # e.wait()
        logger.info(f"成功启动新进程：{new_model_name}")

    def stop_model(self, model_name: str):

        if model_name in imitater_process_dict.processes:
            process = imitater_process_dict.processes.pop(model_name)
            time.sleep(1)
            process.kill()
            logger.info(f"停止进程：{model_name}")
        else:
            logger.error(f"未找到进程：{model_name}")
            raise Exception(f"未找到进程：{model_name}")

    def replace_model(self, model_name: str, new_model_name: str):
        pass

    @classmethod
    def from_config(cls, cfg=None):
        _state_dict = {
            "controller_name": "Imitate",
            "controller_version": "0.0.1",
            "controller_description": "Imitate controller",
            "controller_author": "Imitate"
        }
        state_dict = cfg.get("state_dict", {})
        if state_dict is not None and _state_dict is not None:
            _state_dict = {**state_dict, **_state_dict}
        else:
            # 处理其中一个或两者都为 None 的情况
            _state_dict = state_dict or _state_dict or {}

        return cls(cfg=cfg, state_dict=_state_dict)
