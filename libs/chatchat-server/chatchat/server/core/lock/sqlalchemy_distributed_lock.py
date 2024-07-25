from typing import overload

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from chatchat.server.core.lock.base import DistributedLock
from chatchat.server.db.repository.distributed_lock_repository import add_lock



class SqlAlchemyDistributedLock(DistributedLock):
    session = None

    def __init__(self, lock_key, session, lock_expire=60, lock_offset=4, delay_queue=None):
        super().__init__(lock_key, lock_expire, lock_offset, delay_queue)
        self.session = session

    @classmethod
    def create(cls, lock_key, session, lock_expire=60, lock_offset=4, delay_queue=None) -> 'SqlAlchemyDistributedLock':
        return SqlAlchemyDistributedLock(lock_key, session, lock_expire, lock_offset, delay_queue)

    def lock(self):
        ...

    def release(self):
        ...

    def renew_lock(self):
        ...


if __name__ == '__main__':

    add_lock('lock_key', 'test')
