"""Loader that loads image files."""
from typing import List

from langchain.document_loaders.unstructured import UnstructuredFileLoader
from paddleocr import PaddleOCR
import os
import fitz


class UnstructuredPaddlePDFLoader(UnstructuredFileLoader):
    """Loader that uses unstructured to load image files, such as PNGs and JPGs."""

    def _get_elements(self) -> List:
        def pdf_ocr_txt(filepath, dir_path="tmp_files"):
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            filename = os.path.split(filepath)[-1]
            ocr = PaddleOCR(lang="ch", use_gpu=False, show_log=False)
            doc = fitz.open(filepath)
            txt_file_path = os.path.join(dir_path, "%s.txt" % (filename))
            img_name = './img/.tmp.png'
            with open(txt_file_path, 'w', encoding='utf-8') as fout:

                for i in range(doc.page_count):
                    page = doc[i]
                    text = page.get_text("")
                    fout.write(text)
                    fout.write("\n")

                    img_list = page.get_images()
                    for img in img_list:
                        pix = fitz.Pixmap(doc, img[0])

                        pix.save(img_name)

                        result = ocr.ocr(img_name)
                        ocr_result = [i[1][0] for line in result for i in line]
                        fout.write("\n".join(ocr_result))
            os.remove(img_name)
            return txt_file_path

        txt_file_path = pdf_ocr_txt(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(filename=txt_file_path, **self.unstructured_kwargs)
