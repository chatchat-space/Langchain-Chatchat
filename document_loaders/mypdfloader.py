from typing import List
from langchain.document_loaders.unstructured import UnstructuredFileLoader
import tqdm
import os
import pickle
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from params import *
def keyphrase_extraction(text):
    tr4w = TextRank4Keyword()
    keyword = []
    tr4w.analyze(text=text, lower=True, window=2)
    for item in tr4w.get_keywords(50, word_min_len=2):
        # print(item.word)
        keyword.append(item.word)

    for phrase in tr4w.get_keyphrases(keywords_num=50, min_occur_num= 2):
        # print(phrase)
        keyword.append(phrase)
    # 热词之间用|分隔
    keyphrases = "|".join(keyword)
    # 当前文件的父级目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    with open(os.path.join(parent_dir,"knowledge_base/keyphrases.pkl"), "wb") as f:
        pickle.dump(keyphrases, f)

class RapidOCRPDFLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        def pdf2text(filepath):
            import fitz # pyMuPDF里面的fitz包，不要与pip install fitz混淆
            from rapidocr_onnxruntime import RapidOCR
            import numpy as np
            ocr = RapidOCR()
            doc = fitz.open(filepath)
            resp = ""

            b_unit = tqdm.tqdm(total=doc.page_count, desc="RapidOCRPDFLoader context page index: 0")
            for i, page in enumerate(doc):

                # 更新描述
                b_unit.set_description("RapidOCRPDFLoader context page index: {}".format(i))
                # 立即显示进度条更新结果
                b_unit.refresh()
                # TODO: 依据文本与图片顺序调整处理方式
                text = page.get_text("")
                resp += text + "\n"

                img_list = page.get_images()
                for img in img_list:
                    pix = fitz.Pixmap(doc, img[0])
                    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, -1)
                    result, _ = ocr(img_array)
                    if result:
                        ocr_result = [line[1] for line in result]
                        resp += "\n".join(ocr_result)

                # 更新进度
                b_unit.update(1)
            return resp

        text = pdf2text(self.file_path)
        keyphrase_extraction(text)
        from unstructured.partition.text import partition_text
        return partition_text(text=text, **self.unstructured_kwargs)


if __name__ == "__main__":
    loader = RapidOCRPDFLoader(file_path="../tests/samples/ocr_test.pdf")
    docs = loader.load()
    print(docs)
