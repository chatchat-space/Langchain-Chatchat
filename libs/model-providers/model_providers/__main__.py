import argparse
import asyncio
import logging

from model_providers import BootstrapWebBuilder
from model_providers.core.utils.utils import (
    get_config_dict,
    get_log_file,
    get_timestamp_ms,
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-providers",
        type=str,
        default="/mnt/d/project/Langchain-Chatchat/model-providers/model_providers.yaml",
        help="run model_providers servers",
        dest="model_providers",
    )
    args = parser.parse_args()
    try:
        logging_conf = get_config_dict(
            "INFO",
            get_log_file(log_path="logs", sub_dir=f"local_{get_timestamp_ms()}"),
            1024 * 1024 * 1024 * 3,
            1024 * 1024 * 1024 * 3,
        )
        boot = (
            BootstrapWebBuilder()
            .model_providers_cfg_path(model_providers_cfg_path=args.model_providers)
            .host(host="127.0.0.1")
            .port(port=20000)
            .build()
        )
        boot.set_app_event(started_event=None)
        boot.logging_conf(logging_conf=logging_conf)
        boot.run()

        async def pool_join_thread():
            await boot.join()

        asyncio.run(pool_join_thread())
    except SystemExit:
        logger.info("SystemExit raised, exiting")
        raise
