import datetime

from PySide6.QtCore import QDate

from globals import gw, config, logger
from models.data_operation import get_received_amount_by_sale_contract, \
    save_income_data, get_account_detail, get_account_by_id, \
    get_sale_contract_by_contract_no, \
    get_paid_amount_by_purchase_contract, save_payout_data, \
    get_purchase_contract_by_id, query_purchase_contract_by_sale, \
    query_income_account_by_sale_no, get_customer_by_id, \
    get_paid_amount_by_sale_no, get_payable_amount_by_sale_no, \
    query_unpaid_purchase_item_by_sale_no, query_payout_account_by_sale_no, \
    query_purchase_by_item, save_payment_data, get_sale_contract_by_id, \
    query_issue_invoice, save_issue_invoice, query_main_cost_by_sale_id, \
    query_recv_invoice_amount_by_sale, query_recv_invoice, \
    query_purchase_by_sale_and_supply, save_recv_invoice
from utils import check_float, reverse_dict, object_as_dict, \
    show_success_message, show_failed_message, show_window, \
    amount_str_to_float, set_date
from exceptions import ValueTypeErrException
from models.table_model import TableModel, StaticTableModel
from models.data_model import INCOME_MOLD, PAYOUT_MOLD, PAYMENT_MOLD
from .common_handles import fresh_add_sale_contract_by_contract_no

mold_value_map = {INCOME_MOLD: "入账", PAYOUT_MOLD: "出账", PAYMENT_MOLD: "支出"}
mole_type_map = reverse_dict(mold_value_map)


def get_current_main_window_row_dict():
    window = gw["main_window"]
    table_view = window.saleContractTableView
    index = table_view.currentIndex()
    row = index.row()
    if row == -1:
        return -1
    else:
        data = table_view.model().get_row_dict(row)
        return data

def get_current_purchase_row_dict():
    window = gw["view_purchase_window"]
    table_view = window.purchaseTableView
    index = table_view.currentIndex()
    row = index.row()
    if row == -1:
        return -1
    else:
        data = table_view.model().get_row_dict(row)
        return data

def render_add_income_window(data):
    window = gw["add_income_window"]
    if data and "id" in data:
        window.idLabel.show()
        window.idLineEdit.show()
        window.idLineEdit.setText(str(data["id"]))
    else:
        window.idLabel.hide()
        window.idLineEdit.hide()
        window.idLineEdit.setText("")
    window.saleContractLineEdit.setText(data["sale_no"])
    window.companyLineEdit.setText(data["company"])
    window.outstandingLineEdit.setText(f'{data["outstanding"]:,}')
    window.receivableLineEdit.setText(f'{data["receivable"]:,}')
    window.receivedLineEdit.setText(f'{data["received"]:,}')
    if data and "amount" in data:
        window.cashLineEdit.setText(f'{data["amount"]:,}')
    else:
        window.cashLineEdit.setText("")
    if data and "date" in data:
        date = data["date"]
        window.dateEdit.setDate(QDate(date.year, date.month, date.day))
    else:
        today = datetime.date.today()
        window.dateEdit.setDate(QDate(today.year, today.month, today.day))
    if data and "bank_serial" in data:
        window.bankSerialLineEdit.setText(data["bank_serial"])
    else:
        window.bankSerialLineEdit.setText("")


