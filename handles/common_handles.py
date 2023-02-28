import os
import datetime
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox

from globals import gw, config
from utils import object_as_dict, set_date
from models.data_operation import query_purchase_contract_by_sale,\
    query_purchase_by_item, get_received_amount_by_sale_contract, \
    query_sale_contract, get_purchase_contract, \
    get_paid_amount_by_purchase_contract, list_saler, \
    list_customer_company, get_sale_contract_by_id, \
    get_sale_contract_by_contract_no, get_customer_by_id, \
    list_supply_by_item, query_issue_invoice_amount, \
    query_recv_invoice_amount_by_purchase, list_industry
from models.table_model import TableModel


def get_current_sale_contract_row_dict():
    window = gw["main_window"]
    table_view = window.saleContractTableView
    index = table_view.currentIndex()
    row = index.row()
    if row == -1:
        return {}
    else:
        data = table_view.model().get_row_dict(row)
        return data

def get_current_sale_contract_cell():
    window = gw["main_window"]
    table_view = window.saleContractTableView
    index = table_view.currentIndex()
    row = index.row()
    row_data = table_view.model().get_row_data(row)
    column = index.column()
    keys = list(config["sale_contract"].keys())
    field = keys[column]
    value = row_data[column]
    return field, value


def get_current_sale_contract_id():
    window = gw["main_window"]
    table_view = window.saleContractTableView
    index = table_view.currentIndex()
    row = index.row()
    if row == -1:
        return -1
    else:
        id = table_view.model().get_row_id(row)
        return id


def calc_main_cost(purchase_list):
    main_cost = 0
    for purchase in purchase_list:
        main_cost += purchase.amount
    return main_cost


def calc_commission(sale_contract):
    if sale_contract.assistant:
        commission = (sale_contract.amount - sale_contract.discount) * 0.03
    else:
        commission = 0
    return commission

def calc_profit(revenue, tax_rate):
    profit = revenue / (1 + tax_rate/100)
    profit = round(profit, 1)
    return profit


def sum_purchase_amount(purchase):
    if purchase:
        return purchase.amount
    else:
        return 0


def calc_emi_cost(sale_id):
    purchase = query_purchase_by_item(sale_id, "EMI")
    cost = sum_purchase_amount(purchase)
    return cost


def calc_ems_cost(sale_id):
    purchase = query_purchase_by_item(sale_id, "EMS")
    cost = sum_purchase_amount(purchase)
    return cost


def calc_vol_trans_cost(sale_id):
    purchase_list = query_purchase_by_item(sale_id, "隔离变压器")
    cost = sum_purchase_amount(purchase_list)
    return cost


def calc_shield_cost(sale_id):
    purchase = query_purchase_by_item(sale_id, "屏蔽房")
    cost = sum_purchase_amount(purchase)
    return cost


def calc_computer_cost(sale_id):
    purchase = query_purchase_by_item(sale_id, "电脑")
    cost = sum_purchase_amount(purchase)
    return cost


def calc_env_desk_cost(sale_id):
    purchase = query_purchase_by_item(sale_id, "环境和桌子")
    cost = sum_purchase_amount(purchase)
    return cost


def calc_other_cost(sale_id):
    purchase = query_purchase_by_item(sale_id, "其他")
    cost = sum_purchase_amount(purchase)
    return cost


