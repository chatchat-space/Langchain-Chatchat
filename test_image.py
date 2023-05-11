from paddleocr import PaddleOCR
import os


def image_ocr_txt(filepath, dir_path="tmp_files"):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    filename = os.path.split(filepath)[-1]
    ocr = PaddleOCR(lang="ch", use_gpu=False, show_log=False)
    result = ocr.ocr(img=filepath)

    ocr_result = [i[1][0] for line in result for i in line]
    txt_file_path = os.path.join(dir_path, "%s.txt" % (filename))
    print("\n".join(ocr_result))
    fout = open(txt_file_path, 'w', encoding='utf-8')
    fout.write("\n".join(ocr_result))
    fout.close()
    return txt_file_path


filepath = "./img/test.jpg"
txt_file_path = image_ocr_txt(filepath)
