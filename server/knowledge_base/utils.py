import os
from configs.model_config import KB_ROOT_PATH


def get_kb_path(knowledge_base_name: str):
    return os.path.join(KB_ROOT_PATH, knowledge_base_name)


def get_doc_path(knowledge_base_name: str):
    return os.path.join(get_kb_path(knowledge_base_name), "content")


def get_vs_path(knowledge_base_name: str):
    return os.path.join(get_kb_path(knowledge_base_name), "vector_store")


def get_file_path(knowledge_base_name: str, doc_name: str):
    return os.path.join(get_doc_path(knowledge_base_name), doc_name)


def validate_kb_name(knowledge_base_id: str) -> bool:
    # 检查是否包含预期外的字符或路径攻击关键字
    if "../" in knowledge_base_id:
        return False
    return True


def file2text(filepath):
    # TODO: 替换处理方式
    from langchain.document_loaders import UnstructuredFileLoader
    loader = UnstructuredFileLoader(filepath)

    from langchain.text_splitter import CharacterTextSplitter
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    docs = loader.load_and_split(text_splitter)
    return docs


if __name__ == "__main__":
    filepath = "/Users/liuqian/PycharmProjects/chatchat/knowledge_base/123/content/test.txt"
    docs = file2text(filepath)
