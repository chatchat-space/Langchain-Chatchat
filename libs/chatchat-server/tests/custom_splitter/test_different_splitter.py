import os
import sys

from transformers import AutoTokenizer

sys.path.append("../..")
from chatchat.settings import Settings
from chatchat.server.knowledge_base.utils import make_text_splitter


def text(splitter_name):
    from langchain import document_loaders

    # 使用DocumentLoader读取文件
    filepath = "../../knowledge_base/samples/content/test_files/test.txt"
    loader = document_loaders.UnstructuredFileLoader(filepath, autodetect_encoding=True)
    docs = loader.load()
    text_splitter = make_text_splitter(splitter_name, Settings.kb_settings.CHUNK_SIZE, Settings.kb_settings.OVERLAP_SIZE)
    if splitter_name == "MarkdownHeaderTextSplitter":
        docs = text_splitter.split_text(docs[0].page_content)
        for doc in docs:
            if doc.metadata:
                doc.metadata["source"] = os.path.basename(filepath)
    else:
        docs = text_splitter.split_documents(docs)
    for doc in docs:
        print(doc)
    return docs


import pytest
from langchain.docstore.document import Document


@pytest.mark.parametrize(
    "splitter_name",
    [
        "ChineseRecursiveTextSplitter",
        "SpacyTextSplitter",
        "RecursiveCharacterTextSplitter",
        "MarkdownHeaderTextSplitter",
    ],
)
def test_different_splitter(splitter_name):
    try:
        docs = text(splitter_name)
        assert isinstance(docs, list)
        if len(docs) > 0:
            assert isinstance(docs[0], Document)
    except Exception as e:
        pytest.fail(
            f"test_different_splitter failed with {splitter_name}, error: {str(e)}"
        )
