# httpx 请求默认超时时间（秒）。如果加载模型或对话较慢，出现超时错误，可以适当加大该值。
from typing import List, TypedDict

HTTPX_DEFAULT_TIMEOUT = 300.0
log_verbose = True


class ImitaterModel(TypedDict):
    name: str
    chat_model_path: str
    chat_model_device: str
    chat_template_path: str
    generation_config_path: str
    agent_type: str


class ImitaterEmbedding(TypedDict):
    name: str
    embed_model_path: str
    embed_model_device: str
    embed_batch_size: int


class ImitaterWorker(TypedDict):
    name: str
    model: ImitaterModel
    embedding: ImitaterEmbedding


class ImitaterCfg:
    def __init__(self, cfg: dict = None):
        if cfg is None:
            raise RuntimeError("ImitaterCfg cfg is None.")
        self._cfg = cfg

    def get_cfg(self):
        return self._cfg

    def get_run_openai_api_cfg(self):
        return self._cfg.get("run_openai_api", {})

    def get_imitate_model_workers_by_name(self, name: str) -> ImitaterWorker:

        imitate_model_workers_cfg = self._cfg.get("imitate_model_workers", None)
        if imitate_model_workers_cfg is None:
            raise RuntimeError("imitate_model_workers_cfg is None.")

        get = lambda model_name: imitate_model_workers_cfg[
            self.get_imitate_model_workers_index_by_name(model_name)
        ].get(model_name, {})
        imitate = get(name)
        # 初始化imitate为ImitaterWorker
        worker_cfg = ImitaterWorker(name=name,
                                    model=ImitaterModel(**imitate.get("model", {})),
                                    embedding=ImitaterEmbedding(**imitate.get("embedding", {}))
                                    )
        return worker_cfg

    def get_imitate_model_workers_names(self) -> List[str]:

        imitate_model_workers_cfg = self._cfg.get("imitate_model_workers", None)
        if imitate_model_workers_cfg is None:
            raise RuntimeError("imitate_model_workers_cfg is None.")
        worker_name_cfg = []
        for cfg in imitate_model_workers_cfg:
            for key, imitate_model_workers in cfg.items():
                worker_name_cfg.append(key)
        return worker_name_cfg

    def get_imitate_model_workers_index_by_name(self, name) -> int:

        imitate_model_workers_cfg = self._cfg.get("imitate_model_workers", None)
        if imitate_model_workers_cfg is None:
            raise RuntimeError("imitate_model_workers_cfg is None.")

        for cfg in imitate_model_workers_cfg:
            for key, imitate_model_workers in cfg.items():
                if key == name:
                    return imitate_model_workers_cfg.index(cfg)
        return -1
