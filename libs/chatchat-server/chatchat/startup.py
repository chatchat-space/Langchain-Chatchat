import asyncio
import multiprocessing
from contextlib import asynccontextmanager
import multiprocessing as mp
import os

import logging
import logging.config
import sys
from multiprocessing import Process
logger = logging.getLogger()

# 设置numexpr最大线程数，默认为CPU核心数
try:
    import numexpr

    n_cores = numexpr.utils.detect_number_of_cores()
    os.environ["NUMEXPR_MAX_THREADS"] = str(n_cores)
except:
    pass

from fastapi import FastAPI
import argparse
from typing import List, Dict


def _set_app_event(app: FastAPI, started_event: mp.Event = None):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if started_event is not None:
            started_event.set()
        yield

    app.router.lifespan_context = lifespan


def run_init_server(
        model_platforms_shard: Dict,
        started_event: mp.Event = None,
        model_providers_cfg_path: str = None,
        provider_host: str = None,
        provider_port: int = None):
    from chatchat.init_server import init_server
    from chatchat.configs import (MODEL_PROVIDERS_CFG_PATH_CONFIG,
                                  MODEL_PROVIDERS_CFG_HOST,
                                  MODEL_PROVIDERS_CFG_PORT)
    if model_providers_cfg_path is None:
        model_providers_cfg_path = MODEL_PROVIDERS_CFG_PATH_CONFIG
    if provider_host is None:
        provider_host = MODEL_PROVIDERS_CFG_HOST
    if provider_port is None:
        provider_port = MODEL_PROVIDERS_CFG_PORT

    init_server(model_platforms_shard=model_platforms_shard,
                started_event=started_event,
                model_providers_cfg_path=model_providers_cfg_path,
                provider_host=provider_host,
                provider_port=provider_port)


def run_api_server(model_platforms_shard: Dict,
                   started_event: mp.Event = None,
                   run_mode: str = None):
    from chatchat.server.api_server.server_app import create_app
    import uvicorn
    from chatchat.server.utils import set_httpx_config
    from chatchat.configs import MODEL_PLATFORMS, API_SERVER
    from model_providers.core.utils.utils import (
        get_config_dict,
        get_log_file,
        get_timestamp_ms,
    )

    from chatchat.configs import LOG_PATH
    MODEL_PLATFORMS.extend(model_platforms_shard['provider_platforms'])
    logger.info(f"Api MODEL_PLATFORMS: {MODEL_PLATFORMS}")
    set_httpx_config()
    app = create_app(run_mode=run_mode)
    _set_app_event(app, started_event)

    host = API_SERVER["host"]
    port = API_SERVER["port"]

    logging_conf = get_config_dict(
        "INFO",
        get_log_file(log_path=LOG_PATH, sub_dir=f"run_api_server_{get_timestamp_ms()}"),

        1024*1024*1024*3,
        1024*1024*1024*3,
    )
    logging.config.dictConfig(logging_conf)  # type: ignore
    uvicorn.run(app, host=host, port=port)


