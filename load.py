import argparse
import sys
import os
import shutil
from chains.local_doc_qa import LocalDocQA
import models.shared as shared
from models.loader.args import parser
from models.loader import LoaderCheckPoint
from chains.local_doc_qa import tree

VS_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_store")

UPLOAD_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "content")

local_doc_qa = LocalDocQA()


def get_vs_path(local_doc_id: str):
    return os.path.join(VS_ROOT_PATH, local_doc_id)

def get_file_path(local_doc_id: str, doc_name: str):
    return os.path.join(UPLOAD_ROOT_PATH, local_doc_id, doc_name)

def load_file(path, knowledge_base_id):
    vs_path = get_vs_path(knowledge_base_id)
    vs_path, loaded_files, failed_files = local_doc_qa.init_knowledge_vector_store(path, vs_path)
    if len(loaded_files) > 0:
        file_status = f"{path} 已上传至知识库 {knowledge_base_id}"
        print(file_status)
        if len(failed_files) > 0:
            print( f"{len(failed_files)}个文件上传失败：{failed_files}")
        return file_status
    else:
        file_status = "文件上传失败，请重新上传"
        print(file_status)
        return file_status

if __name__ == "__main__":
    parser.add_argument("--base", type=str, help='Knowlege Base name, alpha beta charactor only')
    parser.add_argument("--path", type=str, help='File or Directory to import')
    args = None
    args = parser.parse_args()
    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM()
    llm_model_ins.set_history_len(10)
    local_doc_qa.init_cfg(llm_model=llm_model_ins)

    if(os.path.exists(args.path)):
        # create knowledge path and source content path
        if not os.path.exists(os.path.join(UPLOAD_ROOT_PATH, args.base)):
            os.makedirs(os.path.join(UPLOAD_ROOT_PATH, args.base))
        if not os.path.exists(os.path.join(VS_ROOT_PATH, args.base)):
            os.makedirs(os.path.join(VS_ROOT_PATH, args.base))
        load_file(os.path.realpath(args.path), args.base)
    else:
        print("path not exist")