def package_purchase_list(purchase_list):
    data = {}
    payable_total = 0
    paid_total = 0
    for purchase in purchase_list:
        payable_total += purchase.amount
        item_paid = get_paid_amount_by_purchase_contract(purchase.id)
        invoice_amount = query_recv_invoice_amount_by_purchase(purchase.id)
        paid_total += item_paid
        if purchase.item == "EMS":
            data["ems_id"] = purchase.id
            data["ems_supply"] = purchase.supply
            data["ems_type"] = purchase.product_type
            data["ems_amount"] = purchase.amount
            data["ems_count"] = purchase.count
            data["ems_mark"] = purchase.mark
            data["ems_paid"] = item_paid
            data["ems_unpaid"] = purchase.amount - item_paid
            data["ems_purchase_no"] = purchase.purchase_no
            data["ems_date"] = purchase.date
            data["ems_file_path"] = purchase.file_path
            data["ems_lob_id"] = purchase.lob_id
            data["ems_invoice"] = invoice_amount
        elif purchase.item == "EMI":
            data["emi_id"] = purchase.id
            data["emi_supply"] = purchase.supply
            data["emi_type"] = purchase.product_type
            data["emi_amount"] = purchase.amount
            data["emi_count"] = purchase.count
            data["emi_mark"] = purchase.mark
            data["emi_paid"] = item_paid
            data["emi_unpaid"] = purchase.amount - item_paid
            data["emi_purchase_no"] = purchase.purchase_no
            data["emi_date"] = purchase.date
            data["emi_invoice"] = invoice_amount
            data["emi_file_path"] = purchase.file_path
            data["emi_lob_id"] = purchase.lob_id
        elif purchase.item == "隔离变压器":
            data["trans_id"] = purchase.id
            data["trans_supply"] = purchase.supply
            data["trans_type"] = purchase.product_type
            data["trans_amount"] = purchase.amount
            data["trans_count"] = purchase.count
            data["trans_mark"] = purchase.mark
            data["trans_paid"] = item_paid
            data["trans_unpaid"] = purchase.amount - item_paid
            data["trans_purchase_no"] = purchase.purchase_no
            data["trans_date"] = purchase.date
            data["trans_invoice"] = invoice_amount
            data["trans_file_path"] = purchase.file_path
            data["trans_lob_id"] = purchase.lob_id
        elif purchase.item == "屏蔽房":
            data["shield_id"] = purchase.id
            data["shield_supply"] = purchase.supply
            data["shield_type"] = purchase.product_type
            data["shield_amount"] = purchase.amount
            data["shield_count"] = purchase.count
            data["shield_mark"] = purchase.mark
            data["shield_paid"] = item_paid
            data["shield_unpaid"] = purchase.amount - item_paid
            data["shield_purchase_no"] = purchase.purchase_no
            data["shield_date"] = purchase.date
            data["shield_invoice"] = invoice_amount
            data["shield_file_path"] = purchase.file_path
            data["shield_lob_id"] = purchase.lob_id
        elif purchase.item == "电脑":
            data["computer_id"] = purchase.id
            data["computer_supply"] = purchase.supply
            data["computer_type"] = purchase.product_type
            data["computer_amount"] = purchase.amount
            data["computer_count"] = purchase.count
            data["computer_mark"] = purchase.mark
            data["computer_paid"] = item_paid
            data["computer_unpaid"] = purchase.amount - item_paid
            data["computer_purchase_no"] = purchase.purchase_no
            data["computer_date"] = purchase.date
            data["computer_invoice"] = invoice_amount
            data["computer_file_path"] = purchase.file_path
            data["computer_lob_id"] = purchase.lob_id
        elif purchase.item == "环境和桌子":
            data["desk_id"] = purchase.id
            data["desk_supply"] = purchase.supply
            data["desk_type"] = purchase.product_type
            data["desk_amount"] = purchase.amount
            data["desk_count"] = purchase.count
            data["desk_mark"] = purchase.mark
            data["desk_paid"] = item_paid
            data["desk_unpaid"] = purchase.amount - item_paid
            data["desk_purchase_no"] = purchase.purchase_no
            data["desk_date"] = purchase.date
            data["desk_invoice"] = invoice_amount
            data["desk_file_path"] = purchase.file_path
            data["desk_lob_id"] = purchase.lob_id
        elif purchase.item == "其他":
            data["other_id"] = purchase.id
            data["other_supply"] = purchase.supply
            data["other_type"] = purchase.product_type
            data["other_amount"] = purchase.amount
            data["other_count"] = purchase.count
            data["other_mark"] = purchase.mark
            data["other_paid"] = item_paid
            data["other_unpaid"] = purchase.amount - item_paid
            data["other_purchase_no"] = purchase.purchase_no
            data["other_date"] = purchase.date
            data["other_invoice"] = invoice_amount
            data["other_file_path"] = purchase.file_path
            data["other_lob_id"] = purchase.lob_id
    unpaid_total = payable_total - paid_total
    data["payable_total"] = payable_total
    data["unpaid_total"] = unpaid_total
    return data


def package_sale_contract_data(sale_contract):
    sale_dict = object_as_dict(sale_contract)
    sale_id = sale_contract.id
    customer_id = sale_contract.customer_id
    customer = get_customer_by_id(customer_id)
    if customer:
        sale_dict["company"] = customer.company
        sale_dict["customer_id"] = customer.id
        sale_dict["industry"] = customer.industry
    if not sale_contract.discount:
        sale_dict["discount"] = 0
    purchase_list = query_purchase_contract_by_sale(sale_id)
    purchase_data = package_purchase_list(purchase_list)
    sale_dict.update(purchase_data)
    sale_dict["ems_cost"] = calc_ems_cost(sale_id)
    sale_dict["emi_cost"] = calc_emi_cost(sale_id)
    sale_dict["vol_trans_cost"] = calc_vol_trans_cost(sale_id)
    sale_dict["shield_cost"] = calc_shield_cost(sale_id)
    sale_dict["computer_cost"] = calc_computer_cost(sale_id)
    sale_dict["other_cost"] = calc_other_cost(sale_id)
    sale_dict["env_desk_cost"] = calc_env_desk_cost(sale_id)
    main_cost = calc_main_cost(purchase_list)
    sale_dict["main_cost"] = main_cost
    received_amount = get_received_amount_by_sale_contract(sale_id)
    sale_dict["income"] = received_amount
    sale_dict["outstanding"] = sale_contract.amount - received_amount
    commission = calc_commission(sale_contract)
    sale_dict["commission"] = commission
    if sale_contract.discount:
        payable_amount = sale_contract.discount + main_cost + commission
    else:
        payable_amount = main_cost + commission
    sale_dict["payableLineEdit"] = payable_amount
    revenue = sale_contract.amount - payable_amount
    sale_dict["revenue"] = revenue
    sale_dict["profit"] = calc_profit(revenue, sale_contract.tax_rate)
    invoice_amount = query_issue_invoice_amount(sale_id)
    sale_dict["invoice_amount"] = invoice_amount
    return sale_dict


def get_sale_table_data(saler, year, month_list, product):
    table_data = []
    window = gw["main_window"]
    query_data = query_sale_contract(saler, year, month_list, product)
    total_amount = 0
    total_cost = 0
    total_revenue = 0
    total_profit = 0
    for contract in query_data:
        data = []
        contract_dict = package_sale_contract_data(contract)
        total_amount += contract_dict["amount"]
        total_cost += contract_dict["main_cost"] + \
                      contract_dict["discount"] + contract_dict["commission"]
        total_revenue += contract_dict["revenue"]
        total_profit += contract_dict["profit"]
        for key in config["sale_contract"].keys():
            data.append(contract_dict.get(key))
        table_data.append(data)
    total = len(table_data)
    window.sumIncomeLineEdit.setText(f"{total_amount:,}")
    window.sumCostLineEdit.setText(f"{total_cost:,}")
    window.sumRevenueLineEdit.setText(f"{total_revenue:,}")
    window.sumProfitLineEdit.setText(f"{total_profit:,}")
    window.totalLineEdit.setText(f"{total}")
    return table_data


