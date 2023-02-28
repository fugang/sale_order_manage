import openpyxl
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMessageBox

from .common_handles import get_purchase_table_data, render_sale_table_data
from globals import config, gw, logger


def render_sale_data(sheet):
    headers = list(config["sale_contract"].values())
    sheet.append(headers)
    sale_list = render_sale_table_data()
    for sale in sale_list:
        sheet.append(sale)

def render_purchase_data(sheet):
    headers = list(config["purchase_contract"].values())
    sheet.append(headers)
    purchase_list = get_purchase_table_data()
    for purchase in purchase_list:
        sheet.append(purchase)


def export_excel_handle():
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.AnyFile)
    file_list = dialog.getSaveFileName(None, "保存报表", "报表", "*.xlsx")
    filename = file_list[0]
    if not filename:
        return
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "销售合同列表"
    render_sale_data(sheet)
    sheet2 = wb.create_sheet(index = 1 , title = "采购合同列表")
    render_purchase_data(sheet2)
    try:
        wb.save(filename)
    except PermissionError:
        QMessageBox.warning(None, "错误", "检查文件是否已打开")
        return
    except Exception as exc:
        logger.error("export xlsx error. %s", exc)
        QMessageBox.warning(None, "错误", "保存错误")
        return
    QMessageBox.information(None, "成功", "导出成功")


def about_handle():
    window = gw["about_window"]
    window.setWindowTitle("关于")
    window.show()
