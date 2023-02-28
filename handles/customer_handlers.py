from globals import gw, config
from models.data_operation import save_customer, \
    get_customer_detail, update_customer, \
    query_customer_by_company
from models.table_model import ModifyTableModel
from utils import object_as_dict, show_success_message, show_failed_message
from exceptions import ValueTypeErrException


def filter_customer_data():
    window = gw["base_info_window"]
    company = window.companyLineEdit.text()
    if not company:
        raise ValueTypeErrException("没有公司名称")
    industry = window.industryCombox.CurrentText()
    direction = window.directionLineEdit.text()
    address = window.addressLineEdit.text()
    linkman = window.linkmanLineEdit.text()
    phone = window.phoneLineEdit.text()
    customer_data = {"company": company, "address": address,
                     "linkman": linkman, "phone": phone,
                     "industry": industry, "direction": direction,
                     }
    return customer_data

def init_customer_form():
    window = gw["base_info_window"]
    window.companyLineEdit.setText("")
    window.industryCombox.setCurrentText("")
    window.directionLineEdit.setText("")
    window.addressLineEdit.setText("")
    window.linkmanLineEdit.setText("")
    window.phoneLineEdit.setText("")

def save_customer_handle():
    window = gw["base_info_window"]
    status_bar = window.baseInfoStatusbar
    try:
        data = filter_customer_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    try:
        save_customer(data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    show_success_message(status_bar, "添加客户信息成功")
    init_customer_form()
    render_customer_tab_data()


def get_customer_dict():
    customer_list = get_customer_detail()
    table_data = []
    for customer in customer_list:
        customer = object_as_dict(customer)
        table_data.append(customer)
    return table_data


def customer_data_changed_handle(index):
    window = gw["base_info_window"]
    status_bar = window.baseInfoStatusbar
    model = window.customerTableView.model()
    row_data = model.get_row_data(index)
    id = row_data["id"]
    try:
        update_customer(id, row_data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    render_customer_tab_data()
    show_success_message(status_bar, "更新成功")


def render_customer_tab_data():
    window = gw["base_info_window"]
    customer_table_data = get_customer_dict()
    headers = list(config["customer_view"].values())
    params = list(config["customer_view"].keys())
    table_model = ModifyTableModel(customer_table_data, headers, params)
    table_model.dataChanged.connect(customer_data_changed_handle)
    window.customerTableView.setModel(table_model)
    window.customerTableView.resizeColumnsToContents()


def get_customer_by_company_handle():
    window = gw["add_sale_contract_window"]
    company = window.companyCombox.currentText()
    customer = query_customer_by_company(company)
    if customer:
        window.customerIDLineEdit.setText(str(customer.id))
        window.industryCombox.setCurrentText(customer.industry)
        window.directionLineEdit.setText(customer.direction)
        window.addressLineEdit.setText(customer.address)
        window.linkmanLineEdit.setText(customer.linkman)
        window.phoneLineEdit.setText(customer.phone)
    else:
        window.customerIDLineEdit.setText("")
        window.industryCombox.setCurrentText("")
        window.directionLineEdit.setText("")
        window.addressLineEdit.setText("")
        window.linkmanLineEdit.setText("")
        window.phoneLineEdit.setText("")
