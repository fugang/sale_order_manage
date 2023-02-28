from globals import gw, config
from models.data_operation import save_item, get_item_detail, \
    update_item
from models.table_model import ItemModifyTableModel
from utils import object_as_dict, show_success_message, show_failed_message
from exceptions import ValueTypeErrException


def init_item_window():
    window = gw["base_info_window"]
    window.itemNameLineEdit.setText("")
    window.itemSpecLineEdit.setText("")


def filter_item():
    window = gw["base_info_window"]
    name = window.itemNameLineEdit.text()
    if not name:
        raise ValueTypeErrException("物品名称错误")
    specification = window.itemSpecLineEdit.text()
    item_data = {"name": name, "specification": specification}
    return item_data

def save_item_handle():
    window = gw["base_info_window"]
    status_bar = window.baseInfoStatusbar
    try:
        item_data = filter_item()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    try:
        save_item(item_data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    show_success_message(status_bar, "添加成功")
    init_item_window()
    render_item_tab_data()


def get_item_table_dict():
    table_data = []
    for item in get_item_detail():
        item = object_as_dict(item)
        table_data.append(item)
    return table_data

def modify_item_handle():
    pass


def item_data_changed_handle(index):
    window = gw["base_info_window"]
    status_bar = window.baseInfoStatusbar
    model = window.itemTableView.model()
    row_data = model.get_row_data(index)
    id = row_data["id"]
    try:
        update_item(id, row_data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    show_success_message(status_bar, "保存成功")
    render_item_tab_data()

def render_item_tab_data():
    window = gw["base_info_window"]
    item_table_data = get_item_table_dict()
    headers = list(config["item_view"].values())
    params = list(config["item_view"].keys())
    item_model = ItemModifyTableModel(item_table_data, headers, params)
    item_model.dataChanged.connect(item_data_changed_handle)
    window.itemTableView.setModel(item_model)
    window.itemTableView.resizeColumnsToContents()
