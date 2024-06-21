from chatchat.init_server import init_server
import multiprocessing as mp

from chatchat.server.utils import is_port_in_use
from chatchat.startup import run_init_server
import logging
import logging.config

logger = logging.getLogger(__name__)


def test_init_server(logging_conf, providers_file):
    logging.config.dictConfig(logging_conf)
    mp.set_start_method("spawn")
    manager = mp.Manager()
    # 定义全局配置变量,使用 Manager 创建共享字典
    model_platforms_shard = manager.dict()
    model_providers_started = manager.Event()
    process = mp.Process(
        target=run_init_server,
        name=f"Model providers Server",
        kwargs=dict(model_platforms_shard=model_platforms_shard, started_event=model_providers_started),
        daemon=True,
    )

    process.start()
    model_providers_started.wait()  # 等待model_providers启动完成
    # 判断服务是否发布
    assert model_providers_started.is_set(), "Model providers server failed to start."

    # 进行一些初始化后的检查或进一步操作
    # 比如：检查端口是否被占用
    assert is_port_in_use(20000), f"Port {20000} is not in use."

    # 最后停止子进程
    process.terminate()
    process.join()
