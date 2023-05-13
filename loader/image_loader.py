"""Loader that loads image files."""
from typing import List

from langchain.document_loaders.unstructured import UnstructuredFileLoader
from paddleocr import PaddleOCR
import os


class UnstructuredPaddleImageLoader(UnstructuredFileLoader):
    """Loader that uses unstructured to load image files, such as PNGs and JPGs."""

    def _get_elements(self) -> List:
        def image_ocr_txt(filepath, dir_path="tmp_files"):
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            filename = os.path.split(filepath)[-1]
            ocr = PaddleOCR(lang="ch", use_gpu=False, show_log=False)
            result = ocr.ocr(img=filepath)

            ocr_result = [i[1][0] for line in result for i in line]
            txt_file_path = os.path.join(dir_path, "%s.txt" % (filename))
            with open(txt_file_path, 'w', encoding='utf-8') as fout:
                fout.write("\n".join(ocr_result))
            return txt_file_path

        txt_file_path = image_ocr_txt(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(filename=txt_file_path, **self.unstructured_kwargs)