def render_payout_window(data):
    window = gw["add_payout_window"]
    if data and "id" in data:
        window.idLabel.show()
        window.idLineEdit.setText(str(data["id"]))
        window.idLineEdit.show()
    else:
        window.idLabel.hide()
        window.idLineEdit.setText("")
        window.idLineEdit.hide()
    if data and "contract_no" in data:
        window.purchaseContractLineEdit.setText(data["contract_no"])
    else:
        window.purchaseContractLineEdit.setText("")
    if data and "company" in data:
        window.companyLineEdit.setText(data["company"])
    else:
        window.companyLineEdit.setText("")
    if data and "item" in data:
        window.itemLineEdit.setText(data["item"])
    else:
        window.itemLineEdit.setText("")
    if data and "payable" in data:
        window.payableLineEdit.setText(f'{data["payable"]:,}')
    else:
        window.payableLineEdit.setText("")
    if data and "paid" in data:
        window.paidLineEdit.setText(f'{data["paid"]:,}')
    else:
        window.paidLineEdit.setText("")
    if data and "amount" in data:
        window.cashLineEdit.setText(f'{data["amount"]:,}')
    else:
        window.cashLineEdit.setText("")
    if data and "unpaid" in data:
        window.unpaidLineEdit.setText(f'{data["unpaid"]:,}')
    if data and "date" in data:
        date = data["date"]
        window.dateEdit.setDate(QDate(date.year, date.month, date.day))
    else:
        now = datetime.datetime.now()
        window.dateEdit.setDate(QDate(now.year, now.month, now.day))
    if data and "bank_serial" in data:
        window.bankSerialLineEdit.setText(data["bank_serial"])
    else:
        window.bankSerialLineEdit.setText("")


def add_income_handle():
    pass


def get_current_purchase_data():
    window = gw["view_purchase_window"]
    table_view = window.purchaseTableView
    index = table_view.currentIndex()
    row = index.row()
    if row == -1:
        return -1
    else:
        data = table_view.model().get_row_dict(row)
        return data

def filter_payment_data():
    window = gw["view_cash_window"]
    date = window.payDateEdit.date().toPython()
    amount = window.payAmountlineEdit.text()
    amount = check_float(amount)
    if not amount:
        raise ValueTypeErrException("支出金额错误")
    description = window.payDespLineEdit.text()
    if not description:
        raise ValueTypeErrException("支出项错误")
    return {"pay_description": description,
            "date": date, "amount": amount,
            }

def save_payment_handle():
    window = gw["view_cash_window"]
    status_bar = window.viewCashStatusbar
    try:
        payment_data = filter_payment_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    try:
        save_payment_data(payment_data)
    except Exception as exc:
        show_failed_message(status_bar, f"新建支出项错误. {exc}")
        return
    show_success_message(status_bar, "新建支出项成功")
    render_cash_window_data()

def add_payout_handle():
    pass


def filter_income_data():
    window = gw["add_income_window"]
    amount = window.cashLineEdit.text()
    amount = check_float(amount)
    if amount is False:
        raise ValueTypeErrException("收款金额错误")
    sale_contract_no = window.saleContractLineEdit.text()
    if not sale_contract_no:
        raise ValueTypeErrException("没有合同编号")
    receivable = window.receivableLineEdit.text()
    receivable = check_float(receivable)
    if receivable is False:
        raise ValueTypeErrException("应收账款错误")
    received = window.receivedLineEdit.text()
    received = check_float(received)
    if received is False:
        raise ValueTypeErrException("已收款错误")
    if receivable > 0:
        if amount + received > receivable:
            raise ValueTypeErrException("收款金额超出应收账款")
    date = window.dateEdit.date()
    date = date.toPython()
    bank_serial = window.bankSerialLineEdit.text()
    data = {"amount": amount, "date": date,
            "bank_serial": bank_serial, "sale_contract": sale_contract_no,
            }
    return data

def filter_payout_data():
    window = gw["add_payout_window"]
    purchase_contract = window.purchaseContractLineEdit.text()
    payable_amount = window.payableLineEdit.text()
    payable_amount = check_float(payable_amount)
    if payable_amount is False:
        raise ValueTypeErrException("应付账款错误")
    paid_amount = window.paidLineEdit.text()
    paid_amount = check_float(paid_amount)
    if paid_amount is False:
        raise ValueTypeErrException("已付款错误")
    amount = window.cashLineEdit.text()
    amount = check_float(amount)
    if amount is False:
        raise ValueTypeErrException("付款金额错误")
    date = window.dateEdit.date()
    date = date.toPython()
    if payable_amount > 0:
        if amount + paid_amount > payable_amount:
            raise ValueTypeErrException("付款金额超过应付账款")
    bank_serial = window.bankSerialLineEdit.text()
    data = {"amount": amount, "date": date, "year": date.year,
            "bank_serial": bank_serial,
            "purchase_contract": purchase_contract,
            }
    return data


