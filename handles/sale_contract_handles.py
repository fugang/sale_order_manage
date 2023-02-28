import os
import subprocess
from PySide6.QtWidgets import QFileDialog, QMessageBox
import hashlib

from globals import gw, logger
from models.data_operation import list_saler, cancel_sale_contract, \
    save_sale_contract, update_sale_contract, \
    upsert_customer, upsert_saler, save_file_data, \
    query_file_data_by_id, save_income_data, list_product_type, \
    save_issue_invoice, upset_industry
from exceptions import ValueTypeErrException
from utils import check_float, check_integer, show_failed_message, \
    show_success_message, show_window
from .common_handles import render_sale_contract_table, \
    get_current_sale_contract_id, get_current_sale_contract_cell, \
    init_sale_contract_window, fresh_add_sale_contract_window


def hide_id_field(action):
    window = gw["add_sale_contract_window"]
    id_widgets = [window.idLabel, window.idLineEdit,
                  window.emiIDLabel, window.emiIDLineEdit,
                  window.shieldIDLabel, window.shieldIDLineEdit,
                  window.otherIDLabel, window.otherIDLineEdit,
                  window.emsIDLabel, window.emsIDLineEdit,
                  window.computerIDLabel, window.computerIDLineEdit,
                  window.voltransIDLabel, window.voltransIDLineEdit,
                  window.deskIDLabel, window.deskIDLineEdit,
                  ]
    for widget in id_widgets:
        if action == "show":
            widget.show()
        elif action == "hide":
            widget.hide()


def add_sale_contract_handle():
    window = gw["add_sale_contract_window"]
    init_sale_contract_window()
    window.activateWindow()
    window.show()


def filter_sale_contract_data():
    window = gw["add_sale_contract_window"]
    id = window.idLineEdit.text()
    saler = window.salerCombox.currentText()
    if not saler:
        raise ValueTypeErrException("没有销售员")
    assistant = window.assisComboBox.currentText()
    sign_date = window.signDateEdit.date().toPython()
    company = window.companyCombox.currentText()
    if not company:
        raise ValueTypeErrException("没有公司名称")
    sale_no = window.contractLineEdit.text()
    if not sale_no:
        raise ValueTypeErrException("沒有合同编号")
    amount = window.amountLineEdit.text()
    amount = check_float(amount)
    if not amount:
        raise ValueTypeErrException("合同金额错误")
    if amount == 0:
        raise ValueTypeErrException("合同金额错误")
    tax_rate = window.taxRateLineEdit.text()
    tax_rate = check_integer(tax_rate)
    if tax_rate is False:
        raise ValueTypeErrException("税率错误")
    discount = window.discountLineEdit.text()
    discount = check_float(discount)
    if discount is False:
        raise ValueTypeErrException("回扣错误")
    marks = window.marksTextEdit.toPlainText()
    lob_id = window.lobIDLineEdit.text()
    if lob_id:
        lob_id = int(lob_id)
    file_path = window.filepathLineEdit.text()
    sale_contract = {"saler": saler, "assistant": assistant,
                     "date": sign_date,
                     "sale_no": sale_no, "amount": amount,
                     "tax_rate": tax_rate, "discount": discount,
                     "marks": marks, "lob_id": lob_id,
                     "file_path": file_path,
                     }
    if id:
        sale_contract["id"] = int(id)
    return sale_contract

def filter_purchase_base_data():
    window = gw["add_sale_contract_window"]
    contract_no = window.purchaseContractLineEdit.text()
    purchase_date = window.purchaseDateEdit.date().toPython()
    sale_contract_no = window.contractLineEdit.text()
    purchase_base = {"contract_no": contract_no, "date": purchase_date,
                     "sale_contract_no": sale_contract_no
                     }
    return purchase_base