def render_sale_table_data():
    window = gw["main_window"]
    year = window.yearCombox.currentText().strip()
    month_list = window.monthCombox.currentData()
    if month_list:
        month_list = [int(month[:-1]) for month in month_list]
    saler = window.salerCombox.currentText()
    product = window.productCombox.currentText()
    table_data = get_sale_table_data(saler, year, month_list, product)
    return table_data


def render_sale_contract_table():
    window = gw["main_window"]
    table_data = render_sale_table_data()
    headers = list(config["sale_contract"].values())
    params = list(config["sale_contract"].keys())
    data_model = TableModel(table_data, headers, params)
    window.saleContractTableView.setModel(data_model)
    window.saleContractTableView.resizeColumnsToContents()


def package_purchase_record(purchase):
    purchase_dict = object_as_dict(purchase)
    paid_amount = get_paid_amount_by_purchase_contract(purchase.id)
    purchase_dict["paid"] = paid_amount
    unpaid_amount = purchase.amount - paid_amount
    purchase_dict["unpaid"] = unpaid_amount
    return purchase_dict


def get_purchase_table_data():
    table_data = []
    window = gw["view_purchase_window"]
    supply = window.supplyCombox.currentText()
    year = window.yearCombox.currentText()
    month_list = window.monthCombox.currentData()
    product = window.productCombox.currentText()
    month_list = [int(m[:-1]) for m in month_list]
    contract_no = window.saleContractLineEdit.text()
    purchase_list = get_purchase_contract(supply, year, contract_no,
                                          month_list, product)
    total_payable = 0
    total_paid = 0
    total_unpaid = 0
    total = len(purchase_list)
    for purchase in purchase_list:
        data = package_purchase_record(purchase)
        total_payable += data["amount"]
        total_paid += data["paid"]
        total_unpaid += data["unpaid"]
        purchase_line = []
        for key in config["purchase_contract"].keys():
            purchase_line.append(data.get(key))
        table_data.append(purchase_line)
    window.payableLineEdit.setText(f"{total_payable:,}")
    window.paidLineEdit.setText(f"{total_paid:,}")
    window.unpaidLineEdit.setText(f"{total_unpaid:,}")
    window.countLineEdit.setText(f"{total}")
    return table_data


def render_purchase_table_data():
    window = gw["view_purchase_window"]
    headers = list(config["purchase_contract"].values())
    params = list(config["purchase_contract"].keys())
    table_data = get_purchase_table_data()
    model = TableModel(table_data, headers, params)
    window.purchaseTableView.setModel(model)
    window.purchaseTableView.resizeColumnsToContents()


def fresh_pruchase_table():
    window = gw["view_purchase_window"]
    render_purchase_table_data()
    window.show()


def init_sale_contract_form(data):
    window = gw["add_sale_contract_window"]
    if data and "id" in data:
        window.idLineEdit.setText(str(data["id"]))
        window.idLineEdit.show()
        window.idLabel.show()
        window.receivedLabel_2.hide()
        window.receivedLineEdit.hide()
    else:
        window.idLineEdit.setText("")
        window.idLineEdit.hide()
        window.idLabel.hide()
        window.receivedLineEdit.setText("")
        window.receivedLabel_2.show()
        window.receivedLineEdit.show()
    if data and "customer_id" in data:
        window.customerIDLineEdit.setText(str(data["customer_id"]))
    window.salerCombox.clear()
    saler_list = list_saler()
    window.salerCombox.addItem("")
    window.salerCombox.addItems(saler_list)
    if data and "saler" in data:
        window.salerCombox.setCurrentText(data["saler"])
        window.salerCombox.setEnabled(False)
    else:
        window.salerCombox.setCurrentText("")
        window.salerCombox.setEnabled(True)
    window.assisComboBox.clear()
    window.assisComboBox.addItem("")
    window.assisComboBox.addItems(saler_list)
    if data and "assistant" in data:
        window.assisComboBox.setCurrentText(data["assistant"])
    else:
        window.assisComboBox.setCurrentText("")
    window.companyCombox.clear()
    window.companyCombox.addItem("")
    window.companyCombox.addItems(list_customer_company())
    if data and "company" in data:
        window.companyCombox.clear()
        window.companyCombox.setCurrentText(data["company"])
        window.companyCombox.setEnabled(True)
        window.companyCombox.lineEdit().setReadOnly(True)
    else:
        window.companyCombox.setEnabled(True)
        window.companyCombox.lineEdit().setReadOnly(False)
    window.industryCombox.clear()
    window.industryCombox.addItem("")
    window.industryCombox.addItems(list_industry())
    if data and "industry" in data:
        window.industryCombox.setCurrentText(data["industry"])
    else:
        window.industryCombox.setCurrentText("")

    if data and "date" in data:
        date = data["date"]
        window.signDateEdit.setDate(QDate(date.year, date.month, date.day))
    else:
        now = datetime.datetime.now()
        window.signDateEdit.setDate(QDate(now.year, now.month, now.day))
    if data and "sale_no" in data:
        window.contractLineEdit.setText(data["sale_no"])
    else:
        window.contractLineEdit.setText("")
    if data and "amount" in data and data["amount"]:
        window.amountLineEdit.setText(f"{data['amount']:,}")
    else:
        window.amountLineEdit.setText("")
    if data and "discount" in data and data["discount"]:
        window.discountLineEdit.setText(f'{data["discount"]:,}')
    else:
        window.discountLineEdit.setText("")
    if data and "marks" in data:
        window.marksTextEdit.setText(data["marks"])
    else:
        window.marksTextEdit.setText("")
    if data and "tax_rate" in data and data["tax_rate"]:
        window.taxRateLineEdit.setText(str(data["tax_rate"]))
    else:
        window.taxRateLineEdit.setText("13")
    if data and "file_path" in data and data["file_path"]:
        filename = os.path.basename(data["file_path"])
        window.downloadButton.setText(filename)
        window.filepathLineEdit.setText(data["file_path"])
        window.viewPushButton.setEnabled(True)
    else:
        window.downloadButton.setText("")
        window.filepathLineEdit.setText("")
        window.viewPushButton.setEnabled(False)
    if data and "lob_id" in data:
        window.lobIDLineEdit.setText(str(data["lob_id"]))
    else:
        window.lobIDLineEdit.setText("")
    if data and "invoice_amount" in data:
        window.invoiceLineEdit.setText(f"{data['invoice_amount']:,}")
        window.invoiceLineEdit.setEnabled(False)
        window.invoiceDateEdit.hide()
        window.invoiceDateLabel.hide()
    else:
        window.invoiceLineEdit.setText("")
        window.invoiceLineEdit.setEnabled(True)
        window.invoiceDateEdit.show()
        window.invoiceDateLabel.show()
        set_date(window.invoiceDateEdit)


