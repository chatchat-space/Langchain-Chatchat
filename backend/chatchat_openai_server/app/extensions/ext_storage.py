from app.extensions.storage.base_storage import BaseStorage
from app.extensions.storage.local_storage import LocalStorage

storage: BaseStorage

STORAGE_TYPE_KEY = 'storage_type'


def init_storage(config):
    global storage
    storage_type = config.get(STORAGE_TYPE_KEY)
    if storage_type == 'local':
        storage = LocalStorage(config)
    elif storage_type == 'minio-storage':
        from app.extensions.storage.minio_storage import MinioStorage
        storage = MinioStorage(config)