def update_saler_combox():
    window = gw["main_window"]
    cur_text = window.salerCombox.currentText()
    window.salerCombox.clear()
    salers = list_saler()
    window.salerCombox.addItem("")
    window.salerCombox.addItems(salers)
    window.salerCombox.setCurrentText(cur_text)
    product_type_list = list_product_type()
    product_type_list.sort()
    window.productCombox.clear()
    if "" not in product_type_list:
        window.productCombox.addItem("")
    window.productCombox.addItems(product_type_list)
    window.productCombox.setCurrentText("")

    cur_month = window.monthCombox.currentText()
    window.monthCombox.clear()
    for i in range(1, 13):
        window.monthCombox.addItem(f"{i}月")
    if cur_month:
        window.monthCombox.setCurrentText(cur_month)


def render_main_window():
    update_saler_combox()
    render_sale_contract_table()


def sale_contract_table_click_handle():
    window = gw["add_sale_contract_window"]
    tab_index = {"emi_cost": 0, "ems_cost": 1, "vol_trans_cost": 2,
                 "shield_cost": 3, "env_desk_cost": 4,
                 "computer_cost": 5, "other_cost": 6
                 }
    field, value = get_current_sale_contract_cell()
    index = tab_index.get(field)
    if index is not None:
        window.saleTabWidget.setCurrentIndex(index)
    modify_contract_data_handle()


def fresh_combox():
    main_window = gw["main_window"]
    cur_text = main_window.salerCombox.currentText()
    salers = list_saler()
    main_window.salerCombox.addItem("")
    main_window.salerCombox.addItems(salers)
    main_window.salerCombox.setCurrentText(cur_text)


def filter_customer_data():
    window = gw["add_sale_contract_window"]
    company = window.companyCombox.currentText()
    industry = window.industryCombox.currentText()
    direction = window.directionLineEdit.text()
    address = window.addressLineEdit.text()
    linkman = window.linkmanLineEdit.text()
    phone = window.phoneLineEdit.text()
    id = window.customerIDLineEdit.text()
    customer = {"industry": industry, "direction": direction,
                "address": address, "linkman": linkman,
                "phone": phone, "company": company,
                }
    if id:
        customer["id"] = int(id)
    return customer


def save_sale_contract_handle():
    window = gw["add_sale_contract_window"]
    status_bar = window.addPerfStatusbar
    try:
        contract_data = filter_sale_contract_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    saler_name = window.salerCombox.currentText()
    saler_data = {"name": saler_name}
    try:
        upsert_saler(saler_data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    assistant = window.assisComboBox.currentText()
    if assistant:
        saler_data = {"name": assistant}
        try:
            upsert_saler(saler_data)
        except Exception as exc:
            show_failed_message(status_bar, str(exc))
            return
    customer_data = filter_customer_data()
    try:
        customer = upsert_customer(customer_data)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    try:
        upset_industry(customer.industry)
    except Exception as exc:
        show_failed_message(status_bar, str(exc))
        return
    contract_data["customer_id"] = customer.id
    id = window.idLineEdit.text()
    received_amount = window.receivedLineEdit.text()
    received_amount = check_float(received_amount)
    if received_amount is False:
        raise ValueTypeErrException("收款金额错误")
    if id:
        id = int(id)
        update_sale_contract(id, contract_data)
        show_success_message(status_bar, "更新成功")
    else:
        try:
            model = save_sale_contract(contract_data)
        except Exception as exc:
            logger.error("save sale button error. %s", exc)
            show_failed_message(status_bar, str(exc))
            return
        if received_amount:
            date = model.date
            income_data = {"amount": received_amount, "date": date, "sale_id": model.id}
            try:
                save_income_data(income_data)
            except Exception as exc:
                show_failed_message(status_bar, str(exc))
                return
        invoice_amount = window.invoiceLineEdit.text()
        invoice_amount = check_float(invoice_amount)
        if invoice_amount is False:
            show_failed_message(status_bar, "开票金额错误")
            return
        if invoice_amount:
            invoice_date = window.invoiceDateEdit.date().toPython()
            invoice_data = {"sale_id": model.id, "amount": invoice_amount,
                            "date": invoice_date, "company": customer.company}
            try:
                save_issue_invoice(invoice_data)
            except Exception as exc:
                show_failed_message(status_bar, str(exc))
                return
        window.idLineEdit.setText(str(model.id))
        show_success_message(status_bar, "提交成功")
    fresh_combox()
    render_sale_contract_table()
    fresh_add_sale_contract_window()


def cancel_contract_handle():
    window = gw["main_window"]
    status_bar = window.mainStatusBar
    id = get_current_sale_contract_id()
    cancel_sale_contract(id)
    show_success_message(status_bar, "已作废")


def modify_contract_data_handle():
    window = gw["add_sale_contract_window"]
    fresh_add_sale_contract_window()
    status_bar = window.addPerfStatusbar
    show_window(window, status_bar)


def save_contract_file(lob_id, file_path):
    if not lob_id:
        QMessageBox.warning(None, "错误", "未找到文件ID")
        return
    lob_id = int(lob_id)
    lob_obj = query_file_data_by_id(lob_id)
    lob = lob_obj.lob
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.AnyFile)
    file_list = dialog.getSaveFileName(None, "导出合同文件",
                                       file_path, "*.*")
    new_path = file_list[0]
    if new_path:
        try:
            with open(new_path, "wb") as writer:
                writer.write(lob)
        except Exception as exc:
            logger.error("write file error. %s", exc)
            QMessageBox.warning(None, "错误", "保存错误")
            return
        QMessageBox.information(None, "成功", "导出成功")