def init_purchase_emi_form(data):
    window = gw["add_sale_contract_window"]
    if data and "emi_id" in data:
        window.emiIDLineEdit.setText(str(data["emi_id"]))
        window.emiIDLabel.show()
        window.emiIDLineEdit.show()
        window.emiPaidAmountLabel.hide()
        window.emiPaidAmountLineEdit.hide()
    else:
        window.emiIDLabel.hide()
        window.emiIDLineEdit.hide()
        window.emiPaidAmountLabel.show()
        window.emiPaidAmountLineEdit.show()
        window.emiPaidAmountLineEdit.setText("")
        window.emiIDLineEdit.setText("")
    window.emiSupplyCombo.clear()
    window.emiSupplyCombo.addItem("")
    if data and "emi_date" in data:
        set_date(window.emiDateEdit, data["emi_date"])
    else:
        set_date(window.emiDateEdit)
    for supply in list_supply_by_item("EMI"):
        window.emiSupplyCombo.addItem(supply)
    if data and "emi_supply" in data:
        window.emiSupplyCombo.setCurrentText(data["emi_supply"])
    if data and "emi_purchase_no" in data:
        window.emiSerialLineEdit.setText(data["emi_purchase_no"])
    if data and "emi_paid" in data:
        window.emiPaidLineEdit.setText(f"{data['emi_paid']:,}")
    else:
        window.emiPaidLineEdit.setText("0")
    if data and "emi_unpaid" in data:
        window.emiUnpaidLineEdit.setText(f"{data['emi_unpaid']:,}")
    else:
        window.emiUnpaidLineEdit.setText("0")
    if data and "emi_type" in data:
        window.emiProductLineEdit.setText(data["emi_type"])
    else:
        window.emiProductLineEdit.setText("")
    if data and "emi_amount" in data:
        window.emiCostLineEdit.setText(f"{data['emi_amount']:,}")
    else:
        window.emiCostLineEdit.setText("")
    if data and "emi_count" in data:
        window.emiCountLineEdit.setText(str(data["emi_count"]))
    else:
        window.emiCountLineEdit.setText("")
    if data and "emi_mark" in data:
        window.emiMarkLineEdit.setText(data["emi_mark"])
    else:
        window.emiMarkLineEdit.setText("")
    if data and "emi_invoice" in data:
        window.emiInvoiceLineEdit.setText(f"{data['emi_invoice']:,}")
        window.emiInvoiceLineEdit.setEnabled(False)
        window.emiInvoiceLabel.hide()
        window.emiInvoiceDateEdit.hide()
    else:
        window.emiInvoiceLineEdit.setText("")
        window.emiInvoiceLineEdit.setEnabled(True)
        window.emiInvoiceLabel.show()
        window.emiInvoiceDateEdit.show()
        set_date(window.emiInvoiceDateEdit)
    if data and "emi_file_path" in data and data["emi_file_path"]:
        filename = os.path.basename(data["emi_file_path"])
        window.emiDownButton.setText(filename)
        window.emiPathLineEdit.setText(data["emi_file_path"])
        window.emiViewButton.setEnabled(True)
    else:
        window.emiDownButton.setText("")
        window.emiPathLineEdit.setText("")
        window.emiViewButton.setEnabled(False)
    if data and "emi_lob_id" in data:
        window.emiLobIDLineEdit.setText(str(data["emi_lob_id"]))
    else:
        window.emiLobIDLineEdit.setText("")