def package_account_data(account):
    account_data = object_as_dict(account)
    account_data["mold_value"] = mold_value_map[account_data["mold"]]
    if account.mold == INCOME_MOLD:
        sale_contract = get_sale_contract_by_id(account.sale_id)
        if sale_contract:
            customer_id = sale_contract.customer_id
            customer = get_customer_by_id(customer_id)
            if customer:
                account_data["company"] = customer.company
        account_data["item"] = ""
    elif account.mold == PAYOUT_MOLD:
        purchase_contract = get_purchase_contract_by_id(
            account.purchase_id)
        account_data["company"] = purchase_contract.supply
        account_data["item"] = purchase_contract.item
    elif account.mold == PAYMENT_MOLD:
        account_data["item"] = account.pay_description
    return account_data


def get_table_data(mold, company, year, month_list):
    window = gw["view_cash_window"]
    if mold:
        mold = mole_type_map[mold]
    account_list = get_account_detail(mold, company, year, month_list)
    table_data = []
    sum_income = 0
    sum_outcome = 0
    for account in account_list:
        data = []
        account_data = package_account_data(account)
        if account.mold == INCOME_MOLD:
            sum_income += account.amount
        elif account.mold == PAYOUT_MOLD:
            sum_outcome += account.amount
        elif account.mold == PAYMENT_MOLD:
            sum_outcome += account.amount
        for key in config["account_view"].keys():
            data.append(account_data.get(key))
        table_data.append(data)
    window.sumIncomelineEdit.setText(f"{sum_income:,}")
    window.sumOutComelineEdit.setText(f"{sum_outcome:,}")
    return table_data


def render_cash_table_data():
    window = gw["view_cash_window"]
    mold = window.moldCombox.currentText()
    company = window.companylineEdit.text()
    year = window.yearCombox.currentText()
    month_list = window.monthCombox.currentData()
    month_list = [int(m[:-1]) for m in month_list]
    table_data = get_table_data(mold, company, year, month_list)
    headers = list(config["account_view"].values())
    params = list(config["account_view"].keys())
    table_model = TableModel(table_data, headers, params)
    window.viewCashtableView.setModel(table_model)
    window.viewCashtableView.resizeColumnsToContents()


def update_combox():
    window = gw["view_cash_window"]
    window.monthCombox.clear()
    for i in range(1, 13):
        window.monthCombox.addItem(f"{i}月")
    window.monthCombox.setCurrentText("")


def render_cash_window_data():
    window = gw["view_cash_window"]
    update_combox()
    window.moldCombox.setCurrentText("")
    window.companylineEdit.setText("")
    window.payDespLineEdit.setText("")
    window.payAmountlineEdit.setText("")
    now = datetime.datetime.now()
    window.payDateEdit.setDate(QDate(now.year, now.month, now.day))
    render_cash_table_data()

def view_cash_handle():
    window = gw["view_cash_window"]
    status_bar = window.viewCashStatusbar
    render_cash_window_data()
    show_window(window, status_bar)

def fresh_cash_table_handle():
    window = gw["view_cash_window"]
    render_cash_table_data()
    window.show()


def view_income_handle():
    window = gw["view_cash_window"]
    contract_data = get_current_main_window_row_dict()
    company = contract_data["company"]
    window.companylineEdit.setText(company)
    window.moldCombox.setCurrentText("入账")
    render_cash_table_data()
    window.show()

def view_payout_handle():
    window = gw["view_cash_window"]
    purchase_data = get_current_purchase_row_dict()
    company = purchase_data["supply"]
    window.companylineEdit.setText(company)
    window.moldCombox.setCurrentText("出账")
    render_cash_table_data()
    window.show()