def run_webui(model_platforms_shard: Dict,
              started_event: mp.Event = None, run_mode: str = None):
    import sys
    from chatchat.server.utils import set_httpx_config
    from chatchat.configs import MODEL_PLATFORMS, WEBUI_SERVER
    from model_providers.core.utils.utils import (
        get_config_dict,
        get_log_file,
        get_timestamp_ms,
    )

    from chatchat.configs import LOG_PATH
    if model_platforms_shard.get('provider_platforms'):
        MODEL_PLATFORMS.extend(model_platforms_shard.get('provider_platforms'))
    logger.info(f"Webui MODEL_PLATFORMS: {MODEL_PLATFORMS}")
    set_httpx_config()

    host = WEBUI_SERVER["host"]
    port = WEBUI_SERVER["port"]

    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webui.py')

    flag_options = {'server_address': host,
                    'server_port': port,
                    'theme_base': 'light',
                    'theme_primaryColor': '#165dff',
                    'theme_secondaryBackgroundColor': '#f5f5f5',
                    'theme_textColor': '#000000',
                    'global_disableWatchdogWarning': None,
                    'global_disableWidgetStateDuplicationWarning': None,
                    'global_showWarningOnDirectExecution': None,
                    'global_developmentMode': None, 'global_logLevel': None, 'global_unitTest': None,
                    'global_suppressDeprecationWarnings': None, 'global_minCachedMessageSize': None,
                    'global_maxCachedMessageAge': None, 'global_storeCachedForwardMessagesInMemory': None,
                    'global_dataFrameSerialization': None, 'logger_level': None, 'logger_messageFormat': None,
                    'logger_enableRich': None, 'client_caching': None, 'client_displayEnabled': None,
                    'client_showErrorDetails': None, 'client_toolbarMode': None, 'client_showSidebarNavigation': None,
                    'runner_magicEnabled': None, 'runner_installTracer': None, 'runner_fixMatplotlib': None,
                    'runner_postScriptGC': None, 'runner_fastReruns': None,
                    'runner_enforceSerializableSessionState': None, 'runner_enumCoercion': None,
                    'server_folderWatchBlacklist': None, 'server_fileWatcherType': None, 'server_headless': None,
                    'server_runOnSave': None, 'server_allowRunOnSave': None, 'server_scriptHealthCheckEnabled': None,
                    'server_baseUrlPath': None, 'server_enableCORS': None, 'server_enableXsrfProtection': None,
                    'server_maxUploadSize': None, 'server_maxMessageSize': None, 'server_enableArrowTruncation': None,
                    'server_enableWebsocketCompression': None, 'server_enableStaticServing': None,
                    'browser_serverAddress': None, 'browser_gatherUsageStats': None, 'browser_serverPort': None,
                    'server_sslCertFile': None, 'server_sslKeyFile': None, 'ui_hideTopBar': None,
                    'ui_hideSidebarNav': None, 'magic_displayRootDocString': None,
                    'magic_displayLastExprIfNoSemicolon': None, 'deprecation_showfileUploaderEncoding': None,
                    'deprecation_showImageFormat': None, 'deprecation_showPyplotGlobalUse': None,
                    'theme_backgroundColor': None, 'theme_font': None}

    args = []
    if run_mode == "lite":
        args += [
            "--",
            "lite",
        ]

    try:
        # for streamlit >= 1.12.1
        from streamlit.web import bootstrap
    except ImportError:
        from streamlit import bootstrap


    logging_conf = get_config_dict(
        "INFO",
        get_log_file(log_path=LOG_PATH, sub_dir=f"run_webui_{get_timestamp_ms()}"),

        1024*1024*1024*3,
        1024*1024*1024*3,
        )
    logging.config.dictConfig(logging_conf)  # type: ignore
    bootstrap.load_config_options(flag_options=flag_options)
    bootstrap.run(script_dir, False, args, flag_options)
    started_event.set()


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--all-webui",
        action="store_true",
        help="run model_providers servers,run api.py and webui.py",
        dest="all_webui",
    )
    parser.add_argument(
        "--all-api",
        action="store_true",
        help="run model_providers  servers, run api.py",
        dest="all_api",
    )

    parser.add_argument(
        "--api",
        action="store_true",
        help="run api.py server",
        dest="api",
    )

    parser.add_argument(
        "-w",
        "--webui",
        action="store_true",
        help="run webui.py server",
        dest="webui",
    )
    parser.add_argument(
        "-i",
        "--lite",
        action="store_true",
        help="以Lite模式运行：仅支持在线API的LLM对话、搜索引擎对话",
        dest="lite",
    )
    args = parser.parse_args()
    return args, parser


def dump_server_info(after_start=False, args=None):
    import platform
    import langchain
    from chatchat.server.utils import api_address, webui_address
    from chatchat.configs import VERSION, TEXT_SPLITTER_NAME, DEFAULT_EMBEDDING_MODEL
    print("\n")
    print("=" * 30 + "Langchain-Chatchat Configuration" + "=" * 30)
    print(f"操作系统：{platform.platform()}.")
    print(f"python版本：{sys.version}")
    print(f"项目版本：{VERSION}")
    print(f"langchain版本：{langchain.__version__}")
    print("\n")

    print(f"当前使用的分词器：{TEXT_SPLITTER_NAME}")

    print(f"默认选用的 Embedding 名称： {DEFAULT_EMBEDDING_MODEL}")

    if after_start:
        print("\n")
        print(f"服务端运行信息：")
        if args.api:
            print(
                f"    Chatchat Model providers Server: model_providers_cfg_path_config:{MODEL_PROVIDERS_CFG_PATH_CONFIG}\n"
                f"                                     provider_host:{MODEL_PROVIDERS_CFG_HOST}\n"
                f"                                     provider_host:{MODEL_PROVIDERS_CFG_HOST}\n")

            print(f"    Chatchat Api Server: {api_address()}")
        if args.webui:
            print(f"    Chatchat WEBUI Server: {webui_address()}")
    print("=" * 30 + "Langchain-Chatchat Configuration" + "=" * 30)
    print("\n")