def init_purchase_ems_form(data):
    window = gw["add_sale_contract_window"]
    if data and "ems_id" in data:
        window.emsIDLineEdit.setText(str(data["ems_id"]))
        window.emsIDLineEdit.show()
        window.emsIDLabel.show()
        window.emsPaidamountLabel.hide()
        window.emsPaidamountLineEdit.hide()
    else:
        window.emsIDLineEdit.setText("")
        window.emsIDLineEdit.hide()
        window.emsIDLabel.hide()
        window.emsPaidamountLabel.show()
        window.emsPaidamountLineEdit.show()
        window.emsPaidamountLineEdit.setText("")
    window.emsSupplyCombo.clear()
    window.emsSupplyCombo.addItem("")
    for supply in list_supply_by_item("EMS"):
        window.emsSupplyCombo.addItem(supply)
    if data and "ems_supply" in data:
        window.emsSupplyCombo.setCurrentText(data["ems_supply"])
    if data and "ems_purchase_no" in data:
        window.emsSerialLineEdit.setText(data["ems_purchase_no"])
    if data and "ems_paid" in data:
        window.emsPaidLineEdit.setText(f"{data['ems_paid']:,}")
    else:
        window.emsPaidLineEdit.setText("0")
    if data and "ems_unpaid" in data:
        window.emsUnpaidLineEdit.setText(f"{data['ems_unpaid']:,}")
    else:
        window.emsUnpaidLineEdit.setText("0")
    if data and "ems_type" in data:
        window.emsProductLineEdit.setText(data["ems_type"])
    else:
        window.emsProductLineEdit.setText("")
    if data and "ems_amount" in data:
        window.emsCostLineEdit.setText(f"{data['ems_amount']:,}")
    else:
        window.emsCostLineEdit.setText("")
    if data and "ems_count" in data:
        window.emsCountLineEdit.setText(str(data["ems_count"]))
    else:
        window.emsCountLineEdit.setText("")
    if data and "ems_mark" in data:
        window.emsMarkLineEdit.setText(data["ems_mark"])
    else:
        window.emsMarkLineEdit.setText("")
    if data and "ems_date" in data:
        set_date(window.emsDateEdit, data["ems_date"])
    else:
        set_date(window.emsDateEdit)
    if data and "ems_invoice" in data:
        window.emsInvoiceLineEdit.setText(f"{data['ems_invoice']:,}")
        window.emsInvoiceLineEdit.setEnabled(False)
        window.emsInvoiceLabel.hide()
        window.emsInvoiceDateEdit.hide()
    else:
        window.emsInvoiceLineEdit.setText("")
        window.emsInvoiceLineEdit.setEnabled(True)
        set_date(window.emsInvoiceDateEdit)
        window.emsInvoiceLabel.show()
        window.emsInvoiceDateEdit.show()
    if data and "ems_file_path" in data and data["ems_file_path"]:
        filename = os.path.basename(data["ems_file_path"])
        window.emsDownButton.setText(filename)
        window.emsPathLineEdit.setText(data["ems_file_path"])
        window.emsViewButton.setEnabled(True)
    else:
        window.emsDownButton.setText("")
        window.emsPathLineEdit.setText("")
        window.emsViewButton.setEnabled(False)
    if data and "ems_lob_id" in data:
        window.emsLobIDLineEdit.setText(str(data["ems_lob_id"]))
    else:
        window.emsLobIDLineEdit.setText("")


def init_purchase_vol_trans_form(data):
    window = gw["add_sale_contract_window"]
    if data and "trans_id" in data:
        window.voltransIDLineEdit.setText(str(data["trans_id"]))
        window.voltransIDLineEdit.show()
        window.voltransIDLabel.show()
        window.transPaidAmountLabel.hide()
        window.transPaidAmountLineEdit.hide()
    else:
        window.voltransIDLineEdit.setText("")
        window.voltransIDLineEdit.hide()
        window.voltransIDLabel.hide()
        window.transPaidAmountLabel.show()
        window.transPaidAmountLineEdit.show()
        window.transPaidAmountLineEdit.setText("")
    window.voltransSupplyCombo.clear()
    window.voltransSupplyCombo.addItem("")
    for supply in list_supply_by_item("隔离变压器"):
        window.voltransSupplyCombo.addItem(supply)
    if data and "trans_supply" in data:
        window.voltransSupplyCombo.setCurrentText(data["trans_supply"])
    if data and "trans_purchase_no" in data:
        window.transSerialLineEdit.setText(data["trans_purchase_no"])
    if data and "trans_paid" in data:
        window.voltransPaidLineEdit.setText(f"{data['trans_paid']:,}")
    else:
        window.voltransPaidLineEdit.setText("0")
    if data and "trans_unpaid" in data:
        window.transUnpaidLineEdit.setText(f"{data['trans_unpaid']:,}")
    else:
        window.transUnpaidLineEdit.setText("0")
    if data and "trans_type" in data:
        window.voltransProductLineEdit.setText(data["trans_type"])
    else:
        window.voltransProductLineEdit.setText("")
    if data and "trans_amount" in data:
        window.voltransCostLineEdit.setText(f"{data['trans_amount']:,}")
    else:
        window.voltransCostLineEdit.setText("")
    if data and "trans_count" in data:
        window.voltransCountLineEdit.setText(str(data["trans_count"]))
    else:
        window.voltransCountLineEdit.setText("")
    if data and "trans_mark" in data:
        window.voltransMarkLineEdit.setText(data["trans_mark"])
    else:
        window.voltransMarkLineEdit.setText("")
    if data and "trans_date" in data:
        set_date(window.transDateEdit, data["trans_date"])
    else:
        set_date(window.transDateEdit)
    if data and "trans_invoice" in data:
        window.transInvoiceLineEdit.setText(f"{data['trans_invoice']:,}")
        window.transInvoiceLineEdit.setEnabled(False)
        window.transInvoiceDateEdit.hide()
        window.transInvoiceLabel.hide()
    else:
        window.transInvoiceLineEdit.setText("")
        window.transInvoiceLineEdit.setEnabled(True)
        set_date(window.transInvoiceDateEdit)
        window.transInvoiceDateEdit.show()
        window.transInvoiceLabel.show()
    if data and "trans_file_path" in data and data["trans_file_path"]:
        filename = os.path.basename(data["trans_file_path"])
        window.transDownButton.setText(filename)
        window.transPathLineEdit.setText(data["trans_file_path"])
        window.transViewButton.setEnabled(True)
    else:
        window.transDownButton.setText("")
        window.transPathLineEdit.setText("")
        window.transViewButton.setEnabled(False)
    if data and "trans_lob_id" in data:
        window.transLobIDLineEdit.setText(str(data["trans_lob_id"]))
    else:
        window.transLobIDLineEdit.setText("")


