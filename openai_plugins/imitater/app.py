import multiprocessing as mp
from multiprocessing import Process
from typing import List

from loom_core.constants import LOOM_LOG_BACKUP_COUNT, LOOM_LOG_MAX_BYTES
from loom_core.openai_plugins.core.adapter import ProcessesInfo
from loom_core.openai_plugins.core.application import ApplicationAdapter

import os
import sys
import logging

from loom_core.openai_plugins.deploy.utils import get_timestamp_ms, get_config_dict, get_log_file
from omegaconf import OmegaConf

logger = logging.getLogger(__name__)
# 为了能使用插件中的函数，需要将当前目录加入到sys.path中
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)
import imitater_process_dict
from imitater_config import ImitaterCfg
from imitater_wrapper import run_imitater


class ImitaterApplicationAdapter(ApplicationAdapter):
    model_worker_started: mp.Event = None

    def __init__(self, cfg=None, state_dict: dict = None):
        self.processesInfo = None
        self._cfg = ImitaterCfg(cfg=cfg)
        super().__init__(state_dict=state_dict)

    def class_name(self) -> str:
        """Get class name."""
        return self.__name__

    @classmethod
    def from_config(cls, cfg=None):
        _state_dict = {
            "application_name": "Imitate",
            "application_version": "0.0.1",
            "application_description": "Imitate application",
            "application_author": "Imitate"
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

        logging_conf = get_config_dict(
            processesInfo.log_level,
            get_log_file(log_path=self._cfg.get_cfg().get("logdir"), sub_dir=f"local_{get_timestamp_ms()}"),
            LOOM_LOG_BACKUP_COUNT,
            LOOM_LOG_MAX_BYTES,
        )
        logging.config.dictConfig(logging_conf)  # type: ignore
        worker_name = self._cfg.get_cfg().get("worker_name", [])
        imitater_process_dict.mp_manager = mp.Manager()

        # prevent re-init cuda error.
        mp.set_start_method(method="spawn", force=True)

        self.model_worker_started = imitater_process_dict.mp_manager.Event()

        process = Process(
            target=run_imitater,
            name=f"model_worker - {worker_name}",
            kwargs=dict(cfg=self._cfg,
                        worker_name=worker_name,
                        started_event=self.model_worker_started,
                        logging_conf=logging_conf),
            daemon=True,
        )
        imitater_process_dict.processes[worker_name] = process

    def start(self):

        for n, p in imitater_process_dict.processes.items():
            p.start()
            p.name = f"{p.name} ({p.pid})"

        # 等待 model_worker启动完成
        # self.model_worker_started.wait()

    def stop(self):
        imitater_process_dict.stop()

