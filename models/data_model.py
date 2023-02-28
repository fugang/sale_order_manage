from sqlalchemy import create_engine, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Date, \
    Integer, Float, DateTime, Boolean, BLOB


Base = declarative_base()
ACTIVE = 1
CANCEL = 2

INCOME_MOLD = 1
PAYOUT_MOLD = 2
PAYMENT_MOLD = 3

INVOICE_ISSUE = 1
INVOICE_RECV = 2


class SaleContractModel(Base):
    __tablename__ = "sale_contract"
    id = Column(Integer, primary_key=True)
    saler = Column(String)
    assistant = Column(String)
    date = Column(Date)
    year = Column(Integer)
    month = Column(Integer)
    customer_id = Column(String)
    sale_no = Column(String, index=True)
    amount = Column(Float)
    tax_rate = Column(Integer)
    discount = Column(Float)
    marks = Column(String)
    created_at = Column(DateTime)
    state = Column(Integer, default=ACTIVE)
    lob_id = Column(Integer)
    file_path = Column(String)

    UniqueConstraint(sale_no)
    UniqueConstraint(customer_id, date)


class PurchaseContractModel(Base):
    __tablename__ = "purchase_contract"
    id = Column(Integer, primary_key=True)
    purchase_no = Column(String, index=True)
    sale_id = Column(Integer, index=True)
    supply = Column(String)
    item = Column(String, index=True)
    product_type = Column(String, index=True)
    count = Column(String)
    date = Column(Date)
    year = Column(Integer)
    month = Column(Integer)
    amount = Column(Float)
    mark = Column(String)
    lob_id = Column(Integer)
    file_path = Column(String)
    created_at = Column(DateTime)
    UniqueConstraint(sale_id, item)


class SupplyInfoModel(Base):
    __tablename__ = "supply_info"
    id = Column(Integer, primary_key=True)
    company = Column(String, index=True)
    items = Column(String, index=True)
    address = Column(String)
    linkman = Column(String)
    phone = Column(String)
    UniqueConstraint(company)


class ItemModel(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    specification = Column(String)
    UniqueConstraint(name)


class CustomerModel(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True)
    company = Column(String, index=True)
    industry = Column(String)
    direction = Column(String)
    address = Column(String)
    linkman = Column(String)
    phone = Column(String)
    UniqueConstraint(company)


class SalerModel(Base):
    __tablename__ = "saler"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    phone = Column(String)
    UniqueConstraint(name)


class AccountModel(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    mold = Column(Integer, index=True)
    sale_id = Column(Integer, index=True)
    purchase_id = Column(Integer, index=True)
    amount = Column(Float)
    date = Column(Date)
    year = Column(Integer)
    month = Column(Integer)
    bank_serial = Column(String)
    pay_account = Column(String)
    pay_description = Column(String)
    created_at = Column(DateTime)


class ContractFile(Base):
    __tablename__ = "contract_file"
    id = Column(Integer, primary_key=True)
    md5sum = Column(String, index=True)
    lob = Column(BLOB)
    UniqueConstraint(md5sum)


class InvoiceModel(Base):
    __tablename__ = "invoice"
    id = Column(Integer, primary_key=True)
    company = Column(Integer)
    amount = Column(Integer)
    mold = Column(Integer)
    sale_id = Column(Integer)
    purchase_id = Column(Integer)
    date = Column(Date)
    year = Column(Integer)
    month = Column(Integer)
    created_at = Column(DateTime)


class IndustryModel(Base):
    __tablename__ = "industry"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
