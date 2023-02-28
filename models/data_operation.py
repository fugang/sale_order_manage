import datetime
import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy.exc
from sqlalchemy import update

from globals import logger
from .data_model import Base, ItemModel, CustomerModel, \
    SaleContractModel, SalerModel, CANCEL, ContractFile, InvoiceModel
from .data_model import SupplyInfoModel, PurchaseContractModel, IndustryModel
from exceptions import DuplicatePrimaryException
from .data_model import AccountModel, INCOME_MOLD, PAYOUT_MOLD, PAYMENT_MOLD
from .data_model import INVOICE_ISSUE, INVOICE_RECV

engine = create_engine("sqlite:///zk-sj_plat.sqlite3", echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
session = Session()


item_map = {"ems_cost": "EMS", "emi_cost": "EMI",
            "vol_trans_cost": "隔离变压器", "shield_cost": "屏蔽房",
            "computer_cost": "电脑", "env_desk_cost": "环境和桌子",
            "other_cost": "其他"
            }


def plug_common_data(data):
    now = datetime.datetime.now()
    data["created_at"] = now
    date = data.get("date")
    if date:
        data["year"] = date.year
        data["month"] = date.month


def query_industry_by_name(name):
    industry = session.query(IndustryModel).filter(
        IndustryModel.name == name).first()
    return industry


def init_item():
    for item in item_map.values():
        if not session.query(ItemModel).filter(ItemModel.name == item).first():
            data = ItemModel(name=item, specification="")
            session.add(data)
    for name in ["灯具电源", "灯具IC", "开关电源", "家用电源",
                 "汽车电子", "电动工具", "高压绝缘子套管等",
                 "大型设备 电焊机 变频器", "医疗器械", "消防",
                 "高压设备", "环保电力", "第三方测试公司",
                 "经销商"]:
        if not query_industry_by_name(name):
            data = IndustryModel(name=name)
            session.add(data)

    session.commit()


def save_item(data):
    data = ItemModel(**data)
    try:
        session.add(data)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise DuplicatePrimaryException("重复的物品信息")
    except Exception as exc:
        logger.error("save item error. %s", exc)
        raise Exception("保存错误")


def list_customer_company():
    customers = session.query(CustomerModel).all()
    company_list = [customer.company for customer in customers]
    return company_list


def get_customer_detail():
    customers = session.query(CustomerModel).all()
    return customers


def save_sale_contract(sale_contract):
    plug_common_data(sale_contract)
    sale_model = SaleContractModel(**sale_contract)
    session.add(sale_model)
    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise DuplicatePrimaryException("重复的记录")
    except Exception as exc:
        session.rollback()
        logger.error("save sale and purchase data error. %s", exc)
        raise Exception("保存错误")
    return sale_model


def upsert_customer(customer_data):
    id = customer_data.get("id")
    if id:
        stmt = update(CustomerModel).where(
            CustomerModel.id == id).values(**customer_data)
        session.execute(stmt)
        customer = CustomerModel(**customer_data)
    else:
        customer = CustomerModel(**customer_data)
        session.add(customer)
    session.commit()
    return customer


def upset_industry(name):
    industry = query_industry_by_name(name)
    if not industry:
        industry = IndustryModel(name=name)
        session.add(industry)
        session.commit()


def list_industry():
    name_list = []
    industry_list = session.query(IndustryModel).all()
    for industry in industry_list:
        name_list.append(industry.name)
    return name_list


def upsert_saler(saler_data):
    name = saler_data["name"]
    saler = session.query(SalerModel).filter(SalerModel.name==name).first()
    if not saler:
        saler = SalerModel(**saler_data)
        session.add(saler)
        session.commit()


def update_sale_contract(id, contract_data):
    stmt = update(SaleContractModel).where(
        SaleContractModel.id==id).values(**contract_data)
    session.execute(stmt)
    session.commit()


def cancel_sale_contract(id):
    stmt = update(SaleContractModel).where(SaleContractModel.id==id).values(state=CANCEL)
    session.execute(stmt)
    session.commit()


def query_sale_contract(saler=None, year=None, month_list=None, product=None):
    query = session.query(SaleContractModel)
    if saler:
        query = query.filter(SaleContractModel.saler.contains(saler))
    if year:
        query = query.filter(SaleContractModel.year==year)
    if month_list:
        query = query.filter(SaleContractModel.month.in_(month_list))
    if product:
        purchase_list = query_purchase_by_product(product)
        sale_no_list = [p.sale_no for p in purchase_list]
        query = query.filter(SaleContractModel.sale_no.in_(sale_no_list))
    data = query.all()
    return data


def query_sale_contract_by_company(company):
    contract_list = session.query(SaleContractModel).filter(
        SaleContractModel.company.like(f"%{company}%")).all()
    return contract_list


def query_purchase_by_product(product_type):
    contract_list = session.query(PurchaseContractModel).filter(
        PurchaseContractModel.product_type == product_type).all()
    return contract_list


def query_main_cost_by_sale_id(sale_id):
    purchase_list = query_purchase_contract_by_sale(sale_id)
    main_cost = 0
    for purchase in purchase_list:
        main_cost += purchase.amount
    return main_cost


def query_purchase_contract_by_company(company):
    contract_list = session.query(PurchaseContractModel).filter(
        PurchaseContractModel.supply.like(f"%{company}%")).all()
    return contract_list


def query_purchase_by_sale_and_supply(sale_id, supply):
    purchase = session.query(PurchaseContractModel).filter(
        PurchaseContractModel.sale_id == sale_id).filter(
        PurchaseContractModel.supply == supply).first()
    return purchase


def query_purchase_item_by_sale_no(sale_no):
    purchase_list = session.query(PurchaseContractModel).filter(
        PurchaseContractModel.sale_no == sale_no).all()
    item_list = []
    for purchase in purchase_list:
        item_list.append(purchase.item)
    return item_list


def query_unpaid_purchase_item_by_sale_no(sale_id):
    item_list = []
    purchase_list = query_purchase_contract_by_sale(sale_id)
    for purchase in purchase_list:
        purchase_id = purchase.id
        account_list = query_payout_account_by_purchase_id(purchase_id)
        total_paid = 0
        for account in account_list:
            total_paid += account.amount
        if total_paid < purchase.amount:
            item_list.append(purchase.item)
    return item_list


def get_sale_contract_by_id(id):
    data = session.query(SaleContractModel).filter(
        SaleContractModel.id == id).first()
    return data


def get_sale_contract_by_contract_no(sale_no):
    data = session.query(SaleContractModel).filter(
        SaleContractModel.sale_no == sale_no).first()
    return data


def get_purchase_contract_by_id(purchase_id):
    data = session.query(PurchaseContractModel).filter(
        PurchaseContractModel.id == purchase_id).first()
    return data


def list_supply():
    supply_list = session.query(SupplyInfoModel).all()
    company_list = [supply.company for supply in supply_list]
    return company_list


def list_product_type():
    product_list = []
    purchase_list = session.query(PurchaseContractModel.product_type).distinct().all()
    for purchase in purchase_list:
        product_list.append(purchase.product_type)
    return product_list


def list_supply_by_item(item):
    supply_list = session.query(SupplyInfoModel).filter(
        SupplyInfoModel.items.like(f"%{item}%"))
    company_list = [supply.company for supply in supply_list]
    return company_list


def get_supply_detail():
    supply = session.query(SupplyInfoModel).all()
    return supply


def get_supply_by_id(id):
    supply = session.query(SupplyInfoModel).filter(SupplyInfoModel.id==id).first()
    return supply


def get_supply_by_company(company):
    supply = session.query(SupplyInfoModel).filter(
        SupplyInfoModel.company==company).first()
    return supply


def list_item():
    item_list = session.query(ItemModel).all()
    name_list = [item.name for item in item_list]
    return name_list


def get_item_detail():
    item_list = session.query(ItemModel).all()
    return item_list


def get_item_by_id(id):
    item = session.query(ItemModel).filter(ItemModel.id==id).first()
    return item


def update_item(id, data):
    stmt = update(ItemModel).where(ItemModel.id == id).values(**data)
    session.execute(stmt)
    session.commit()

def list_saler():
    salers = session.query(SalerModel).all()
    names = [saler.name for saler in salers]
    return names


def get_saler_by_id(id):
    saler = session.query(SalerModel).filter(SalerModel.id==id).first()
    return saler


def update_saler(id, data):
    stmt = update(SalerModel).where(SalerModel.id == id).values(**data)
    session.execute(stmt)
    session.commit()


def get_saler_detail():
    salers = session.query(SalerModel).all()
    return salers


def save_customer(customer_data):
    data = CustomerModel(**customer_data)
    session.add(data)
    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise DuplicatePrimaryException("重复客户信息")
    except Exception as exc:
        logger.error("save customer error. %s", exc)
        session.rollback()
        raise Exception("保存错误")


def update_customer(id, data):
    try:
        stmt = update(CustomerModel).where(CustomerModel.id == id).values(**data)
        session.execute(stmt)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise DuplicatePrimaryException("重复的公司名称")
    except Exception as exc:
        logger.error("update customer error. %s", exc)
        raise Exception("更新错误")


def get_customer_by_id(id):
    customer = session.query(CustomerModel).filter(CustomerModel.id==id).first()
    return customer


def query_customer_by_company(company):
    customer = session.query(CustomerModel).filter(
        CustomerModel.company==company).first()
    return customer


def save_saler(saler_data):
    data = SalerModel(**saler_data)
    try:
        session.add(data)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise DuplicatePrimaryException("重复销售员信息")
    except Exception as exc:
        logger.error("save saler error. %s", exc)
        session.rollback()
        raise Exception("保存错误")


def save_supply(data):
    data = SupplyInfoModel(**data)
    try:
        session.add(data)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise DuplicatePrimaryException("重复供应商信息")
    except Exception as exc:
        logger.error("save supply error. %s", exc)
        session.rollback()
        raise Exception("保存错误")


def update_supply(id, data):
    stmt = update(SupplyInfoModel).where(SupplyInfoModel.id == id).values(**data)
    session.execute(stmt)
    session.commit()


def upsert_supply_data(supply_data):
    company = supply_data.get("company")
    supply = get_supply_by_company(company)
    if supply:
        if supply.items:
            origin_item_list = supply.items.split(",")
        else:
            origin_item_list = []
        items = supply_data["items"]
        item_list = items.split(",")
        for item in item_list:
            if item not in origin_item_list:
                origin_item_list.append(item)
        supply_data["items"] = ",".join(origin_item_list)
        update_supply(supply.id, supply_data)
    else:
        save_supply(supply_data)


def save_purchase_data(data):
    plug_common_data(data)
    model = PurchaseContractModel(**data)
    try:
        session.add(model)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        logger.error("save purchase data duplicate record")
        raise DuplicatePrimaryException("重复的采购信息")
    except Exception as exc:
        logger.error("save purchase data error. %s", exc)
        logger.exception(exc)
        traceback.print_exc()
        session.rollback()
        raise Exception("保存错误")
    return model


def update_purchase_data(id, data):
    stmt = update(PurchaseContractModel).where(
        PurchaseContractModel.id == id).values(**data)
    session.execute(stmt)
    session.commit()


def query_purchase_contract_by_sale(sale_id):
    purchase_list = session.query(PurchaseContractModel).filter(
        PurchaseContractModel.sale_id == sale_id).all()
    return purchase_list


def query_purchase_by_item(sale_id, item):
    purchase = session.query(PurchaseContractModel).filter(
        PurchaseContractModel.sale_id == sale_id).filter(
        PurchaseContractModel.item == item).first()
    return purchase


def get_purchase_contract(supply, year, contract_no, month_list, product):
    query = session.query(PurchaseContractModel)
    if supply:
        query = query.filter(PurchaseContractModel.supply == supply)
    if year:
        query = query.filter(PurchaseContractModel.year == year)
    if contract_no:
        query = query.filter(
            PurchaseContractModel.sale_contract_no.like(f'%{contract_no}%'))
    if month_list:
        query = query.filter(PurchaseContractModel.month.in_(month_list))
    if product:
        query = query.filter(PurchaseContractModel.product_type==product)
    data = query.all()
    return data


def get_received_amount_by_sale_contract(sale_id):
    data_list = session.query(AccountModel).filter(
        AccountModel.sale_id == sale_id).filter(
        AccountModel.mold == INCOME_MOLD).all()
    received = 0
    for data in data_list:
        received += data.amount
    return received


def query_income_account_by_sale_no(sale_id):
    account_list = session.query(AccountModel).filter(
        AccountModel.sale_id == sale_id).filter(
        AccountModel.mold == INCOME_MOLD).all()
    return account_list


def query_payout_account_by_purchase_id(purchase_id):
    account_list = session.query(AccountModel).filter(
        AccountModel.purchase_id==purchase_id).all()
    return account_list


def query_payout_account_by_sale_no(sale_id):
    account_list = session.query(AccountModel).filter(
        AccountModel.sale_id == sale_id).filter(
        AccountModel.mold == PAYOUT_MOLD).all()
    return account_list


def get_paid_amount_by_purchase_contract(purchase_id):
    data_list = session.query(AccountModel).filter(
        AccountModel.purchase_id==purchase_id).all()
    paid = 0
    for data in data_list:
        paid += data.amount
    return paid


def get_paid_amount_by_sale_no(sale_id):
    data_list = session.query(AccountModel).filter(
        AccountModel.sale_id==sale_id).filter(AccountModel.mold==PAYOUT_MOLD).all()
    paid = 0
    for data in data_list:
        paid += data.amount
    return paid


def get_payable_amount_by_sale_no(sale_id):
    data_list = session.query(PurchaseContractModel).filter(
        PurchaseContractModel.sale_id == sale_id).all()
    total_payable = 0
    for data in data_list:
        total_payable += data.amount
    return total_payable


def get_account_by_id(id):
    account = session.query(AccountModel).filter(AccountModel.id==id).first()
    return account


def get_account_detail(mold, company, year, month_list):
    query = session.query(AccountModel)
    if mold:
        query = query.filter(AccountModel.mold == mold)
    if company:
        sale_contract_list = []
        sale_list = query_sale_contract_by_company(company)
        for contract in sale_list:
            sale_contract_list.append(contract.contract_no)
        if sale_contract_list:
            query = query.filter(AccountModel.sale_contract.in_(sale_contract_list))
        purchase_contract_list = []
        purchase_list = query_purchase_contract_by_company(company)
        for contract in purchase_list:
            purchase_contract_list.append(contract.contract_no)
        if purchase_contract_list:
            query = query.filter(
                AccountModel.purchase_contract.in_(purchase_contract_list))
    if year:
        query = query.filter(AccountModel.year == year)
    if month_list:
        query = query.filter(AccountModel.month.in_(month_list))
    account_list = query.all()
    return account_list


def save_income_data(data):
    plug_common_data(data)
    data["mold"] = INCOME_MOLD
    data = AccountModel(**data)
    try:
        session.add(data)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise DuplicatePrimaryException("重复记录")
    except Exception as exc:
        logger.error("save income data error. %s", exc)
        session.rollback()
        raise Exception(exc)


def save_issue_invoice(data):
    plug_common_data(data)
    data["mold"] = INVOICE_ISSUE
    data = InvoiceModel(**data)
    try:
        session.add(data)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise DuplicatePrimaryException("重复记录")
    except Exception as exc:
        logger.error("save invoice data error. %s", exc)
        session.rollback()
        raise Exception(exc)


def save_recv_invoice(data):
    plug_common_data(data)
    data["mold"] = INVOICE_RECV
    data = InvoiceModel(**data)
    try:
        session.add(data)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise DuplicatePrimaryException("重复记录")
    except Exception as exc:
        logger.error("save invoice data error. %s", exc)
        session.rollback()
        raise Exception(exc)


def query_issue_invoice(sale_id):
    invoice_list = session.query(InvoiceModel).filter(
        InvoiceModel.sale_id == sale_id).filter(
        InvoiceModel.mold == INVOICE_ISSUE).all()
    return invoice_list


def query_recv_invoice(sale_id):
    invoice_list = session.query(InvoiceModel).filter(
        InvoiceModel.sale_id == sale_id).filter(
        InvoiceModel.mold == INVOICE_RECV).all()
    return invoice_list

def query_issue_invoice_amount(sale_id):
    total = 0
    for invoice in query_issue_invoice(sale_id):
        total += invoice.amount
    return total


def query_recv_invoice_by_purchase(purchase_id):
    invoice_list = session.query(InvoiceModel).filter(
        InvoiceModel.purchase_id == purchase_id).filter(
        InvoiceModel.mold == INVOICE_RECV).all()
    return invoice_list


def query_recv_invoice_by_sale(sale_id):
    invoice_list = session.query(InvoiceModel).filter(
        InvoiceModel.sale_id == sale_id).filter(
        InvoiceModel.mold == INVOICE_RECV).all()
    return invoice_list


def query_recv_invoice_amount_by_purchase(purchase_id):
    invoice_list = query_recv_invoice_by_purchase(purchase_id)
    total = 0
    for invoice in invoice_list:
        total += invoice.amount
    return total


def query_recv_invoice_amount_by_sale(sale_id):
    invoice_list = query_recv_invoice_by_sale(sale_id)
    total = 0
    for invoice in invoice_list:
        total += invoice.amount
    return total


def save_payout_data(data):
    data["created_at"] = datetime.datetime.now()
    data["mold"] = PAYOUT_MOLD
    data["year"] = data["date"].year
    data["month"] = data["date"].month
    data = AccountModel(**data)
    try:
        session.add(data)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise DuplicatePrimaryException("重复记录")
    except Exception as exc:
        logger.error("save payout data error. %s", exc)
        session.rollback()
        raise Exception(exc)


def save_payment_data(data):
    data["created_at"] = datetime.datetime.now()
    data["mold"] = PAYMENT_MOLD
    data["year"] = data["date"].year
    data["month"] = data["date"].month
    data = AccountModel(**data)
    session.add(data)
    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise DuplicatePrimaryException("重复记录")
    except Exception as exc:
        logger.error("save payout data error. %s", exc)
        session.rollback()
        raise Exception(exc)


def update_payout_data(id, data):
    stmt = update(AccountModel).where(AccountModel.id == id).values(**data)
    session.execute(stmt)
    session.commit()


def update_income_data(id, data):
    stmt = update(AccountModel).where(AccountModel.id == id).values(**data)
    session.execute(stmt)
    session.commit()


def save_file_data(data):
    md5sum = data["md5sum"]
    model = session.query(ContractFile).filter(ContractFile.md5sum == md5sum).first()
    if model:
        return model
    else:
        model = ContractFile(**data)
        session.add(model)
        try:
            session.commit()
        except Exception as exc:
            logger.error("save file data error. %s", exc)
            raise Exception("保存失败")
        return model


def query_file_data_by_id(lob_id):
    data = session.query(ContractFile).filter(ContractFile.id == lob_id).first()
    return data


init_item()
