from configs.model_config import *
import nltk

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

filepath = "docs/test.pdf"
from loader import UnstructuredPaddlePDFLoader

loader = UnstructuredPaddlePDFLoader(filepath, mode="elements")
docs = loader.load()
for doc in docs:
    print(doc)
