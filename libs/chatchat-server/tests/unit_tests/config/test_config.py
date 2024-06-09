from chatchat.configs import ConfigBasicFactory, ConfigBasic
import os


def test_config_factory_def():
    test_config_factory = ConfigBasicFactory()
    config: ConfigBasic = test_config_factory.get_config()
    assert config is not None
    assert config.log_verbose is False
    assert config.CHATCHAT_ROOT is not None
    assert config.DATA_PATH is not None
    assert config.IMG_DIR is not None
    assert config.NLTK_DATA_PATH is not None
    assert config.LOG_FORMAT is not None
    assert config.LOG_PATH is not None
    assert config.MEDIA_PATH is not None

    assert os.path.exists(os.path.join(config.MEDIA_PATH, "image"))
    assert os.path.exists(os.path.join(config.MEDIA_PATH, "audio"))
    assert os.path.exists(os.path.join(config.MEDIA_PATH, "video"))
