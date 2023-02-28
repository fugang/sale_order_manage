from sqlalchemy import *
from migrate import *

from sqlalchemy import Table, Column, Integer, String, MetaData, Date

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    account = Table('sale_contract', meta, autoload=True)
    emailc = Column('email', String(128))
    emailc.create(account)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    account = Table('account', meta, autoload=True)
    account.c.email.drop()
