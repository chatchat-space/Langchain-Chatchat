from pathlib import Path

from chatchat.configs import ConfigBasicFactory, ConfigBasic, ConfigBasicWorkSpace
import os


def test_config_basic_workspace():
    config_basic_workspace: ConfigBasicWorkSpace = ConfigBasicWorkSpace()
    assert config_basic_workspace.get_config() is not None
    base_root = os.path.join(Path(__file__).absolute().parent, "chatchat")
    config_basic_workspace.set_data_path(os.path.join(base_root, "data"))
    config_basic_workspace.set_log_verbose(True)
    config_basic_workspace.set_log_format(" %(message)s")

    config: ConfigBasic = config_basic_workspace.get_config()
    assert config.log_verbose is True
    assert config.DATA_PATH == os.path.join(base_root, "data")
    assert config.IMG_DIR is not None
    assert config.NLTK_DATA_PATH == os.path.join(base_root, "data", "nltk_data")
    assert config.LOG_FORMAT == " %(message)s"
    assert config.LOG_PATH == os.path.join(base_root, "data", "logs")
    assert config.MEDIA_PATH == os.path.join(base_root, "data", "media")

    assert os.path.exists(os.path.join(config.MEDIA_PATH, "image"))
    assert os.path.exists(os.path.join(config.MEDIA_PATH, "audio"))
    assert os.path.exists(os.path.join(config.MEDIA_PATH, "video"))
    config_basic_workspace.clear()


def test_workspace_default():
    from chatchat.configs import (log_verbose, DATA_PATH, IMG_DIR, NLTK_DATA_PATH, LOG_FORMAT, LOG_PATH, MEDIA_PATH)
    assert log_verbose is False
    assert DATA_PATH is not None
    assert IMG_DIR is not None
    assert NLTK_DATA_PATH is not None
    assert LOG_FORMAT is not None
    assert LOG_PATH is not None
    assert MEDIA_PATH is not None
