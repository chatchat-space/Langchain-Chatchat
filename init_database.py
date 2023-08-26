from server.knowledge_base.migrate import create_tables, reset_tables, folder2db, recreate_all_vs, list_kbs_from_folder
from configs.model_config import NLTK_DATA_PATH
import nltk
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path
from startup import dump_server_info
from datetime import datetime


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.formatter_class = argparse.RawTextHelpFormatter

    parser.add_argument(
        "--recreate-vs",
        action="store_true",
        help=('''
            recreate all vector store.
            use this option if you have copied document files to the content folder, but vector store has not been populated or DEFAUL_VS_TYPE/EMBEDDING_MODEL changed.
            if your vector store is ready with the configs, just skip this option to fill info to database only.
            '''
        )
    )
    args = parser.parse_args()

    dump_server_info()

    start_time = datetime.now()

    if args.recreate_vs:
        reset_tables()
        print("database talbes reseted")
        print("recreating all vector stores")
        recreate_all_vs()
    else:
        create_tables()
        print("database talbes created")
        print("filling kb infos to database")
        for kb in list_kbs_from_folder():
            folder2db(kb, "fill_info_only")

    end_time = datetime.now()
    print(f"总计用时： {end_time-start_time}")
