"""Loader that loads image files."""
from typing import Any, List, Union

from langchain.document_loaders.unstructured import UnstructuredFileLoader
from paddleocr import PaddleOCR
import os
import fitz
import nltk
import uuid
from configs.model_config import NLTK_DATA_PATH
from configs.model_config import KB_TMP_PATH, logger

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

class UnstructuredPaddlePDFLoader(UnstructuredFileLoader):
    """Loader that uses unstructured to load image files, such as PNGs and JPGs."""

    def __init__(self, file_path: str, orc:PaddleOCR = None, mode: str = "single", **unstructured_kwargs: Any):
        super().__init__(file_path, mode, **unstructured_kwargs)
        self.ocr = orc

    def _get_elements(self) -> List:
        def pdf_ocr_txt(filepath, dir_path="tmp_files"):
            dir_path = str(uuid.uuid4())
            full_dir_path = KB_TMP_PATH
            doc = fitz.open(filepath)
            txt_file_path = os.path.join(full_dir_path, f"{os.path.split(filepath)[-1]}.txt")
            img_name = os.path.join(full_dir_path, f"tmp-{dir_path}.png")
            logger.info(f"read full {txt_file_path} and image {img_name}")
            with open(txt_file_path, 'w', encoding='utf-8') as fout:
                for i in range(doc.page_count):
                    page = doc[i]
                    text = page.get_text("")
                    fout.write(text)
                    fout.write("\n")

                    img_list = page.get_images()
                    for img in img_list:
                        pix = fitz.Pixmap(doc, img[0])
                        if pix.n - pix.alpha >= 4:
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                        pix.save(img_name)
                        result = self.ocr.ocr(img_name)
                        ocr_result = [i[1][0] for line in result for i in line]
                        fout.write("\n".join(ocr_result))
            if os.path.exists(img_name):
                os.remove(img_name)
            return txt_file_path

        txt_file_path = pdf_ocr_txt(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(filename=txt_file_path, **self.unstructured_kwargs)


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base", "samples", "content", "test.pdf")
    loader = UnstructuredPaddlePDFLoader(filepath, mode="elements")
    docs = loader.load()
    for doc in docs:
        print(doc)
