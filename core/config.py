from hydra import initialize, compose
import warnings
import os

from omegaconf import DictConfig

warnings.filterwarnings('ignore')


class ConfigWarp:
    cfg: DictConfig = None
    env_options_name_list: list = []
    env_options_name_value_list: list = []

    def __init__(self, config_name=None, overrides=None):
        if config_name is not None:
            self.load(config_name, overrides)

    def load(self, config_name='api_config', overrides=None):

        with initialize(config_path="../"):
            self.cfg = compose(config_name=config_name)
        # 环境变量列表
        self.env_options_name_list = list(self.flatten_dict(self.cfg).keys())
        env_overrides = []
        for env_name in self.env_options_name_list:
            if os.getenv(env_name) is not None:
                env_overrides.append(env_name + '=' + os.getenv(env_name))
        self.cfg.merge_with_dotlist(env_overrides)
        if overrides is not None:
            self.cfg.merge_with_dotlist(overrides)
        return self.cfg

    def get_val(self, key: str, default_val=None):
        key_list = key.split('.')
        value = self.cfg
        for k in key_list:
            value = value.get(k)
            if value is None:
                return default_val
        return value

    def flatten_dict(self, data, parent_key='', sep='.'):
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, DictConfig):
                items.extend(self.flatten_dict(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
        return dict(items)
