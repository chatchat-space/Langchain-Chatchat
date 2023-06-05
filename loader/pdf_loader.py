"""Loader that loads image files."""
from typing import List

from langchain.document_loaders.unstructured import UnstructuredFileLoader
from paddleocr import PaddleOCR
import os
import fitz
import nltk
from configs.model_config import NLTK_DATA_PATH
from pdf2docx import Converter
import pypandoc
import re

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path


class UnstructuredPaddlePDFLoader(UnstructuredFileLoader):
    """Loader that uses unstructured to load image files, such as PNGs and JPGs."""

    def _get_elements(self) -> List:

        def pdf_ocr_txt(pdfpath, txt_file_path, img_name):
            ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, show_log=False)
            doc = fitz.open(pdfpath)

            with open(txt_file_path, 'a+', encoding='utf-8') as fout:
                for i in range(doc.page_count):
                    page = doc[i]

                    d = page.get_text("dict", sort=True)
                    for cur_block in d["blocks"]:
                        if cur_block['type'] == 0:
                            block_text = []
                            for line in cur_block['lines']:
                                for span in line['spans']:
                                    block_text.append(span['text'])
                            fout.write(''.join(block_text))
                            fout.write('\n')
                        elif cur_block['type'] == 1:
                            pix = fitz.Pixmap(cur_block['image'])
                            if pix.n - pix.alpha >= 4:
                                pix = fitz.Pixmap(fitz.csRGB, pix)
                            pix.save(img_name)

                            result = ocr.ocr(img_name)
                            ocr_result = [i[1][0] for line in result for i in line]
                            fout.write("\n".join(ocr_result))
                            fout.write("\n")
                        else:
                            print(cur_block['type'])

            if os.path.exists(img_name):
                os.remove(img_name)

        def pdf_markdown_txt(pdfpath, txt_file_path, docx_file):
            # pdf -> docx
            cv = Converter(pdfpath)
            cv.convert(docx_file, debug=False, ignore_page_error=True, multi_processing=False,
                       extract_stream_table=True,
                       parse_lattice_table=True,
                       parse_stream_table=True,
                       delete_end_line_hyphen=True)
            cv.close()

            # docx -> plain text with grid tables
            pdoc_args = ['--no-highlight', '--wrap=none', '--columns=128', '--extract-media=tmp_media']
            format = "plain-simple_tables-multiline_tables-pipe_tables" \
                     "+grid_tables-escaped_line_breaks-table_captions-smart-auto_identifiers"
            outputfilename = docx_file + '.txt'
            pypandoc.convert_file(docx_file, format, 'docx', outputfile=outputfilename, extra_args=pdoc_args)

            # clean tables
            with open(outputfilename, encoding='utf-8') as fin:
                lines = fin.readlines()

            def is_grid_table_line1(line):
                return len(line) >= 3 and line[:2] == '+=' and line[-2:] == '=+'

            def is_grid_table_line2(line):
                return len(line) >= 3 and line[:2] == '+-' and line[-2:] == '-+'

            def is_chart_table_line(line):
                return bool(re.match(r'^\+(-)+\+$', line))

            newlines = []
            chart_table_start = False
            for line_count, line in enumerate(lines):
                line = line.rstrip()
                if is_chart_table_line(line):
                    chart_table_start = not chart_table_start
                    continue

                if chart_table_start and line.startswith("| ") and line.endswith(" |"):
                    continue
                if chart_table_start and line.startswith("+=") and line.endswith("=+"):
                    continue

                if is_grid_table_line2(line):
                    continue
                elif is_grid_table_line1(line):
                    new_text = re.sub('=+', '-', line)
                    new_text = new_text.replace('+', '|')
                elif len(line) >= 2 and line[:1] == '|' and line[-1:] == '|':
                    new_text = re.sub('\s+', ' ', line)
                    last_line = lines[line_count - 1].rstrip()
                    if is_grid_table_line1(last_line) or is_grid_table_line2(last_line):
                        pass
                    else:
                        # 合并
                        last_line_items = newlines[-1].split('|')
                        this_line_items = new_text.split('|')
                        if len(last_line_items) == len(this_line_items):
                            n = len(last_line_items)
                            for i in range(n):
                                if this_line_items[i].strip():
                                    last_line_items[i] += this_line_items[i]
                            newlines[-1] = '|'.join(last_line_items)
                            continue

                else:
                    new_text = line
                newlines.append(new_text)

            with open(txt_file_path, 'a+', encoding='utf-8') as fout:
                fout.write('\n'.join(newlines))
                fout.write('\n')

        dir_path = "tmp_files"
        full_dir_path = os.path.join(os.path.dirname(self.file_path), dir_path)
        if not os.path.exists(full_dir_path):
            os.makedirs(full_dir_path)

        txt_file_path = os.path.join(full_dir_path, f"{os.path.split(self.file_path)[-1]}.txt")
        with open(txt_file_path, 'w', encoding='utf-8') as _:
            pass
        img_name = os.path.join(full_dir_path, 'tmp.png')
        docx_file = os.path.join(full_dir_path, f"{os.path.split(self.file_path)[-1]}.docx")

        pdf_markdown_txt(self.file_path, txt_file_path, docx_file)
        pdf_ocr_txt(self.file_path, txt_file_path, img_name)

        from unstructured.partition.text import partition_text
        return partition_text(filename=txt_file_path, **self.unstructured_kwargs)


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "content", "samples", "test.pdf")
    loader = UnstructuredPaddlePDFLoader(filepath, mode="elements")
    docs = loader.load()
    for doc in docs:
        print(doc)
