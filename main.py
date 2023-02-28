import sys
import traceback

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QFile
from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtGui import QScreen, QAction, QIcon

from globals import gw, logger
from handles.sale_contract_handles import add_sale_contract_handle, \
    save_sale_contract_handle, render_sale_contract_table, \
    render_main_window, sale_contract_table_click_handle, \
    download_contract_file, download_emi_contract_file, \
    download_ems_contract_file, download_trans_contract_file, \
    download_shield_contract_file, download_desk_contract_file, \
    download_computer_contract_file, download_other_contract_file, \
    upload_contract_file, upload_emi_contract_file, \
    upload_ems_contract_file, upload_trans_contract_file, \
    upload_shield_contract_file, upload_computer_contract_file, \
    upload_desk_contract_file, upload_other_contract_file, \
    view_contract_file, view_emi_contract_file, \
    view_ems_contract_file, view_trans_contract_file, \
    view_shield_contract_file, view_desk_contract_file, \
    view_computer_contract_file, view_other_contract_file

from handles.customer_handlers import save_customer_handle, \
    get_customer_by_company_handle
from handles.saler_handlers import save_saler_handle
from handles.purchase_handles import view_purchase_handle, \
     purchase_table_click_handle, save_purchase_data_in_tab
from handles.supply_handles import save_supply_info_handle
from handles.item_handles import save_item_handle
from widgets.checkedCombox import MultiComboBox
from handles.cash_handles import view_cash_handle, \
    fresh_cash_table_handle, modify_cash_handle, \
    view_cash_in_handle, add_cash_in_handle, view_cash_out_handle, \
    add_cash_out_handle, save_payment_handle, item_changed_handle, \
    add_issue_invoice_handle, add_recv_invoice_handle
from handles.common_handles import fresh_pruchase_table
from handles.base_info_handle import base_info_handle
from handles.export_handle import export_excel_handle, about_handle


try:
    from ctypes import windll
    myappid = 'zksj.1.0.0'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


