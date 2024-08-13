from app.depends.storage.base_storage import BaseStorage


storage: BaseStorage

STORAGE_TYPE_KEY = 'storage_type'


def init_storage(config):
    global storage
    storage_type = config.get(STORAGE_TYPE_KEY)
    if storage_type == 'local_storage':
        from app.depends.storage.local_storage import LocalStorage
        storage = LocalStorage(config)
    elif storage_type == 'minio_storage':
        from app.depends.storage.minio_storage import MinioStorage
        storage = MinioStorage(config)
