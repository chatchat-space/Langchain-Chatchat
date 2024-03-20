from multiprocessing import Process
from typing import Dict
import logging

logger = logging.getLogger(__name__)
mp_manager = None
processes: Dict[str, Process] = {}


def stop():
    for n, process in processes.items():
        logger.warning("Sending SIGKILL to %s", p)
        try:

            process.kill()
        except Exception as e:
            logger.info("Failed to kill process %s", p, exc_info=True)

    for n, p in processes.items():
        logger.info("Process status: %s", p)

    del processes