def download_contract_file():
    window = gw["add_sale_contract_window"]
    lob_id = window.lobIDLineEdit.text()
    file_path = window.filepathLineEdit.text()
    save_contract_file(lob_id, file_path)

def download_emi_contract_file():
    window = gw["add_sale_contract_window"]
    lob_id = window.emiLobIDLineEdit.text()
    file_path = window.emiPathLineEdit.text()
    save_contract_file(lob_id, file_path)

def download_ems_contract_file():
    window = gw["add_sale_contract_window"]
    lob_id = window.emsLobIDLineEdit.text()
    file_path = window.emsPathLineEdit.text()
    save_contract_file(lob_id, file_path)

def download_trans_contract_file():
    window = gw["add_sale_contract_window"]
    lob_id = window.transLobIDLineEdit.text()
    file_path = window.transPathLineEdit.text()
    save_contract_file(lob_id, file_path)

def download_shield_contract_file():
    window = gw["add_sale_contract_window"]
    lob_id = window.shieldLobIDLineEdit.text()
    file_path = window.shieldPathLineEdit.text()
    save_contract_file(lob_id, file_path)

def download_desk_contract_file():
    window = gw["add_sale_contract_window"]
    lob_id = window.deskdLobIDLineEdit.text()
    file_path = window.deskPathLineEdit.text()
    save_contract_file(lob_id, file_path)

def download_computer_contract_file():
    window = gw["add_sale_contract_window"]
    lob_id = window.compLobIDLineEdit.text()
    file_path = window.compPathLineEdit.text()
    save_contract_file(lob_id, file_path)

def download_other_contract_file():
    window = gw["add_sale_contract_window"]
    lob_id = window.otherLobIDLineEdit.text()
    file_path = window.otherPathLineEdit.text()
    save_contract_file(lob_id, file_path)

def save_lob_file(file_path):
    if not file_path:
        return
    with open(file_path, "rb") as reader:
        data = reader.read()
    md5sum = hashlib.md5(data).hexdigest()
    file_data = {"lob": data, "md5sum": md5sum}
    contract_file = save_file_data(file_data)
    file_id = contract_file.id
    return file_id

def select_and_save_file():
    window = gw["add_sale_contract_window"]
    sale_id = window.idLineEdit.text()
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.ExistingFile)
    file_obj = dialog.getOpenFileName()
    file_path = file_obj[0]
    file_id = save_lob_file(file_path)
    if sale_id and file_id:
        sale_id = int(sale_id)
        update_data = {"lob_id": file_id,
                       "file_path": file_path}
        update_sale_contract(sale_id, update_data)
    return file_path, file_id


def set_file_button_text(file_path, file_id,
                         lob_id_line, name_button,
                         view_button, path_line):
    filename = os.path.basename(file_path)
    lob_id_line.setText(str(file_id))
    name_button.setText(filename)
    view_button.setEnabled(True)
    path_line.setText(file_path)