def get_cash_window_current_id():
    window = gw["view_cash_window"]
    table_view = window.viewCashtableView
    index = table_view.currentIndex()
    row = index.row()
    if row == -1:
        return -1
    else:
        id = table_view.model().get_row_id(row)
        return id


def modify_cash_handle():
    id = get_cash_window_current_id()
    account = get_account_by_id(id)
    if account.mold == INCOME_MOLD:
        window = gw["add_income_window"]
        sale_id = account.sale_id
        received = get_received_amount_by_sale_contract(sale_id)
        sale_contract = get_sale_contract_by_id(sale_id)
        if sale_contract:
            sale_no = sale_contract.sale_no
            customer_id = sale_contract.customer_id
            customer = get_customer_by_id(customer_id)
            if customer:
                company = customer.company
            else:
                company = ""
            receivable = sale_contract.amount
            company = sale_contract.company
            date = account.date
            outstanding = receivable - received
        else:
            receivable = 0
            company = ""
            date = None
            outstanding = 0
        amount = account.amount
        data = {"sale_contract": sale_no, "receivable": receivable,
                "received": received, "company": company,
                "id": account.id, "amount": amount,
                "date": date, "outstanding": outstanding,
                }
        render_add_income_window(data)
        window.show()
    elif account.mold == PAYOUT_MOLD:
        window = gw["add_payout_window"]
        purchase_id = account.purchase_id
        purchase_no = account.purchase_no
        purchase = get_purchase_contract_by_id(purchase_id)
        paid = get_paid_amount_by_purchase_contract(purchase_id)
        unpaid = purchase.amount - paid
        data = {"id": id, "purchase_no": purchase_no,
                "company": purchase.supply, "item": purchase.item,
                "payable": purchase.amount, "paid": paid,
                "amount": account.amount,
                "date": account.date,
                "bank_serial": account.bank_serial,
                "unpaid": unpaid,
                }
        render_payout_window(data)
        window.show()
    elif account.mold == PAYMENT_MOLD:
        pass


# def table_data_changed_handle(index):
#     window = gw["cash_in_out_window"]
#     model = window.inCashTableView.model()
#     row_data = model.get_row_dict(index.row())


def render_cash_in_table_data():
    window = gw["cash_in_out_window"]
    sale_id = int(window.saleIDLineEdit.text())
    account_list = query_income_account_by_sale_no(sale_id)
    headers = list(config["cash_in_view"].values())
    params = list(config["cash_in_view"].keys())
    data_list = []
    for account in account_list:
        line = []
        account = object_as_dict(account)
        for key in params:
            line.append(account.get(key))
        data_list.append(line)
    model = TableModel(data_list, headers, params)
    # model.dataChanged.connect(table_data_changed_handle)
    window.inCashTableView.setModel(model)
    window.inCashTableView.resizeColumnsToContents()


def package_payout_data(account):
    account_data = object_as_dict(account)
    purchase_id = account.purchase_id
    purchase = get_purchase_contract_by_id(purchase_id)
    account_data["item"] = purchase.item
    account_data["supply"] = purchase.supply
    return account_data


def render_cash_out_table_data():
    window = gw["cash_in_out_window"]
    sale_id = int(window.saleIDLineEdit.text())
    account_list = query_payout_account_by_sale_no(sale_id)
    headers = list(config["cash_out_view"].values())
    params = list(config["cash_out_view"].keys())
    data_list = []
    for account in account_list:
        line = []
        account = package_payout_data(account)
        for key in params:
            line.append(account.get(key))
        data_list.append(line)
    model = TableModel(data_list, headers, params)
    window.outCashTableView.setModel(model)
    window.outCashTableView.resizeColumnsToContents()