async def start_main_server():
    import time
    import signal
    from chatchat.configs import LOG_PATH
    from model_providers.core.utils.utils import (
        get_config_dict,
        get_log_file,
        get_timestamp_ms,
    )

    logging_conf = get_config_dict(
        "INFO",
        get_log_file(log_path=LOG_PATH, sub_dir=f"start_main_server_{get_timestamp_ms()}"),

        1024*1024*1024*3,
        1024*1024*1024*3,
        )
    logging.config.dictConfig(logging_conf)  # type: ignore
    def handler(signalname):
        """
        Python 3.9 has `signal.strsignal(signalnum)` so this closure would not be needed.
        Also, 3.8 includes `signal.valid_signals()` that can be used to create a mapping for the same purpose.
        """

        def f(signal_received, frame):
            raise KeyboardInterrupt(f"{signalname} received")

        return f

    # This will be inherited by the child process if it is forked (not spawned)
    signal.signal(signal.SIGINT, handler("SIGINT"))
    signal.signal(signal.SIGTERM, handler("SIGTERM"))

    mp.set_start_method("spawn")
    manager = mp.Manager()
    run_mode = None

    args, parser = parse_args()

    if args.all_webui:
        args.api = True
        args.api_worker = True
        args.webui = True
    elif args.all_api:
        args.api = True
        args.api_worker = True
        args.webui = False
    elif args.api:
        args.api = True
        args.api_worker = False
        args.webui = False
    if args.lite:
        args.api = True
        args.api_worker = False
        args.webui = True

    dump_server_info(args=args)

    if len(sys.argv) > 1:
        logger.info(f"正在启动服务：")
        logger.info(f"如需查看 llm_api 日志，请前往 {LOG_PATH}")

    processes = {}

    def process_count():
        return len(processes)

    # 定义全局配置变量,使用 Manager 创建共享字典
    model_platforms_shard = manager.dict()
    model_providers_started = manager.Event()
    if args.api:
        process = Process(
            target=run_init_server,
            name=f"Model providers Server",
            kwargs=dict(model_platforms_shard=model_platforms_shard, started_event=model_providers_started),
            daemon=True,
        )
        processes["model_providers"] = process
    api_started = manager.Event()
    if args.api:
        process = Process(
            target=run_api_server,
            name=f"API Server",
            kwargs=dict(model_platforms_shard=model_platforms_shard, started_event=api_started, run_mode=run_mode),
            daemon=False,
        )
        processes["api"] = process

    webui_started = manager.Event()
    if args.webui:
        process = Process(
            target=run_webui,
            name=f"WEBUI Server",
            kwargs=dict(model_platforms_shard=model_platforms_shard, started_event=webui_started, run_mode=run_mode),
            daemon=True,
        )
        processes["webui"] = process

    if process_count() == 0:
        parser.print_help()
    else:
        try:
            # 保证任务收到SIGINT后，能够正常退出
            if p := processes.get("model_providers"):
                p.start()
                p.name = f"{p.name} ({p.pid})"
                model_providers_started.wait()  # 等待model_providers启动完成

            if p := processes.get("api"):
                p.start()
                p.name = f"{p.name} ({p.pid})"
                api_started.wait()  # 等待api.py启动完成

            if p := processes.get("webui"):
                p.start()
                p.name = f"{p.name} ({p.pid})"
                webui_started.wait()  # 等待webui.py启动完成

            dump_server_info(after_start=True, args=args)

            # 等待所有进程退出
            while processes:
                for p in processes.values():
                    p.join(2)
                    if not p.is_alive():
                        processes.pop(p.name)
        except Exception as e:
            logger.error(e)
            logger.warning("Caught KeyboardInterrupt! Setting stop event...")
        finally:

            for p in processes.values():
                logger.warning("Sending SIGKILL to %s", p)
                # Queues and other inter-process communication primitives can break when
                # process is killed, but we don't care here

                if isinstance(p, dict):
                    for process in p.values():
                        process.kill()
                else:
                    p.kill()

            for p in processes.values():
                logger.info("Process status: %s", p)


def main():
    # 添加这行代码
    cwd = os.getcwd()
    sys.path.append(cwd)
    multiprocessing.freeze_support()
    print("cwd:"+cwd)
    from chatchat.server.knowledge_base.migrate import create_tables
    create_tables()
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
    loop.run_until_complete(start_main_server())


if __name__ == "__main__":
    main()
