import os

from transformers import AutoTokenizer
import sys

sys.path.append("../..")
from configs.model_config import (
    CHUNK_SIZE,
    OVERLAP_SIZE,
    text_splitter_dict, llm_model_dict, LLM_MODEL, TEXT_SPLITTER_NAME
)
import langchain.document_loaders
import importlib


def test_different_splitter(splitter_name, chunk_size: int = CHUNK_SIZE,
                            chunk_overlap: int = OVERLAP_SIZE, ):
    if splitter_name == "MarkdownHeaderTextSplitter":  # MarkdownHeaderTextSplitter特殊判定
        headers_to_split_on = text_splitter_dict[splitter_name]['headers_to_split_on']
        text_splitter = langchain.text_splitter.MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on)

    else:

        try:  ## 优先使用用户自定义的text_splitter
            text_splitter_module = importlib.import_module('text_splitter')
            TextSplitter = getattr(text_splitter_module, splitter_name)
        except:  ## 否则使用langchain的text_splitter
            text_splitter_module = importlib.import_module('langchain.text_splitter')
            TextSplitter = getattr(text_splitter_module, splitter_name)

        if text_splitter_dict[splitter_name]["source"] == "tiktoken":
            try:
                text_splitter = TextSplitter.from_tiktoken_encoder(
                    encoding_name=text_splitter_dict[splitter_name]["tokenizer_name_or_path"],
                    pipeline="zh_core_web_sm",
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            except:
                text_splitter = TextSplitter.from_tiktoken_encoder(
                    encoding_name=text_splitter_dict[splitter_name]["tokenizer_name_or_path"],
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
        elif text_splitter_dict[splitter_name]["source"] == "huggingface":
            if text_splitter_dict[splitter_name]["tokenizer_name_or_path"] == "":
                text_splitter_dict[splitter_name]["tokenizer_name_or_path"] = \
                    llm_model_dict[LLM_MODEL]["local_model_path"]

            if text_splitter_dict[splitter_name]["tokenizer_name_or_path"] == "gpt2":
                from transformers import GPT2TokenizerFast
                from langchain.text_splitter import CharacterTextSplitter
                tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")  ##  这里选择你用的tokenizer
            else:
                tokenizer = AutoTokenizer.from_pretrained(
                    text_splitter_dict[splitter_name]["tokenizer_name_or_path"],
                    trust_remote_code=True)
            text_splitter = TextSplitter.from_huggingface_tokenizer(
                tokenizer=tokenizer,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

    return text_splitter


if __name__ == "__main__":
    from langchain import document_loaders

    # 使用DocumentLoader读取文件
    filepath = "../../knowledge_base/samples/content/test.txt"
    loader = document_loaders.UnstructuredFileLoader(filepath, autodetect_encoding=True)
    docs = loader.load()
    text_splitter = text_different_splitter(TEXT_SPLITTER_NAME, CHUNK_SIZE, OVERLAP_SIZE)
    # 使用text_splitter进行分词

    if TEXT_SPLITTER_NAME == "MarkdownHeaderTextSplitter":
        split_docs = text_splitter.split_text(docs[0].page_content)
        for doc in docs:
            # 如果文档有元数据
            if doc.metadata:
                doc.metadata["source"] = os.path.basename(filepath)
    else:
        split_docs = text_splitter.split_documents(docs)

    # 打印分词结果
    for doc in split_docs:
        print(doc)