def main():
    app = QApplication(sys.argv)
    icon = QIcon("610.ico")
    app.setWindowIcon(icon)
    screen_size = QScreen.availableGeometry(QApplication.primaryScreen())
    ui_loader = QUiLoader()
    ui_loader.registerCustomWidget(MultiComboBox)
    main_ui = QFile("ui/main_window.ui")
    main_ui.open(QFile.ReadOnly)
    main_window = ui_loader.load(main_ui)
    main_window.setWindowIcon(icon)
    gw["main_window"] = main_window

    main_window.saleContractTableView.doubleClicked.connect(
        sale_contract_table_click_handle)

    add_sale_contract_ui = QFile("ui/add_sale_contract.ui")
    add_sale_contract_ui.open(QFile.ReadOnly)
    add_sale_contract_window = ui_loader.load(add_sale_contract_ui)
    add_sale_contract_window.customerIDLineEdit.hide()
    add_sale_contract_window.lobIDLineEdit.hide()
    add_sale_contract_window.filepathLineEdit.hide()
    add_sale_contract_window.emiPathLineEdit.hide()
    add_sale_contract_window.emsPathLineEdit.hide()
    add_sale_contract_window.transPathLineEdit.hide()
    add_sale_contract_window.shieldPathLineEdit.hide()
    add_sale_contract_window.deskPathLineEdit.hide()
    add_sale_contract_window.compPathLineEdit.hide()
    add_sale_contract_window.otherPathLineEdit.hide()
    add_sale_contract_window.emiLobIDLineEdit.hide()
    add_sale_contract_window.emsLobIDLineEdit.hide()
    add_sale_contract_window.transLobIDLineEdit.hide()
    add_sale_contract_window.shieldLobIDLineEdit.hide()
    add_sale_contract_window.deskLobIDLineEdit.hide()
    add_sale_contract_window.compLobIDLineEdit.hide()
    add_sale_contract_window.otherLobIDLineEdit.hide()
    add_sale_contract_window.addPerfButton.clicked.connect(save_sale_contract_handle)
    add_sale_contract_window.addPurchaseButton.clicked.connect(save_purchase_data_in_tab)
    add_sale_contract_window.companyCombox.currentTextChanged.connect(
        get_customer_by_company_handle)
    add_sale_contract_window.cashInButton.clicked.connect(view_cash_in_handle)
    add_sale_contract_window.cashOutButton.clicked.connect(view_cash_out_handle)
    add_sale_contract_window.downloadButton.clicked.connect(download_contract_file)
    add_sale_contract_window.emiDownButton.clicked.connect(download_emi_contract_file)
    add_sale_contract_window.emsDownButton.clicked.connect(download_ems_contract_file)
    add_sale_contract_window.transDownButton.clicked.connect(download_trans_contract_file)
    add_sale_contract_window.shieldDownButton.clicked.connect(download_shield_contract_file)
    add_sale_contract_window.deskDownButton.clicked.connect(download_desk_contract_file)
    add_sale_contract_window.compDownButton.clicked.connect(download_computer_contract_file)
    add_sale_contract_window.otherDownButton.clicked.connect(download_other_contract_file)
    add_sale_contract_window.addFileButton.clicked.connect(upload_contract_file)
    add_sale_contract_window.emiUploadButton.clicked.connect(upload_emi_contract_file)
    add_sale_contract_window.emsUploadButton.clicked.connect(upload_ems_contract_file)
    add_sale_contract_window.transUploadButton.clicked.connect(upload_trans_contract_file)
    add_sale_contract_window.shieldUploadButton.clicked.connect(upload_shield_contract_file)
    add_sale_contract_window.deskUploadButton.clicked.connect(upload_desk_contract_file)
    add_sale_contract_window.compUploadButton.clicked.connect(upload_computer_contract_file)
    add_sale_contract_window.otherUploadButton.clicked.connect(upload_other_contract_file)
    add_sale_contract_window.viewPushButton.clicked.connect(view_contract_file)
    add_sale_contract_window.emiViewButton.clicked.connect(view_emi_contract_file)
    add_sale_contract_window.emsViewButton.clicked.connect(view_ems_contract_file)
    add_sale_contract_window.transViewButton.clicked.connect(view_trans_contract_file)
    add_sale_contract_window.shieldViewButton.clicked.connect(view_shield_contract_file)
    add_sale_contract_window.deskViewButton.clicked.connect(view_desk_contract_file)
    add_sale_contract_window.compViewButton.clicked.connect(view_computer_contract_file)
    add_sale_contract_window.otherViewButton.clicked.connect(view_other_contract_file)
    gw["add_sale_contract_window"] = add_sale_contract_window

    view_cash_ui = QFile("ui/view_cash.ui")
    view_cash_ui.open(QFile.ReadOnly)
    view_cash_window = ui_loader.load(view_cash_ui)
    view_cash_window.companylineEdit.textChanged.connect(fresh_cash_table_handle)
    view_cash_window.moldCombox.currentIndexChanged.connect(fresh_cash_table_handle)
    view_cash_window.yearCombox.currentIndexChanged.connect(fresh_cash_table_handle)
    view_cash_window.monthCombox.currentTextChanged.connect(fresh_cash_table_handle)
    view_cash_window.viewCashtableView.doubleClicked.connect(modify_cash_handle)
    view_cash_window.addPaymentButton.clicked.connect(save_payment_handle)
    gw["view_cash_window"] = view_cash_window

    cash_in_out_ui = QFile("ui/cash_in_out.ui")
    cash_in_out_ui.open(QFile.ReadOnly)
    cash_in_out_window = ui_loader.load(cash_in_out_ui)
    cash_in_out_window.purchaseIDLineEdit.hide()
    cash_in_out_window.saleIDLineEdit.hide()
    cash_in_out_window.purchseIDLineEdit.hide()
    cash_in_out_window.addInCashButton.clicked.connect(add_cash_in_handle)
    cash_in_out_window.addOutCashButton.clicked.connect(add_cash_out_handle)
    cash_in_out_window.itemComboBox.currentTextChanged.connect(item_changed_handle)
    cash_in_out_window.issueInvoicePushButton.clicked.connect(add_issue_invoice_handle)
    cash_in_out_window.recvInvoicePushButton.clicked.connect(add_recv_invoice_handle)
    gw["cash_in_out_window"] = cash_in_out_window

    base_info_ui = QFile("ui/base_info.ui")
    base_info_ui.open(QFile.ReadOnly)
    base_info_window = ui_loader.load(base_info_ui)
    base_info_window.addCustomerButton.clicked.connect(save_customer_handle)
    base_info_window.addSupplyButton.clicked.connect(save_supply_info_handle)
    base_info_window.addSalerButton.clicked.connect(save_saler_handle)
    base_info_window.addItemButton.clicked.connect(save_item_handle)
    gw["base_info_window"] = base_info_window

    view_purchase_ui = QFile("ui/view_purchase.ui")
    view_purchase_ui.open(QFile.ReadOnly)
    view_purchase_window = ui_loader.load(view_purchase_ui)
    view_purchase_window.supplyCombox.currentIndexChanged.connect(fresh_pruchase_table)
    view_purchase_window.yearCombox.currentIndexChanged.connect(fresh_pruchase_table)
    view_purchase_window.saleContractLineEdit.textChanged.connect(fresh_pruchase_table)
    view_purchase_window.monthCombox.currentTextChanged.connect(fresh_pruchase_table)
    view_purchase_window.productCombox.currentTextChanged.connect(fresh_pruchase_table)
    view_purchase_window.purchaseTableView.doubleClicked.connect(
        purchase_table_click_handle)
    gw["view_purchase_window"] = view_purchase_window

    about_ui = QFile("ui/about.ui")
    about_ui.open(QFile.ReadOnly)
    about_window = ui_loader.load(about_ui)
    gw["about_window"] = about_window

    render_main_window()
    main_window.setFixedWidth(screen_size.width())
    main_window.setFixedHeight(screen_size.height()-30)
    main_window.showMaximized()

    main_window.saleContractTableView.setFixedWidth(screen_size.width()-20)
    main_window.saleContractTableView.setFixedHeight(screen_size.height()-200)

    main_window.yearCombox.currentIndexChanged.connect(render_sale_contract_table)
    main_window.monthCombox.currentTextChanged.connect(render_sale_contract_table)
    main_window.salerCombox.currentTextChanged.connect(render_sale_contract_table)
    main_window.productCombox.currentTextChanged.connect(render_sale_contract_table)

    add_sale_action = QAction("销售合同", main_window)
    add_sale_action.setStatusTip("新增销售合同")
    add_sale_action.triggered.connect(add_sale_contract_handle)
    main_window.toolBar.addAction(add_sale_action)

    view_purchase_action = QAction("采购订单", main_window)
    view_purchase_action.setStatusTip("采购订单")
    view_purchase_action.triggered.connect(view_purchase_handle)
    main_window.toolBar.addAction(view_purchase_action)

    base_info_action = QAction("基础信息", main_window)
    base_info_action.setStatusTip("客户信息|供应商信息|销售员信息|采购物品信息")
    base_info_action.triggered.connect(base_info_handle)
    main_window.toolBar.addAction(base_info_action)

    view_cash_action = QAction("现金流", main_window)
    view_cash_action.setStatusTip("查看出/入账信息")
    view_cash_action.triggered.connect(view_cash_handle)
    main_window.toolBar.addAction(view_cash_action)

    export_excel_action = QAction("导出数据", main_window)
    export_excel_action.setStatusTip("导出销售合同列表和采购合同列表")
    export_excel_action.triggered.connect(export_excel_handle)
    main_window.toolBar.addAction(export_excel_action)

    about_action = QAction("关于", main_window)
    about_action.triggered.connect(about_handle)
    main_window.toolBar.addAction(about_action)

    # init_context_menu()
    app.exec()


# main()

try:
    main()
except Exception as exc:
    traceback.print_exc()
    logger.exception(exc)