def init_income_tab():
    window = gw["cash_in_out_window"]
    sale_window = gw["add_sale_contract_window"]
    sale_no = sale_window.contractLineEdit.text()
    sale_id = int(sale_window.idLineEdit.text())
    window.saleIDLineEdit.setText(str(sale_id))
    window.companyLineEdit.setText(sale_window.companyCombox.currentText())
    window.saleContractLineEdit.setText(sale_no)
    window.receivableLineEdit.setText(sale_window.amountLineEdit.text())
    window.receivedLineEdit.setText(sale_window.incomeLineEdit.text())
    window.outstandingLineEdit.setText(sale_window.outstandingLineEdit.text())
    now = datetime.datetime.now()
    window.inAmountLineEdit.setText("")
    window.inDateEdit.setDate(QDate(now.year, now.month, now.day))
    window.payDate.setDate(QDate(now.year, now.month, now.day))
    render_cash_in_table_data()


def init_outcome_tab():
    window = gw["cash_in_out_window"]
    sale_window = gw["add_sale_contract_window"]
    sale_id = int(sale_window.idLineEdit.text())
    sale_no = sale_window.contractLineEdit.text()
    window.saleContractLineEdit2.setText(sale_no)
    window.payableLineEdit.setText(sale_window.mainCostLineEdit.text())
    window.totalPayableLineEdit.setText(sale_window.mainCostLineEdit.text())
    paid_total = get_paid_amount_by_sale_no(sale_id)
    window.paidTotalLineEdit.setText(f"{paid_total:,}")
    payable_total = get_payable_amount_by_sale_no(sale_id)
    unpaid = payable_total - paid_total
    window.unpaidLineEdit.setText(f"{unpaid:,}")
    item_list = query_unpaid_purchase_item_by_sale_no(sale_id)
    window.itemComboBox.clear()
    if item_list:
        window.itemComboBox.addItems(item_list)
    sale_window = gw["add_sale_contract_window"]
    index = sale_window.saleTabWidget.currentIndex()
    item = sale_window.saleTabWidget.tabText(index)
    if item_list:
        if item not in item_list:
            item = item_list[0]
    else:
        item = ""
    if item:
        window.itemComboBox.setCurrentText(item)
        purchase = query_purchase_by_item(sale_id, item)
        init_item_summary(purchase)
    else:
        init_empty_item_summary()
    render_cash_out_table_data()


def package_issue_invoice(invoice_list):
    result = []
    for invoice in invoice_list:
        invoice_data = object_as_dict(invoice)
        result.append(invoice_data)
    return result


def render_issue_invoice_table_data():
    window = gw["cash_in_out_window"]
    sale_window = gw["add_sale_contract_window"]
    sale_id = int(sale_window.idLineEdit.text())
    invoice_list = query_issue_invoice(sale_id)
    invoice_list = package_issue_invoice(invoice_list)
    params = list(config["cash_issue_invoice_view"].keys())
    headers = list(config["cash_issue_invoice_view"].values())
    data_model = StaticTableModel(invoice_list, headers, params)
    window.issueInvoiceTableView.setModel(data_model)
    window.issueInvoiceTableView.resizeColumnsToContents()


def init_issue_invoice_tab():
    window = gw["cash_in_out_window"]
    sale_window = gw["add_sale_contract_window"]
    total = amount_str_to_float(sale_window.amountLineEdit.text())
    issued = amount_str_to_float(sale_window.invoiceLineEdit.text())
    unissued = total - issued
    window.issueTotalAmtLineEdit.setText(sale_window.amountLineEdit.text())
    window.issuedAmtLineEdit.setText(sale_window.invoiceLineEdit.text())
    window.unissueAmtLineEdit.setText(f"{unissued:,}")
    window.companyLineEdit_2.setText(sale_window.companyCombox.currentText())
    set_date(window.issueDateEdit)
    render_issue_invoice_table_data()


def package_recv_invoice_data(invoice_list):
    result = []
    for invoice in invoice_list:
        invoice_data = object_as_dict(invoice)
        result.append(invoice_data)
    return result


