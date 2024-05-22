import logging
import os
from pathlib import Path

import langchain


# 是否显示详细日志
log_verbose = False
langchain.verbose = False

# 通常情况下不需要更改以下内容

# chatchat 项目根目录
CHATCHAT_ROOT = str(Path(__file__).absolute().parent.parent)

# 用户数据根目录
DATA_PATH = os.path.join(CHATCHAT_ROOT, "data")
if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)

# 项目相关图片
IMG_DIR = os.path.join(CHATCHAT_ROOT, "img")
if not os.path.exists(IMG_DIR):
    os.mkdir(IMG_DIR)

# nltk 模型存储路径
NLTK_DATA_PATH = os.path.join(DATA_PATH, "nltk_data")
import nltk
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

# 日志格式
LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format=LOG_FORMAT)


# 日志存储路径
LOG_PATH = os.path.join(DATA_PATH, "logs")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

# 模型生成内容（图片、视频、音频等）保存位置
MEDIA_PATH = os.path.join(DATA_PATH, "media")
if not os.path.exists(MEDIA_PATH):
    os.mkdir(MEDIA_PATH)
    os.mkdir(os.path.join(MEDIA_PATH, "image"))
    os.mkdir(os.path.join(MEDIA_PATH, "audio"))
    os.mkdir(os.path.join(MEDIA_PATH, "video"))

# 临时文件目录，主要用于文件对话
BASE_TEMP_DIR = os.path.join(DATA_PATH, "temp")
if not os.path.exists(BASE_TEMP_DIR):
    os.mkdir(BASE_TEMP_DIR)
