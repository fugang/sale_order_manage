from globals import gw
from .customer_handlers import render_customer_tab_data
from .supply_handles import render_supply_tab_data
from .saler_handlers import render_saler_tab_data
from .item_handles import render_item_tab_data
from utils import show_window


def base_info_handle():
    window = gw["base_info_window"]
    render_tab_data()
    status_bar = window.baseInfoStatusbar
    show_window(window, status_bar)


def render_tab_data():
    render_customer_tab_data()
    render_supply_tab_data()
    render_saler_tab_data()
    render_item_tab_data()

