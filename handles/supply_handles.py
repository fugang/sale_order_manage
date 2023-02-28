from globals import gw, config
from models.data_operation import save_supply, get_supply_detail, \
    update_supply, list_item
from models.table_model import ModifyTableModel
from utils import object_as_dict, show_success_message, show_failed_message
from exceptions import ValueTypeErrException


def init_supply_window():
    window = gw["base_info_window"]
    window.supplyLineEdit.setText("")
    window.supplyAddrLineEdit.setText("")
    window.supplyLinkmanLineEdit.setText("")
    window.supplyPhoneLineEdit.setText("")


def filter_supply_info():
    window = gw["base_info_window"]
    company = window.supplyLineEdit.text()
    if not company:
        raise ValueTypeErrException("供应商公司名称错误")
    address = window.supplyAddrLineEdit.text()
    linkman = window.supplyLinkmanLineEdit.text()
    phone = window.supplyPhoneLineEdit.text()
    items = window.itemComboBox.currentData()
    if not items:
        raise ValueTypeErrException("物品类型错误")
    items = ",".join(items)
    supply_data = {"company": company, "address": address,
                   "linkman": linkman, "phone": phone,
                   "items": items,
                   }
    return supply_data

def save_supply_info_handle():
    window = gw["base_info_window"]
    status_bar = window.baseInfoStatusbar
    try:
        supply_data = filter_supply_info()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    try:
        save_supply(supply_data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    show_success_message(status_bar, "添加成功")
    init_supply_window()
    render_supply_tab_data()


def get_supply_table_dict():
    table_data = []
    supply_list = get_supply_detail()
    for supply in supply_list:
        supply = object_as_dict(supply)
        table_data.append(supply)
    return table_data


def get_current_supply_cell():
    window = gw["view_supply_window"]
    table_view = window.supplyTableView
    index = table_view.currentIndex()
    row = index.row()
    row_data = table_view.model().get_row_data(row)
    column = index.column()
    keys = list(config["supply_view"].keys())
    field = keys[column]
    value = row_data[column]
    return field, value


def get_current_row_id():
    window = gw["view_supply_window"]
    table_view = window.supplyTableView
    index = table_view.currentIndex()
    row = index.row()
    if row == -1:
        return -1
    else:
        id = table_view.model().get_row_id(row)
        return id


def modify_supply_handle():
    pass


def supply_data_changed_handle(index):
    window = gw["base_info_window"]
    status_bar = window.baseInfoStatusbar
    model = window.supplyTableView.model()
    row_data = model.get_row_data(index)
    id = row_data["id"]
    try:
        update_supply(id, row_data)
    except Exception:
        show_failed_message(status_bar, "保存失败")
        return
    show_success_message(status_bar, "保存成功")
    render_supply_tab_data()

def render_supply_tab_data():
    window = gw["base_info_window"]
    supply_list = get_supply_table_dict()
    headers = list(config["supply_view"].values())
    params = list(config["supply_view"].keys())
    supply_model = ModifyTableModel(supply_list, headers, params)
    supply_model.dataChanged.connect(supply_data_changed_handle)
    window.supplyTableView.setModel(supply_model)
    window.supplyTableView.resizeColumnsToContents()
    item_names = list_item()
    window.itemComboBox.clear()
    window.itemComboBox.addItems(item_names)
    window.itemComboBox.setCurrentData("")
