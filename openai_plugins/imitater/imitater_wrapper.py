import multiprocessing
from typing import List, Optional, Dict

from fastapi import FastAPI
import sys

import multiprocessing as mp
import uvicorn
import os
import logging
import asyncio
import signal
import inspect

logger = logging.getLogger(__name__)
# 为了能使用fastchat_wrapper.py中的函数，需要将当前目录加入到sys.path中
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)

from imitater_config import ImitaterCfg

"""
防止Can't pickle Function
"""


def _start_imitater(
        started_event: mp.Event = None
):
    from imitater.service.app import launch_app
    # 跳过键盘中断，
    signal.signal(signal.SIGINT, lambda *_: None)
    launch_app()


def run_imitater(
        cfg: ImitaterCfg,
        worker_name: str,
        started_event: mp.Event = None,
        logging_conf: Optional[dict] = None):
    # 跳过键盘中断，
    signal.signal(signal.SIGINT, lambda *_: None)

    logging.config.dictConfig(logging_conf)  # type: ignore
    import os
    worker_cfg = cfg.get_imitate_model_workers_by_name(worker_name)

    os.environ["AGENT_TYPE"] = worker_cfg.get("model").get("agent_type")
    os.environ["CHAT_MODEL_PATH"] = worker_cfg.get("model").get("chat_model_path")
    os.environ["CHAT_MODEL_DEVICE"] = worker_cfg.get("model").get("chat_model_device")
    os.environ["CHAT_TEMPLATE_PATH"] = worker_cfg.get("model").get("chat_template_path")
    os.environ["GENERATION_CONFIG_PATH"] = worker_cfg.get("model").get("generation_config_path")

    os.environ["EMBED_MODEL_PATH"] = worker_cfg.get("embedding").get("embed_model_path")
    os.environ["EMBED_MODEL_DEVICE"] = worker_cfg.get("embedding").get("embed_model_device")
    os.environ["EMBED_BATCH_SIZE"] = str(worker_cfg.get("embedding").get("embed_batch_size"))

    os.environ["SERVICE_PORT"] = str(cfg.get_run_openai_api_cfg().get("port", 30000))

    _start_imitater(started_event=started_event)
