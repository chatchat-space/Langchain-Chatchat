from configs.model_config import *
import nltk

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

filepath = "./img/test.jpg"
from loader import UnstructuredPaddleImageLoader

loader = UnstructuredPaddleImageLoader(filepath, mode="elements")
docs = loader.load()
for doc in docs:
    print(doc)
