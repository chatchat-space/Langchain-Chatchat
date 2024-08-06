from app.extensions.storage.base_storage import BaseStorage
from app.extensions.storage.local_storage import LocalStorage

storage: BaseStorage


def init_storage(config):
    global storage
    storage = LocalStorage(config)
