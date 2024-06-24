# Description: 初始化数据库，包括创建表、导入数据、更新向量空间等操作
import multiprocessing as mp
from datetime import datetime
from typing import Dict

from chatchat.configs import DEFAULT_EMBEDDING_MODEL, MODEL_PLATFORMS, logger
from chatchat.server.knowledge_base.migrate import (
    create_tables,
    folder2db,
    import_from_db,
    prune_db_docs,
    prune_folder_files,
    reset_tables,
)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="please specify only one operate method once time."
    )

    parser.add_argument(
        "-r",
        "--recreate-vs",
        action="store_true",
        help=(
            """
            recreate vector store.
            use this option if you have copied document files to the content folder, but vector store has not been populated or DEFAUL_VS_TYPE/DEFAULT_EMBEDDING_MODEL changed.
            """
        ),
    )
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help=("create empty tables if not existed"),
    )
    parser.add_argument(
        "--clear-tables",
        action="store_true",
        help=(
            "create empty tables, or drop the database tables before recreate vector stores"
        ),
    )
    parser.add_argument(
        "--import-db", help="import tables from specified sqlite database"
    )
    parser.add_argument(
        "-u",
        "--update-in-db",
        action="store_true",
        help=(
            """
            update vector store for files exist in database.
            use this option if you want to recreate vectors for files exist in db and skip files exist in local folder only.
            """
        ),
    )
    parser.add_argument(
        "-i",
        "--increment",
        action="store_true",
        help=(
            """
            update vector store for files exist in local folder and not exist in database.
            use this option if you want to create vectors incrementally.
            """
        ),
    )
    parser.add_argument(
        "--prune-db",
        action="store_true",
        help=(
            """
            delete docs in database that not existed in local folder.
            it is used to delete database docs after user deleted some doc files in file browser
            """
        ),
    )
    parser.add_argument(
        "--prune-folder",
        action="store_true",
        help=(
            """
            delete doc files in local folder that not existed in database.
            is is used to free local disk space by delete unused doc files.
            """
        ),
    )
    parser.add_argument(
        "-n",
        "--kb-name",
        type=str,
        nargs="+",
        default=[],
        help=(
            "specify knowledge base names to operate on. default is all folders exist in KB_ROOT_PATH."
        ),
    )
    parser.add_argument(
        "-e",
        "--embed-model",
        type=str,
        default=DEFAULT_EMBEDDING_MODEL,
        help=("specify embeddings model."),
    )

    args = parser.parse_args()
    start_time = datetime.now()

    mp.set_start_method("spawn")
    manager = mp.Manager()

    processes = {}

    try:
        if args.create_tables:
            create_tables()  # confirm tables exist

        if args.clear_tables:
            reset_tables()
            print("database tables reset")

        if args.recreate_vs:
            create_tables()
            print("recreating all vector stores")
            folder2db(
                kb_names=args.kb_name, mode="recreate_vs", embed_model=args.embed_model
            )
        elif args.import_db:
            import_from_db(args.import_db)
        elif args.update_in_db:
            folder2db(
                kb_names=args.kb_name, mode="update_in_db", embed_model=args.embed_model
            )
        elif args.increment:
            folder2db(
                kb_names=args.kb_name, mode="increment", embed_model=args.embed_model
            )
        elif args.prune_db:
            prune_db_docs(args.kb_name)
        elif args.prune_folder:
            prune_folder_files(args.kb_name)

        end_time = datetime.now()
        print(f"总计用时\t：{end_time-start_time}\n")
    except Exception as e:
        logger.error(e, exc_info=True)
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