def upload_contract_file():
    window = gw["add_sale_contract_window"]
    file_path, file_id = select_and_save_file()
    set_file_button_text(file_path, file_id,
                         window.lobIDLineEdit,
                         window.downloadButton,
                         window.viewPushButton,
                         window.filepathLineEdit,
                         )


def upload_emi_contract_file():
    window = gw["add_sale_contract_window"]
    file_path, file_id = select_and_save_file()
    set_file_button_text(file_path, file_id,
                         window.emiLobIDLineEdit,
                         window.emiDownButton,
                         window.emiViewButton,
                         window.emiPathLineEdit
                         )

def upload_ems_contract_file():
    window = gw["add_sale_contract_window"]
    file_path, file_id = select_and_save_file()
    set_file_button_text(file_path, file_id,
                         window.emsLobIDLineEdit,
                         window.emsDownButton,
                         window.emsViewButton,
                         window.emsPathLineEdit)

def upload_trans_contract_file():
    window = gw["add_sale_contract_window"]
    file_path, file_id = select_and_save_file()
    set_file_button_text(file_path, file_id,
                         window.transLobIDLineEdit,
                         window.transDownButton,
                         window.transViewButton,
                         window.transPathLineEdit
                         )

def upload_shield_contract_file():
    window = gw["add_sale_contract_window"]
    file_path, file_id = select_and_save_file()
    set_file_button_text(file_path, file_id,
                         window.shieldLobIDLineEdit,
                         window.shieldDownButton,
                         window.shieldViewButton,
                         window.shieldPathLineEdit
                         )

def upload_desk_contract_file():
    window = gw["add_sale_contract_window"]
    file_path, file_id = select_and_save_file()
    set_file_button_text(file_path, file_id,
                         window.deskLobIDLineEdit,
                         window.deskDownButton,
                         window.deskViewButton,
                         window.deskPathLineEdit
                         )

def upload_computer_contract_file():
    window = gw["add_sale_contract_window"]
    file_path, file_id = select_and_save_file()
    set_file_button_text(file_path, file_id,
                         window.compLobIDLineEdit,
                         window.compDownButton,
                         window.compViewButton,
                         window.compPathLineEdit
                         )

def upload_other_contract_file():
    window = gw["add_sale_contract_window"]
    file_path, file_id = select_and_save_file()
    set_file_button_text(file_path, file_id,
                         window.otherLobIDLineEdit,
                         window.otherDownButton,
                         window.otherViewButton,
                         window.otherPathLineEdit
                         )

def open_contract_file(file_path):
    if file_path and os.path.isfile(file_path):
        cmd = f"start {file_path}"
        subprocess.Popen(cmd, shell=True)
    else:
        QMessageBox.warning(None, "错误", "文件不存在，请先下载")

def view_contract_file():
    window = gw["add_sale_contract_window"]
    file_path = window.filepathLineEdit.text()
    open_contract_file(file_path)

def view_emi_contract_file():
    window = gw["add_sale_contract_window"]
    file_path = window.emiPathLineEdit.text()
    open_contract_file(file_path)

def view_ems_contract_file():
    window = gw["add_sale_contract_window"]
    file_path = window.emsPathLineEdit.text()
    open_contract_file(file_path)

def view_trans_contract_file():
    window = gw["add_sale_contract_window"]
    file_path = window.transPathLineEdit.text()
    open_contract_file(file_path)

def view_shield_contract_file():
    window = gw["add_sale_contract_window"]
    file_path = window.shieldPathLineEdit.text()
    open_contract_file(file_path)

def view_desk_contract_file():
    window = gw["add_sale_contract_window"]
    file_path = window.deskPathLineEdit.text()
    open_contract_file(file_path)

def view_computer_contract_file():
    window = gw["add_sale_contract_window"]
    file_path = window.compPathLineEdit.text()
    open_contract_file(file_path)

def view_other_contract_file():
    window = gw["add_sale_contract_window"]
    file_path = window.otherPathLineEdit.text()
    open_contract_file(file_path)