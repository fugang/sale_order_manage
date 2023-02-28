from globals import gw

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QCursor

from globals import gw
from .sale_contract_handles import modify_contract_data_handle, cancel_contract_handle
from .purchase_handles import add_purchase_handle, \
    modify_purchase_handle
from .supply_handles import modify_supply_handle
from .item_handles import modify_item_handle
from .cash_handles import add_income_handle, modify_cash_handle, \
    view_income_handle, add_payout_handle, view_payout_handle


def sale_contract_menu_handle(pos):
    menu = QMenu()
    edit_action = menu.addAction("修改")
    cancel_action = menu.addAction('作废')
    menu.addSeparator()
    add_purchase_action = menu.addAction("新建采购合同")
    view_purchase_action = menu.addAction("查看采购合同")
    menu.addSeparator()
    add_income_action = menu.addAction("新建入账")
    view_income_action = menu.addAction("查看入账")

    edit_action.triggered.connect(modify_contract_data_handle)
    cancel_action.triggered.connect(cancel_contract_handle)
    add_purchase_action.triggered.connect(add_purchase_handle)
    view_purchase_action.triggered.connect()
    add_income_action.triggered.connect(add_income_handle)
    view_income_action.triggered.connect(view_income_handle)
    menu.exec_(QCursor.pos())


def init_sale_contract_context_menu():
    main_window = gw["main_window"]
    table_view = main_window.saleContractTableView
    table_view.setContextMenuPolicy(Qt.CustomContextMenu)
    table_view.customContextMenuRequested.connect(sale_contract_menu_handle)



def supply_menu_handle(pos):
    menu = QMenu()
    edit_action = menu.addAction("修改")
    edit_action.triggered.connect(modify_supply_handle)
    menu.exec_(QCursor.pos())


def init_supply_info_context_menu():
    window = gw["view_supply_window"]
    table_view = window.supplyTableView
    table_view.setContextMenuPolicy(Qt.CustomContextMenu)
    table_view.customContextMenuRequested.connect(supply_menu_handle)


def customer_menu_handle(pos):
    # menu = QMenu()
    # edit_action = menu.addAction("修改")
    # edit_action.triggered.connect(modify_customer_handle)
    # menu.exec_(QCursor.pos())
    pass


def init_customer_info_context_menu():
    window = gw["view_customer_window"]
    table_view = window.customerTableView
    table_view.setContextMenuPolicy(Qt.CustomContextMenu)
    table_view.customContextMenuRequested.connect(customer_menu_handle)


def item_menu_handle(pos):
    menu = QMenu()
    edit_action = menu.addAction("修改")
    edit_action.triggered.connect(modify_item_handle)
    menu.exec_(QCursor.pos())


def init_item_info_context_menu():
    window = gw["view_item_window"]
    table_view = window.itemTableView
    table_view.setContextMenuPolicy(Qt.CustomContextMenu)
    table_view.customContextMenuRequested.connect(item_menu_handle)


def saler_menu_handle(pos):
    menu = QMenu()
    edit_action = menu.addAction("修改")
    edit_action.triggered.connect(modify_saler_handle)
    menu.exec_(QCursor.pos())


def init_saler_info_context_menu():
    window = gw["view_saler_window"]
    table_view = window.salerTableView
    table_view.setContextMenuPolicy(Qt.CustomContextMenu)
    table_view.customContextMenuRequested.connect(saler_menu_handle)


def cash_menu_handle(pos):
    menu = QMenu()
    edit_action = menu.addAction("修改")
    edit_action.triggered.connect(modify_cash_handle)
    menu.exec_(QCursor.pos())


def init_account_info_context_menu():
    window = gw["view_cash_window"]
    table_view = window.viewCashtableView
    table_view.setContextMenuPolicy(Qt.CustomContextMenu)
    table_view.customContextMenuRequested.connect(cash_menu_handle)


def purchase_menu_handle(pos):
    menu = QMenu()
    edit_action = menu.addAction("修改")
    add_payout_action = menu.addAction("新建出账")
    view_payout_action = menu.addAction("查看出账")
    edit_action.triggered.connect(modify_purchase_handle)
    add_payout_action.triggered.connect(add_payout_handle)
    view_payout_action.triggered.connect(view_payout_handle)
    menu.exec_(QCursor.pos())

def init_purchase_info_context_menu():
    window = gw["view_purchase_window"]
    table_view = window.purchaseTableView
    table_view.setContextMenuPolicy(Qt.CustomContextMenu)
    table_view.customContextMenuRequested.connect(purchase_menu_handle)


def init_context_menu():
    init_sale_contract_context_menu()
    init_supply_info_context_menu()
    init_customer_info_context_menu()
    init_item_info_context_menu()
    init_saler_info_context_menu()
    init_purchase_info_context_menu()
    init_account_info_context_menu()
