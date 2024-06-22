import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from dataclasses_json import DataClassJsonMixin
from pydantic import BaseModel

logger = logging.getLogger()


class Config(BaseModel):
    @classmethod
    @abstractmethod
    def class_name(cls) -> str:
        """Get class name."""

    def to_dict(self, **kwargs: Any) -> Dict[str, Any]:
        data = self.dict(**kwargs)
        data["class_name"] = self.class_name()
        return data

    def to_json(self, **kwargs: Any) -> str:
        data = self.to_dict(**kwargs)
        return json.dumps(data, indent=4, ensure_ascii=False)


F = TypeVar("F", bound=Config)


@dataclass
class ConfigFactory(Generic[F], DataClassJsonMixin):
    """config for ChatChat"""

    @classmethod
    @abstractmethod
    def get_config(cls) -> F:
        raise NotImplementedError


CF = TypeVar("CF", bound=ConfigFactory)


class ConfigWorkSpace(Generic[CF, F], ABC):
    """
    ConfigWorkSpace是一个配置工作空间的抽象类，提供基础的配置信息存储和读取功能。
    提供ConfigFactory建造方法产生实例。
    该类的实例对象用于存储工作空间的配置信息，如工作空间的路径等
    工作空间的配置信息存储在用户的家目录下的.chatchat/workspace/workspace_config.json文件中。
    注意：不存在则读取默认
    """

    config_factory_cls: Type[CF]
    _config_factory: Optional[CF] = None

    def __init__(self):
        self.workspace = os.path.join(os.path.expanduser("~"), ".chatchat", "workspace")
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace, exist_ok=True)
        self.workspace_config = os.path.join(self.workspace, "workspace_config.json")
        # 初始化工作空间配置，转换成json格式，实现Config的实例化

        _load_config = self._load_config()
        if _load_config is None:
            self._config_factory = self._build_config_factory(config_json={})
            self.store_config()

        else:
            config_type_json = self.get_config_by_type(self.get_type())

            config_json = config_type_json.get("config")
            self._config_factory = self._build_config_factory(config_json)

    @abstractmethod
    def _build_config_factory(self, config_json: Any) -> CF:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_type(cls) -> str:
        raise NotImplementedError

    def get_config(self) -> F:
        return self._config_factory.get_config()

    def clear(self):
        logger.info("Clear workspace config.")
        os.remove(self.workspace_config)

    def _load_config(self):
        try:
            with open(self.workspace_config, "r") as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return None

    @staticmethod
    def _get_store_cfg_index_by_type(store_cfg, store_cfg_type) -> int:
        if store_cfg is None:
            raise RuntimeError("store_cfg is None.")
        for cfg in store_cfg:
            if cfg.get("type") == store_cfg_type:
                return store_cfg.index(cfg)

        return -1

    def get_config_by_type(self, cfg_type) -> Dict[str, Any]:
        store_cfg = self._load_config()
        if store_cfg is None:
            raise RuntimeError("store_cfg is None.")

        get_lambda = lambda store_cfg_type: store_cfg[
            self._get_store_cfg_index_by_type(store_cfg, store_cfg_type)
        ]
        return get_lambda(cfg_type)

    def store_config(self):
        logger.info("Store workspace config.")
        _load_config = self._load_config()
        with open(self.workspace_config, "w") as f:
            config_json = self.get_config().to_dict()

            if _load_config is None:
                _load_config = []
            config_json_index = self._get_store_cfg_index_by_type(
                store_cfg=_load_config, store_cfg_type=self.get_type()
            )
            config_type_json = {"type": self.get_type(), "config": config_json}
            if config_json_index == -1:
                _load_config.append(config_type_json)
            else:
                _load_config[config_json_index] = config_type_json
            f.write(json.dumps(_load_config, indent=4, ensure_ascii=False))