def render_recv_invoice_table():
    window = gw["cash_in_out_window"]
    sale_id = int(window.saleIDLineEdit.text())
    invoice_list = query_recv_invoice(sale_id)
    invoice_list = package_recv_invoice_data(invoice_list)
    params = list(config["cash_recv_invoice_view"].keys())
    headers = list(config["cash_recv_invoice_view"].values())
    data_model = StaticTableModel(invoice_list, headers, params)
    window.receiveInvoiceTableView.setModel(data_model)
    window.receiveInvoiceTableView.resizeColumnsToContents()


def init_recv_invoice_tab():
    window = gw["cash_in_out_window"]
    sale_id = int(window.saleIDLineEdit.text())
    main_cost = query_main_cost_by_sale_id(sale_id)
    window.rcvTotalAmtLineEdit.setText(f"{main_cost:,}")
    recv_invoice = query_recv_invoice_amount_by_sale(sale_id)
    window.rcvReceivedAmtLineEdit.setText(f"{recv_invoice:,}")
    un_receive = main_cost - recv_invoice
    window.rcvUnreceivedAmtLineEdit.setText(f"{un_receive:,}")
    init_recv_invoice_form()
    render_recv_invoice_table()


def init_cash_tab_data():
    init_income_tab()
    init_outcome_tab()
    init_issue_invoice_tab()
    init_recv_invoice_tab()


def view_cash_in_handle():
    window = gw["cash_in_out_window"]
    window.cashTabWidget.setCurrentIndex(0)
    window.inCashTableView.resizeColumnsToContents()
    window.outCashTableView.resizeColumnsToContents()
    view_cash_tab_handle()


def view_cash_out_handle():
    window = gw["cash_in_out_window"]
    window.cashTabWidget.setCurrentIndex(1)
    view_cash_tab_handle()


def view_cash_tab_handle():
    window = gw["cash_in_out_window"]
    status_bar = window.cashTabStatusbar
    sale_window = gw["add_sale_contract_window"]
    sale_no = sale_window.contractLineEdit.text()
    if not sale_no:
        show_failed_message(status_bar, "没有关联合同")
    else:
        init_cash_tab_data()
        show_window(window, status_bar)


def filter_cash_in_form():
    window = gw["cash_in_out_window"]
    amount = window.inAmountLineEdit.text()
    amount = check_float(amount)
    if amount is False or amount == 0:
        raise ValueTypeErrException("收款金额错误")
    date = window.inDateEdit.date().toPython()
    sale_id = int(window.saleIDLineEdit.text())
    return {"amount": amount, "date": date, "sale_id": sale_id}


def add_cash_in_handle():
    window = gw["cash_in_out_window"]
    status_bar = window.cashTabStatusbar
    try:
        income_data = filter_cash_in_form()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    outstanding_amount = window.outstandingLineEdit.text()
    outstanding_amount = outstanding_amount.replace(",", "")
    outstanding_amount = float(outstanding_amount)
    if income_data["amount"] > outstanding_amount:
        show_failed_message(status_bar, "收款金额超过未收金额")
        return
    try:
        save_income_data(income_data)
    except Exception as exc:
        logger.error("save in cash error. %s", exc)
        show_failed_message(status_bar, "新增入账失败")
        return
    show_success_message(status_bar, "新增入账成功")
    sale_no = income_data["sale_no"]
    fresh_add_sale_contract_by_contract_no(sale_no)
    init_cash_tab_data()


def filter_cash_out_form():
    window = gw["cash_in_out_window"]
    amount = window.payAmountLineEdit.text()
    amount = check_float(amount)
    if amount is False:
        raise ValueTypeErrException("付款金额错误")
    date = window.payDate.date().toPython()
    sale_id = int(window.saleIDLineEdit.text())
    purchase_id = int(window.purchaseIDLineEdit.text())
    return {"amount": amount, "date": date, "sale_id": sale_id,
            "purchase_id": purchase_id}