def init_purchase_shield_form(data):
    window = gw["add_sale_contract_window"]
    if data and "shield_id" in data:
        window.shieldIDLineEdit.setText(str(data["shield_id"]))
        window.shieldIDLineEdit.show()
        window.shieldIDLabel.show()
        window.shieldPaidAmountLabel.hide()
        window.shieldPaidAmountLineEdit.hide()
    else:
        window.shieldIDLineEdit.setText("")
        window.shieldIDLineEdit.hide()
        window.shieldIDLabel.hide()
        window.shieldPaidAmountLabel.show()
        window.shieldPaidAmountLineEdit.show()
        window.shieldPaidAmountLineEdit.setText("")
    window.shieldSupplyCombo.clear()
    window.shieldSupplyCombo.addItem("")
    for supply in list_supply_by_item("屏蔽房"):
        window.shieldSupplyCombo.addItem(supply)
    if data and "shield_supply" in data:
        window.shieldSupplyCombo.setCurrentText(data["shield_supply"])
    if data and "shield_purchase_no" in data:
        window.shiedSerialLineEdit.setText(data["shield_purchase_no"])
    if data and "shield_paid" in data:
        window.shieldPaidLineEdit.setText(f"{data['shield_paid']:,}")
    else:
        window.shieldPaidLineEdit.setText("0")
    if data and "shield_unpaid" in data:
        window.shieldUnpaidLineEdit.setText(f"{data['shield_unpaid']:,}")
    else:
        window.shieldUnpaidLineEdit.setText("0")
    if data and "shield_type" in data:
        window.shieldProductLineEdit.setText(data["shield_type"])
    else:
        window.shieldProductLineEdit.setText("")
    if data and "shield_amount" in data:
        window.shieldCostLineEdit.setText(f'{data["shield_amount"]:,}')
    else:
        window.shieldCostLineEdit.setText("")
    if data and "shield_count" in data:
        window.shieldCountLineEdit.setText(str(data["shield_count"]))
    else:
        window.shieldCountLineEdit.setText("")
    if data and "shield_mark" in data:
        window.shieldMarkLineEdit.setText(data["shield_mark"])
    else:
        window.shieldMarkLineEdit.setText("")
    if data and "shield_date" in data:
        set_date(window.shieldDateEdit, data["shield_date"])
    else:
        set_date(window.shieldDateEdit)
    if data and "shield_invoice" in data:
        window.shieldInvoiceLineEdit.setText(f"{data['shield_invoice']:,}")
        window.shieldInvoiceLineEdit.setEnabled(False)
        window.shieldInvoiceLabel.hide()
        window.shieldInvoiceDateEdit.hide()
    else:
        window.shieldInvoiceLineEdit.setText("")
        window.shieldInvoiceLineEdit.setEnabled(True)
        window.shieldInvoiceLabel.show()
        window.shieldInvoiceDateEdit.show()
        set_date(window.shieldInvoiceDateEdit)
    if data and "shield_file_path" in data and data["shield_file_path"]:
        filename = os.path.basename(data["shield_file_path"])
        window.shieldDownButton.setText(filename)
        window.shieldPathLineEdit.setText(data["shield_file_path"])
        window.shieldViewButton.setEnabled(True)
    else:
        window.shieldDownButton.setText("")
        window.shieldPathLineEdit.setText("")
        window.shieldViewButton.setEnabled(False)
    if data and "shield_lob_id" in data:
        window.shieldLobIDLineEdit.setText(str(data["shield_lob_id"]))
    else:
        window.shieldLobIDLineEdit.setText("")


