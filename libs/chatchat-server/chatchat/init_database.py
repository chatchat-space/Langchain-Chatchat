# Description: 初始化数据库，包括创建表、导入数据、更新向量空间等操作
from datetime import datetime
import multiprocessing as mp
import sys
import time
from typing import Dict

import click

from chatchat.settings import Settings
from chatchat.server.knowledge_base.migrate import (
    create_tables,
    folder2db,
    import_from_db,
    prune_db_docs,
    prune_folder_files,
    reset_tables,
)
from chatchat.utils import build_logger
from chatchat.server.utils import get_default_embedding


logger = build_logger()


def worker(args: dict):
    start_time = datetime.now()

    try:
        if args.get("create_tables"):
            create_tables()  # confirm tables exist

        if args.get("clear_tables"):
            reset_tables()
            print("database tables reset")

        if args.get("recreate_vs"):
            create_tables()
            print("recreating all vector stores")
            folder2db(
                kb_names=args.get("kb_name"), mode="recreate_vs", embed_model=args.get("embed_model")
            )
        elif args.get("import_db"):
            import_from_db(args.get("import_db"))
        elif args.get("update_in_db"):
            folder2db(
                kb_names=args.get("kb_name"), mode="update_in_db", embed_model=args.get("embed_model")
            )
        elif args.get("increment"):
            folder2db(
                kb_names=args.get("kb_name"), mode="increment", embed_model=args.get("embed_model")
            )
        elif args.get("prune_db"):
            prune_db_docs(args.get("kb_name"))
        elif args.get("prune_folder"):
            prune_folder_files(args.get("kb_name"))

        end_time = datetime.now()
        print(f"总计用时\t：{end_time-start_time}\n")
    except Exception as e:
        logger.exception(e)


@click.command(help="知识库相关功能")
@click.option(
        "-r",
        "--recreate-vs",
        is_flag=True,
        help=(
            """
            recreate vector store.
            use this option if you have copied document files to the content folder, but vector store has not been populated or DEFAUL_VS_TYPE/DEFAULT_EMBEDDING_MODEL changed.
            """
        ),
)
@click.option(
        "--create-tables",
        is_flag=True,
        help=("create empty tables if not existed"),
)
@click.option(
        "--clear-tables",
        is_flag=True,
        help=(
            "create empty tables, or drop the database tables before recreate vector stores"
        ),
)
@click.option(
        "-u",
        "--update-in-db",
        is_flag=True,
        help=(
            """
            update vector store for files exist in database.
            use this option if you want to recreate vectors for files exist in db and skip files exist in local folder only.
            """
        ),
)
@click.option(
        "-i",
        "--increment",
        is_flag=True,
        help=(
            """
            update vector store for files exist in local folder and not exist in database.
            use this option if you want to create vectors incrementally.
            """
        ),
)
@click.option(
        "--prune-db",
        is_flag=True,
        help=(
            """
            delete docs in database that not existed in local folder.
            it is used to delete database docs after user deleted some doc files in file browser
            """
        ),
)
@click.option(
        "--prune-folder",
        is_flag=True,
        help=(
            """
            delete doc files in local folder that not existed in database.
            is is used to free local disk space by delete unused doc files.
            """
        ),
)
@click.option(
        "-n",
        "--kb-name",
        multiple=True,
        default=[],
        help=(
            "specify knowledge base names to operate on. default is all folders exist in KB_ROOT_PATH."
        ),
)
@click.option(
        "-e",
        "--embed-model",
        type=str,
        default=get_default_embedding(),
        help=("specify embeddings model."),
)
@click.option(
        "--import-db",
        help="import tables from specified sqlite database"
)
def main(**kwds):
    p = mp.Process(target=worker, args=(kwds,), daemon=True)
    p.start()
    while p.is_alive():
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            logger.warning("Caught KeyboardInterrupt! Setting stop event...")
            p.terminate()
            sys.exit()


if __name__ == "__main__":
    mp.set_start_method("spawn")
    main()