def add_cash_out_handle():
    window = gw["cash_in_out_window"]
    status_bar = window.cashTabStatusbar
    try:
        outcome_data = filter_cash_out_form()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    unpaid = window.itemUnpaidLineEdit.text()
    unpaid = amount_str_to_float(unpaid)
    if outcome_data["amount"] > unpaid:
        show_failed_message(status_bar, "付款金额超过欠款")
        return
    try:
        save_payout_data(outcome_data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    show_success_message(status_bar, "新增出账成功")
    sale_no = window.saleContractLineEdit.text()
    fresh_add_sale_contract_by_contract_no(sale_no)
    init_cash_tab_data()


def init_item_summary(purchase):
    window = gw["cash_in_out_window"]
    window.supplyLineEdit.setText(purchase.supply)
    window.payableLineEdit.setText(f"{purchase.amount:,}")
    window.purchaseIDLineEdit.setText(str(purchase.id))
    paid_amount = get_paid_amount_by_purchase_contract(purchase.id)
    window.paidLineEdit.setText(f"{paid_amount:,}")
    unpaid_amount = purchase.amount - paid_amount
    window.itemUnpaidLineEdit.setText(f"{unpaid_amount:,}")


def item_changed_handle():
    window = gw["cash_in_out_window"]
    sale_id = int(window.idLineEdit.text())
    item = window.itemComboBox.currentText()
    purchase = query_purchase_by_item(sale_id, item)
    init_item_summary(purchase)


def init_empty_item_summary():
    window = gw["cash_in_out_window"]
    window.itemComboBox.addItems("")
    window.itemComboBox.setCurrentText("")
    window.supplyLineEdit.setText("")
    window.payableLineEdit.setText("")
    window.purchaseIDLineEdit.setText("")
    window.paidLineEdit.setText("")
    window.itemUnpaidLineEdit.setText("")


def init_issue_invoice_form():
    window = gw["cash_in_out_window"]
    window.issueAmtLineEdit.setText("")
    set_date(window.issueDateEdit)


def filter_issue_invoice_form():
    window = gw["cash_in_out_window"]
    sale_id = int(window.saleIDLineEdit.text())
    company = window.companyLineEdit_2.text()
    amount = window.issueAmtLineEdit.text()
    amount = check_float(amount)
    if amount is False:
        raise ValueTypeErrException("金额错误")
    date = window.issueDateEdit.date().toPython()
    data = {"sale_id": sale_id, "amount": amount, "date": date,
            "company": company}
    return data


def add_issue_invoice_handle():
    window = gw["cash_in_out_window"]
    status_bar = window.cashTabStatusbar
    try:
        invoice_data = filter_issue_invoice_form()
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    try:
        save_issue_invoice(invoice_data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    show_success_message(status_bar, "提交成功")
    init_issue_invoice_form()
    render_issue_invoice_table_data()


def filter_recv_invoice_form():
    window = gw["cash_in_out_window"]
    sale_id = int(window.saleIDLineEdit.text())
    company = window.rcvCmpCombox.currentText()
    purchase = query_purchase_by_sale_and_supply(sale_id, company)
    amount = window.rcvAmtLineEdit.text()
    amount = check_float(amount)
    if amount is False:
        raise ValueTypeErrException("金额错误")
    date = window.rcvDateEdit.date().toPython()
    invoice_data = {"company": company, "purchase_id": purchase.id,
                    "amount": amount, "date": date, "sale_id": sale_id}
    return invoice_data


def init_recv_invoice_form():
    window = gw["cash_in_out_window"]
    sale_id = int(window.saleIDLineEdit.text())
    purchase_list = query_purchase_contract_by_sale(sale_id)
    company_list = [purchase.supply for purchase in purchase_list]
    window.rcvCmpCombox.clear()
    window.rcvCmpCombox.addItems(company_list)
    window.rcvAmtLineEdit.setText("")
    set_date(window.rcvDateEdit)


def add_recv_invoice_handle():
    window = gw["cash_in_out_window"]
    status_bar = window.cashTabStatusbar
    try:
        invoice_data = filter_recv_invoice_form()
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    try:
        save_recv_invoice(invoice_data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    show_success_message(status_bar, "提交成功")
    init_recv_invoice_form()
    render_recv_invoice_table()