def init_purchase_computer_form(data):
    window = gw["add_sale_contract_window"]
    if data and "computer_id" in data:
        window.computerIDLineEdit.setText(str(data["computer_id"]))
        window.computerIDLineEdit.show()
        window.computerIDLabel.show()
        window.computerPaidAmountLabel.hide()
        window.computerPaidAmountLineEdit.hide()
    else:
        window.computerIDLineEdit.setText("")
        window.computerIDLineEdit.hide()
        window.computerIDLabel.hide()
        window.computerPaidAmountLabel.show()
        window.computerPaidAmountLineEdit.show()
        window.computerPaidAmountLineEdit.setText("")
    window.computerSupplyCombo.clear()
    window.computerSupplyCombo.addItem("")
    for supply in list_supply_by_item("电脑"):
        window.computerSupplyCombo.addItem(supply)
    if data and "computer_supply" in data:
        window.computerSupplyCombo.setCurrentText(data["computer_supply"])
    if data and "computer_purchase_no" in data:
        window.computerSerialLineEdit.setText(data["computer_purchase_no"])
    if data and "computer_paid" in data:
        window.computerPaidLineEdit.setText(f"{data['computer_paid']:,}")
    else:
        window.computerPaidLineEdit.setText("0")
    if data and "computer_unpaid" in data:
        window.computerUnpaidLineEdit.setText(f"{data['computer_unpaid']:,}")
    else:
        window.computerUnpaidLineEdit.setText("0")
    if data and "computer_type" in data:
        window.computerProductLineEdit.setText(data["computer_type"])
    else:
        window.computerProductLineEdit.setText("")
    if data and "computer_amount" in data:
        window.computerCostLineEdit.setText(f"{data['computer_amount']:,}")
    else:
        window.computerCostLineEdit.setText("")
    if data and "computer_count" in data:
        window.computerCountLineEdit.setText(str(data["computer_count"]))
    else:
        window.computerCountLineEdit.setText("")
    if data and "computer_mark" in data:
        window.computerMarkLineEdit.setText(data["computer_mark"])
    else:
        window.computerMarkLineEdit.setText("")
    if data and "computer_date" in data:
        set_date(window.computerDateEdit, data["computer_date"])
    else:
        set_date(window.computerDateEdit)
    if data and "computer_invoice" in data:
        window.compInvoiceLineEdit.setText(f"{data['computer_invoice']:,}")
        window.compInvoiceLineEdit.setEnabled(False)
        window.compInvoiceLabel.hide()
        window.compInvoiceDateEdit.hide()
    else:
        window.compInvoiceLineEdit.setEnabled(True)
        window.compInvoiceLabel.show()
        window.compInvoiceDateEdit.show()
        set_date(window.deskInvoiceDateEdit)
    if data and "computer_file_path" in data and data["computer_file_path"]:
        filename = os.path.basename(data["computer_file_path"])
        window.compDownButton.setText(filename)
        window.compPathLineEdit.setText(data["computer_file_path"])
        window.compViewButton.setEnabled(True)
    else:
        window.compDownButton.setText("")
        window.compPathLineEdit.setText("")
        window.compViewButton.setEnabled(False)
    if data and "computer_lob_id" in data:
        window.compLobIDLineEdit.setText(str(data["computer_lob_id"]))
    else:
        window.compLobIDLineEdit.setText("")


def init_purchase_desk_form(data):
    window = gw["add_sale_contract_window"]
    if data and "desk_id" in data:
        window.deskIDLineEdit.setText(str(data["desk_id"]))
        window.deskIDLineEdit.show()
        window.deskIDLabel.show()
        window.deskPaidAmountLabel.hide()
        window.deskPaidAmountLineEdit.hide()
    else:
        window.deskIDLineEdit.setText("")
        window.deskIDLineEdit.hide()
        window.deskIDLabel.hide()
        window.deskPaidAmountLabel.show()
        window.deskPaidAmountLineEdit.show()
        window.deskPaidAmountLineEdit.setText("")
    window.deskSupplyCombo.clear()
    window.deskSupplyCombo.addItem("")
    for supply in list_supply_by_item("环境和桌子"):
        window.deskSupplyCombo.addItem(supply)
    if data and "desk_supply" in data:
        window.deskSupplyCombo.setCurrentText(data["desk_supply"])
    if data and "desk_purchase_no" in data:
        window.deskSerialLineEdit.setText(data["desk_purchase_no"])
    if data and "desk_paid" in data:
        window.deskPaidLineEdit.setText(f"{data['desk_paid']:,}")
    else:
        window.deskPaidLineEdit.setText("0")
    if data and "desk_unpaid" in data:
        window.deskUnpaidLineEdit.setText(f"{data['desk_unpaid']:,}")
    else:
        window.deskUnpaidLineEdit.setText("0")
    if data and "desk_type" in data:
        window.deskProductLineEdit.setText(data["desk_type"])
    else:
        window.deskProductLineEdit.setText("")
    if data and "desk_amount" in data:
        window.deskCostLineEdit.setText(f"{data['desk_amount']:,}")
    else:
        window.deskCostLineEdit.setText("")
    if data and "desk_count" in data:
        window.deskCountLineEdit.setText(str(data["desk_count"]))
    else:
        window.deskCountLineEdit.setText("")
    if data and "desk_mark" in data:
        window.deskMarkLineEdit.setText(data["desk_mark"])
    else:
        window.deskMarkLineEdit.setText("")
    if data and "desk_date" in data:
        set_date(window.deskDateEdit, data["desk_date"])
    else:
        set_date(window.deskDateEdit)
    if data and "desk_invoice" in data:
        window.deskInvoiceAmtLineEdit.setEnabled(False)
        window.deskInvoiceAmtLineEdit.setText(f"{data['desk_invoice']:,}")
        window.deskInvoiceLabel.hide()
        window.deskInvoiceDateEdit.hide()
    else:
        window.deskInvoiceAmtLineEdit.setEnabled(True)
        window.deskInvoiceLabel.show()
        window.deskInvoiceDateEdit.show()
        set_date(window.compInvoiceDateEdit)
    if data and "desk_file_path" in data and data["desk_file_path"]:
        filename = os.path.basename(data["desk_file_path"])
        window.deskDownButton.setText(filename)
        window.deskPathLineEdit.setText(data["desk_file_path"])
        window.deskViewButton.setEnabled(True)
    else:
        window.deskDownButton.setText("")
        window.deskPathLineEdit.setText("")
        window.deskViewButton.setEnabled(False)
    if data and "desk_lob_id" in data:
        window.deskLobIDLineEdit.setText(str(data["desk_lob_id"]))
    else:
        window.deskLobIDLineEdit.setText("")


