mq_service = None


def init_mq(config):
    global mq_service
    mq_type = config.get('mq_type', 'local_mq')
    if mq_type == 'local_mq':
        from app.extensions.mq.loacl_mq import LocalMqService
        mq_service = LocalMqService(config)
