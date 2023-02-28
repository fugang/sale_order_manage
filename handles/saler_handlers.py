from globals import gw, config
from models.data_operation import save_saler, get_saler_detail, \
    update_saler
from models.table_model import ModifyTableModel
from utils import object_as_dict, show_failed_message, show_success_message
from exceptions import ValueTypeErrException


def filter_saler_data():
    window = gw["base_info_window"]
    name = window.salerLineEdit.text()
    if not name:
        raise ValueTypeErrException("销售员姓名错误")
    phone = window.salerPhoneLineEdit.text()
    return {"name": name, "phone": phone}

def init_saler_window():
    window = gw["base_info_window"]
    window.salerLineEdit.setText("")
    window.salerPhoneLineEdit.setText("")


def save_saler_handle():
    window = gw["base_info_window"]
    status_bar = window.baseInfoStatusbar
    try:
        data = filter_saler_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    try:
        save_saler(data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    show_success_message(status_bar, "添加成功")
    init_saler_window()
    render_saler_tab_data()

def get_saler_table_dict():
    table_data = []
    for saler in get_saler_detail():
        saler = object_as_dict(saler)
        table_data.append(saler)
    return table_data

def saler_data_changed_handle(index):
    window = gw["base_info_window"]
    status_bar = window.baseInfoStatusbar
    model = window.salerTableView.model()
    row_data = model.get_row_data(index)
    id = row_data["id"]
    try:
        update_saler(id, row_data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    show_success_message(status_bar, "保存成功")
    render_saler_tab_data()

def render_saler_tab_data():
    window = gw["base_info_window"]
    saler_table_data = get_saler_table_dict()
    headers = list(config["saler_view"].values())
    params = list(config["saler_view"].keys())
    saler_model = ModifyTableModel(saler_table_data, headers, params)
    saler_model.dataChanged.connect(saler_data_changed_handle)
    window.salerTableView.setModel(saler_model)
    window.salerTableView.resizeColumnsToContents()
