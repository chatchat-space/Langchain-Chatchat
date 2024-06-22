import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

sys.path.append(str(Path(__file__).parent))
import _core_config as core_config

logger = logging.getLogger()


class ConfigBasic(core_config.Config):
    log_verbose: Optional[bool] = None
    """是否开启日志详细信息"""
    CHATCHAT_ROOT: Optional[str] = None
    """项目根目录"""
    DATA_PATH: Optional[str] = None
    """用户数据根目录"""
    IMG_DIR: Optional[str] = None
    """项目相关图片"""
    NLTK_DATA_PATH: Optional[str] = None
    """nltk 模型存储路径"""
    LOG_FORMAT: Optional[str] = None
    """日志格式"""
    LOG_PATH: Optional[str] = None
    """日志存储路径"""
    MEDIA_PATH: Optional[str] = None
    """模型生成内容（图片、视频、音频等）保存位置"""
    BASE_TEMP_DIR: Optional[str] = None
    """临时文件目录，主要用于文件对话"""

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__

    def __str__(self):
        return self.to_json()


@dataclass
class ConfigBasicFactory(core_config.ConfigFactory[ConfigBasic]):
    """Basic config for ChatChat"""

    def __init__(self):
        # 日志格式
        self.LOG_FORMAT = (
            "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
        )
        logging.basicConfig(format=self.LOG_FORMAT)
        self.LOG_VERBOSE = False
        self.CHATCHAT_ROOT = str(Path(__file__).absolute().parent.parent)
        # 用户数据根目录
        self.DATA_PATH = os.path.join(self.CHATCHAT_ROOT, "data")
        self._DATA_PATH = os.path.join(self.CHATCHAT_ROOT, "data")
        if not os.path.exists(self._DATA_PATH):
            os.makedirs(self._DATA_PATH, exist_ok=True)

        self._init_data_dir()

        # 项目相关图片
        self.IMG_DIR = os.path.join(self.CHATCHAT_ROOT, "img")
        if not os.path.exists(self.IMG_DIR):
            os.makedirs(self.IMG_DIR, exist_ok=True)

    def log_verbose(self, verbose: bool):
        self.LOG_VERBOSE = verbose

    def data_path(self, path: str):
        self.DATA_PATH = path
        if not os.path.exists(self.DATA_PATH):
            os.makedirs(self.DATA_PATH, exist_ok=True)
        # 复制_DATA_PATH数据到DATA_PATH
        if self._DATA_PATH != self.DATA_PATH:
            os.system(f"cp -r {self._DATA_PATH}/* {self.DATA_PATH}")

        self._init_data_dir()

    def log_format(self, log_format: str):
        self.LOG_FORMAT = log_format
        logging.basicConfig(format=self.LOG_FORMAT)

    def _init_data_dir(self):
        logger.info(f"Init data dir: {self.DATA_PATH}")
        # nltk 模型存储路径
        self.NLTK_DATA_PATH = os.path.join(self.DATA_PATH, "nltk_data")
        import nltk

        nltk.data.path = [self.NLTK_DATA_PATH] + nltk.data.path
        # 日志存储路径
        self.LOG_PATH = os.path.join(self.DATA_PATH, "logs")
        if not os.path.exists(self.LOG_PATH):
            os.makedirs(self.LOG_PATH, exist_ok=True)

        # 模型生成内容（图片、视频、音频等）保存位置
        self.MEDIA_PATH = os.path.join(self.DATA_PATH, "media")
        if not os.path.exists(self.MEDIA_PATH):
            os.makedirs(self.MEDIA_PATH, exist_ok=True)
            os.makedirs(os.path.join(self.MEDIA_PATH, "image"), exist_ok=True)
            os.makedirs(os.path.join(self.MEDIA_PATH, "audio"), exist_ok=True)
            os.makedirs(os.path.join(self.MEDIA_PATH, "video"), exist_ok=True)

        # 临时文件目录，主要用于文件对话
        self.BASE_TEMP_DIR = os.path.join(self.DATA_PATH, "temp")
        if not os.path.exists(self.BASE_TEMP_DIR):
            os.makedirs(self.BASE_TEMP_DIR, exist_ok=True)

        logger.info(f"Init data dir: {self.DATA_PATH} success.")

    def get_config(self) -> ConfigBasic:
        config = ConfigBasic()
        config.log_verbose = self.LOG_VERBOSE
        config.CHATCHAT_ROOT = self.CHATCHAT_ROOT
        config.DATA_PATH = self.DATA_PATH
        config.IMG_DIR = self.IMG_DIR
        config.NLTK_DATA_PATH = self.NLTK_DATA_PATH
        config.LOG_FORMAT = self.LOG_FORMAT
        config.LOG_PATH = self.LOG_PATH
        config.MEDIA_PATH = self.MEDIA_PATH
        config.BASE_TEMP_DIR = self.BASE_TEMP_DIR
        return config


class ConfigBasicWorkSpace(
    core_config.ConfigWorkSpace[ConfigBasicFactory, ConfigBasic]
):
    """
    工作空间的配置预设，提供ConfigBasic建造方法产生实例。
    """

    config_factory_cls = ConfigBasicFactory

    def __init__(self):
        super().__init__()

    def _build_config_factory(self, config_json: Any) -> ConfigBasicFactory:
        _config_factory = self.config_factory_cls()

        if config_json.get("log_verbose"):
            _config_factory.log_verbose(config_json.get("log_verbose"))
        if config_json.get("DATA_PATH"):
            _config_factory.data_path(config_json.get("DATA_PATH"))
        if config_json.get("LOG_FORMAT"):
            _config_factory.log_format(config_json.get("LOG_FORMAT"))

        return _config_factory

    @classmethod
    def get_type(cls) -> str:
        return ConfigBasic.class_name()

    def get_config(self) -> ConfigBasic:
        return self._config_factory.get_config()

    def set_log_verbose(self, verbose: bool):
        self._config_factory.log_verbose(verbose)
        self.store_config()

    def set_data_path(self, path: str):
        self._config_factory.data_path(path)
        self.store_config()

    def set_log_format(self, log_format: str):
        self._config_factory.log_format(log_format)
        self.store_config()


config_basic_workspace: ConfigBasicWorkSpace = ConfigBasicWorkSpace()
