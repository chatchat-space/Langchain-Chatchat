from datetime import datetime, timedelta

from chatchat.server.db.models.distributed_lock_model import DistributedLockModel
from chatchat.server.db.session import with_session
from chatchat.server.knowledge_base.migrate import create_tables


@with_session
def add_lock(session, lock_key, owner, lock_expire):
    """
    新增锁记录
    """
    new_lock = DistributedLockModel(lock_key=lock_key, owner=owner, update_lock_time=datetime.now(), lock_status=True)
    new_lock.expire_time = new_lock.update_lock_time + timedelta(seconds=lock_expire)
    session.add(new_lock)
    return new_lock.id


@with_session
def get_lock(session, lock_key):
    """
    根据锁键获取锁记录
    """
    return session.query(DistributedLockModel).filter_by(lock_key=lock_key).first()


@with_session
def update_lock(session, lock_key, lock_status, update_lock_time):
    """
    更新锁的状态和更新时间
    """
    lock = session.query(DistributedLockModel).filter_by(lock_key=lock_key).first()
    lock.lock_status = lock_status
    lock.update_lock_time = update_lock_time
    session.commit()


@with_session
def check_lock_expiry(session, lock_key):
    """
    检查锁是否过期
    """
    lock = session.query(DistributedLockModel).filter_by(lock_key=lock_key).first()
    current_time = datetime.now()
    if lock.expire_time and current_time > lock.expire_time:
        return True
    else:
        return False


create_tables()
add_lock('2', '1',30)