def init_purchase_other_form(data):
    window = gw["add_sale_contract_window"]
    if data and "other_id" in data:
        window.otherIDLineEdit.setText(str(data["other_id"]))
        window.otherIDLineEdit.show()
        window.otherIDLabel.show()
        window.otherPaidAmountLabel.hide()
        window.otherPaidAmountLineEdit.hide()
    else:
        window.otherIDLineEdit.setText("")
        window.otherIDLineEdit.hide()
        window.otherIDLabel.hide()
        window.otherPaidAmountLabel.show()
        window.otherPaidAmountLineEdit.show()
        window.otherPaidAmountLineEdit.setText("")
    window.otherSupplyCombo.clear()
    window.otherSupplyCombo.addItem("")
    for supply in list_supply_by_item("其他"):
        window.otherSupplyCombo.addItem(supply)
    if data and "other_supply" in data:
        window.otherSupplyCombo.setCurrentText(data["other_supply"])
    if data and "other_purchase_no" in data:
        window.otherSerialLineEdit.setText(data["other_purchase_no"])
    if data and "other_paid" in data:
        window.otherPaidLineEdit.setText(f"{data['other_paid']:,}")
    else:
        window.otherPaidLineEdit.setText("0")
    if data and "other_unpaid" in data:
        window.otherUnpaidLineEdit.setText(f"{data['other_unpaid']:,}")
    else:
        window.otherUnpaidLineEdit.setText("0")
    if data and "other_type" in data:
        window.otherProductLineEdit.setText(data["other_type"])
    else:
        window.otherProductLineEdit.setText("")
    if data and "other_amount" in data:
        window.otherCostLineEdit.setText(f"{data['other_amount']:,}")
    else:
        window.otherCostLineEdit.setText("")
    if data and "other_count" in data:
        window.otherCountLineEdit.setText(str(data["other_count"]))
    else:
        window.otherCountLineEdit.setText("")
    if data and "other_mark" in data:
        window.otherMarkLineEdit.setText(data["other_mark"])
    else:
        window.otherMarkLineEdit.setText("")
    if data and "other_date" in data:
        set_date(window.otherDateEdit, data["other_date"])
    else:
        set_date(window.otherDateEdit)
    if data and "other_invoice" in data:
        window.otherInvioceLineEdit.setText(f"{data['other_invoice']:,}")
        window.otherInvioceLineEdit.setEnabled(False)
        window.otherInvoiceLabel.hide()
        window.otherInvoiceDateEdit.hide()
    else:
        window.otherInvioceLineEdit.setEnabled(True)
        window.otherInvioceLineEdit.setText("")
        window.otherInvoiceLabel.show()
        window.otherInvoiceDateEdit.show()
        set_date(window.otherInvoiceDateEdit)
    if data and "other_file_path" in data and data["other_file_path"]:
        filename = os.path.basename(data["other_file_path"])
        window.otherDownButton.setText(filename)
        window.otherPathLineEdit.setText(data["other_file_path"])
        window.otherViewButton.setEnabled(True)
    else:
        window.otherDownButton.setText("")
        window.otherPathLineEdit.setText("")
        window.otherViewButton.setEnabled(False)
    if data and "other_lob_id" in data:
        window.otherLobIDLineEdit.setText(str(data["other_lob_id"]))
    else:
        window.otherLobIDLineEdit.setText("")


def init_sale_summary_form(data):
    window = gw["add_sale_contract_window"]
    if data and "main_cost" in data and data["main_cost"]:
        window.mainCostLineEdit.setText(f'{data["main_cost"]:,}')
    else:
        window.mainCostLineEdit.setText("")
    if data and "income" in data:
        window.incomeLineEdit.setText(f"{data['income']:,}")
    else:
        window.incomeLineEdit.setText("0")
    if data and "outstanding" in data:
        window.outstandingLineEdit.setText(f"{data['outstanding']:,}")
    else:
        window.outstandingLineEdit.setText("0")
    if data and "payableLineEdit" in data:
        window.payableLineEdit.setText(f"{data['payableLineEdit']:,}")
    else:
        window.payableLineEdit.setText("0")
    if data and "commission" in data:
        window.commisionLineEdit.setText(f'{data["commission"]:,}')
    else:
        window.commisionLineEdit.setText("")
    if data and "profit" in data:
        window.profitLineEdit.setText(f'{data["profit"]:,}')
    else:
        window.profitLineEdit.setText("")
    if data and "unpaid_total" in data:
        window.unpaidLineEdit.setText(f"{data['unpaid_total']:,}")
    else:
        window.unpaidLineEdit.setText("0")


def init_sale_contract_window(data=None):
    init_sale_contract_form(data)
    init_sale_summary_form(data)
    init_purchase_emi_form(data)
    init_purchase_ems_form(data)
    init_purchase_vol_trans_form(data)
    init_purchase_shield_form(data)
    init_purchase_computer_form(data)
    init_purchase_desk_form(data)
    init_purchase_other_form(data)


def fresh_add_sale_contract_by_contract_no(contract_no):
    sale_contract = get_sale_contract_by_contract_no(contract_no)
    data = package_sale_contract_data(sale_contract)
    init_sale_contract_window(data)


def fresh_add_sale_contract_window():
    id = get_current_sale_contract_id()
    if id == -1:
        window = gw["add_sale_contract_window"]
        id = window.idLineEdit.text()
        if not id:
            QMessageBox.warning(None, "错误", "空数据")
            return
        else:
            id = int(id)
    sale_contract = get_sale_contract_by_id(id)
    data = package_sale_contract_data(sale_contract)
    init_sale_contract_window(data)
