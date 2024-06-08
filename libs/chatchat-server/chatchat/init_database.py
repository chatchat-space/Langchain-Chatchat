# Description: 初始化数据库，包括创建表、导入数据、更新向量空间等操作
from datetime import datetime
import multiprocessing as mp
from typing import Dict

from chatchat.server.knowledge_base.migrate import (create_tables, reset_tables, import_from_db,
                                           folder2db, prune_db_docs, prune_folder_files)
from chatchat.configs import DEFAULT_EMBEDDING_MODEL, MODEL_PLATFORMS, logger



def run_init_model_provider(
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


def main():
    import argparse

    parser = argparse.ArgumentParser(description="please specify only one operate method once time.")

    parser.add_argument(
        "-r",
        "--recreate-vs",
        action="store_true",
        help=('''
            recreate vector store.
            use this option if you have copied document files to the content folder, but vector store has not been populated or DEFAUL_VS_TYPE/DEFAULT_EMBEDDING_MODEL changed.
            '''
        )
    )
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help=("create empty tables if not existed")
    )
    parser.add_argument(
        "--clear-tables",
        action="store_true",
        help=("create empty tables, or drop the database tables before recreate vector stores")
    )
    parser.add_argument(
        "--import-db",
        help="import tables from specified sqlite database"
    )
    parser.add_argument(
        "-u",
        "--update-in-db",
        action="store_true",
        help=('''
            update vector store for files exist in database.
            use this option if you want to recreate vectors for files exist in db and skip files exist in local folder only.
            '''
        )
    )
    parser.add_argument(
        "-i",
        "--increment",
        action="store_true",
        help=('''
            update vector store for files exist in local folder and not exist in database.
            use this option if you want to create vectors incrementally.
            '''
        )
    )
    parser.add_argument(
        "--prune-db",
        action="store_true",
        help=('''
            delete docs in database that not existed in local folder.
            it is used to delete database docs after user deleted some doc files in file browser
            '''
        )
    )
    parser.add_argument(
        "--prune-folder",
        action="store_true",
        help=('''
            delete doc files in local folder that not existed in database.
            is is used to free local disk space by delete unused doc files.
            '''
        )
    )
    parser.add_argument(
        "-n",
        "--kb-name",
        type=str,
        nargs="+",
        default=[],
        help=("specify knowledge base names to operate on. default is all folders exist in KB_ROOT_PATH.")
    )
    parser.add_argument(
        "-e",
        "--embed-model",
        type=str,
        default=DEFAULT_EMBEDDING_MODEL,
        help=("specify embeddings model.")
    )

    args = parser.parse_args()
    start_time = datetime.now()

    mp.set_start_method("spawn")
    manager = mp.Manager()

    # 定义全局配置变量,使用 Manager 创建共享字典
    model_platforms_shard = manager.dict()
    model_providers_started = manager.Event()
    processes = {}
    process = mp.Process(
        target=run_init_model_provider,
        name=f"Model providers Server",
        kwargs=dict(model_platforms_shard=model_platforms_shard, started_event=model_providers_started),
        daemon=True,
    )
    processes["model_providers"] = process
    try:
        # 保证任务收到SIGINT后，能够正常退出
        if p := processes.get("model_providers"):
            p.start()
            p.name = f"{p.name} ({p.pid})"
            model_providers_started.wait()  # 等待model_providers启动完成
            MODEL_PLATFORMS.extend(model_platforms_shard['provider_platforms'])
            logger.info(f"Api MODEL_PLATFORMS: {MODEL_PLATFORMS}")


        if args.create_tables:
            create_tables() # confirm tables exist

        if args.clear_tables:
            reset_tables()
            print("database tables reset")

        if args.recreate_vs:
            create_tables()
            print("recreating all vector stores")
            folder2db(kb_names=args.kb_name, mode="recreate_vs", embed_model=args.embed_model)
        elif args.import_db:
            import_from_db(args.import_db)
        elif args.update_in_db:
            folder2db(kb_names=args.kb_name, mode="update_in_db", embed_model=args.embed_model)
        elif args.increment:
            folder2db(kb_names=args.kb_name, mode="increment", embed_model=args.embed_model)
        elif args.prune_db:
            prune_db_docs(args.kb_name)
        elif args.prune_folder:
            prune_folder_files(args.kb_name)

        end_time = datetime.now()
        print(f"总计用时： {end_time-start_time}")
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


if __name__ == "__main__":
    main()
