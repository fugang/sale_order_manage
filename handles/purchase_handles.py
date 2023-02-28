
from globals import gw, config, logger
from .common_handles import render_sale_contract_table, \
    fresh_add_sale_contract_by_contract_no
from models.data_operation import list_supply, save_payout_data
from models.data_operation import save_purchase_data, update_purchase_data, \
    upsert_supply_data, list_product_type, save_recv_invoice
from exceptions import ValueTypeErrException
from utils import check_float, show_success_message, show_failed_message
from .common_handles import render_purchase_table_data
from .cash_handles import add_payout_handle


def add_purchase_handle():
    pass


def get_current_sale_contract_data():
    window = gw["main_window"]
    table_view = window.saleContractTableView
    index = table_view.currentIndex()
    row = index.row()
    if row == -1:
        return []
    else:
        data = table_view.model().get_row_dict(row)
        return data


def get_current_purchase_cell():
    window = gw["view_purchase_window"]
    table_view = window.purchaseTableView
    index = table_view.currentIndex()
    row = index.row()
    row_data = table_view.model().get_row_data(row)
    column = index.column()
    keys = list(config["purchase_contract"].keys())
    field = keys[column]
    value = row_data[column]
    return field, value


def init_supply_combox():
    window = gw["view_purchase_window"]
    window.saleContractLineEdit.setText("")
    window.supplyCombox.clear()
    window.supplyCombox.addItem("")
    for supply in list_supply():
        window.supplyCombox.addItem(supply)


def update_combox():
    window = gw["view_purchase_window"]
    if window.monthCombox.model().rowCount() == 0:
        window.monthCombox.addItems(["1月", "2月", "3月", "4月",
                                     "5月", "6月", "7月", "8月",
                                     "9月", "10月", "11月", "12月"
                                     ])
        window.monthCombox.setCurrentText("")
    window.productCombox.clear()
    product_list = list_product_type()
    if "" not in product_list:
        product_list.append("")
    product_list.sort()
    window.productCombox.addItems(product_list)


def view_purchase_handle():
    window = gw["view_purchase_window"]
    update_combox()
    init_supply_combox()
    render_purchase_table_data()
    window.show()


def view_purchase_by_sale_contract():
    pass


def get_current_purchase_data():
    window = gw["view_purchase_window"]
    table_view = window.purchaseTableView
    index = table_view.currentIndex()
    row = index.row()
    if row == -1:
        return -1
    else:
        data = table_view.model().get_row_dict(row)
        return data


def modify_purchase_handle():
    pass


def purchase_table_click_handle():
    field, value = get_current_purchase_cell()
    if field in ["id", "supply", "contract_no", "sale_contract_no",
                 "item", "product_type", "count", "date",
                 "amount", "mark",
                 ]:
        modify_purchase_handle()
    else:
        add_payout_handle()


def filter_emi_data():
    window = gw["add_sale_contract_window"]
    sale_id = int(window.idLineEdit.text())
    if not sale_id:
        raise ValueTypeErrException("没有绑定销售合同")
    purchase_no = window.emiSerialLineEdit.text()
    if not purchase_no:
        raise ValueTypeErrException("合同编号错误")
    emi_cost = window.emiCostLineEdit.text()
    emi_cost = check_float(emi_cost)
    if not emi_cost:
        raise ValueTypeErrException("EMI采购金额错误")
    emi_supply = window.emiSupplyCombo.currentText()
    if not emi_supply:
        raise ValueTypeErrException("EMI设备供应商错误")
    emi_date = window.emiDateEdit.date().toPython()
    emi_item = window.emiItemLineEdit.text()
    emi_product_type = window.emiProductLineEdit.text()
    emi_count = window.emiCountLineEdit.text()
    emi_mark = window.emiMarkLineEdit.text()
    emi_file_path = window.emiPathLineEdit.text()
    emi_lob_id = window.emiLobIDLineEdit.text()
    if emi_lob_id:
        emi_lob_id = int(emi_lob_id)
    emi_purchase = {"supply": emi_supply,
                    "item": emi_item,
                    "product_type": emi_product_type,
                    "sale_id": sale_id,
                    "purchase_no": purchase_no,
                    "count": emi_count,
                    "amount": emi_cost,
                    "mark": emi_mark,
                    "date": emi_date,
                    "file_path": emi_file_path,
                    "lob_id": emi_lob_id
                    }
    return emi_purchase


def filter_ems_data():
    window = gw["add_sale_contract_window"]
    sale_id = int(window.idLineEdit.text())
    if not sale_id:
        raise ValueTypeErrException("没有管理销售合同")
    purchase_no = window.emsSerialLineEdit.text()
    if not purchase_no:
        raise ValueTypeErrException("合同编号错误")
    ems_cost = window.emsCostLineEdit.text()
    ems_cost = check_float(ems_cost)
    if not ems_cost:
        raise ValueTypeErrException("EMS采购金额错误")
    ems_supply = window.emsSupplyCombo.currentText()
    if not ems_supply:
        raise ValueTypeErrException("EMS供应商错误")
    ems_date = window.emsDateEdit.date().toPython()
    ems_item = window.emsItemLineEdit.text()
    ems_product_type = window.emsProductLineEdit.text()
    ems_count = window.emsCountLineEdit.text()
    ems_mark = window.emsMarkLineEdit.text()
    ems_file_path = window.emsPathLineEdit.text()
    ems_lob_id = window.emsLobIDLineEdit.text()
    if ems_lob_id:
        ems_lob_id = int(ems_lob_id)
    ems_purchase = {"supply": ems_supply,
                    "item": ems_item,
                    "product_type": ems_product_type,
                    "count": ems_count,
                    "amount": ems_cost,
                    "mark": ems_mark,
                    "sale_id": sale_id,
                    "purchase_no": purchase_no,
                    "date": ems_date,
                    "file_path": ems_file_path,
                    "lob_id": ems_lob_id,
                    }
    return ems_purchase


def save_purchase_ems_handle():
    window = gw["add_sale_contract_window"]
    status_bar = window.addPerfStatusbar
    try:
        purchase_ems = filter_ems_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    supply_data = {"company": purchase_ems["supply"],
                   "items": "EMS"}
    try:
        upsert_supply_data(supply_data)
    except Exception as exc:
        logger.error("upsert supply error. %s", exc)
        show_failed_message(status_bar, "保存EMS供应商失败")
        return
    id = window.emsIDLineEdit.text()
    if id:
        id = int(id)
        update_purchase_data(id, purchase_ems)
        show_success_message(status_bar, "保存EMS订单成功")
    else:
        try:
            purchase_model = save_purchase_data(purchase_ems)
        except Exception as exc:
            logger.error("save purchase error. %s", exc)
            show_failed_message(status_bar, f"保存EMS订单错误. {exc}")
            return
        paid_amount = window.emsPaidamountLineEdit.text()
        try:
            save_purchase_payout_data(paid_amount, purchase_model)
        except ValueTypeErrException as exc:
            show_failed_message(status_bar, str(exc))
            return
        except Exception as exc:
            logger.error("save purchase payout error. %s", exc)
            show_failed_message(status_bar, str(exc))
            return
        invoice_amount = window.emsInvoiceLineEdit.text()
        invoice_amount = check_float(invoice_amount)
        invoice_date = window.emsInvoiceDateEdit.date().toPython()
        if invoice_amount is False:
            show_failed_message(status_bar, "收票金额错误")
            return
        if invoice_amount:
            invoice_data = {"amount": invoice_amount, "purchase_id": purchase_model.id,
                            "sale_id": purchase_model.sale_id,
                            "company": purchase_model.company,
                            "date": invoice_date}
            try:
                save_recv_invoice(invoice_data)
            except Exception as exc:
                show_failed_message(status_bar, str(exc))
                return
        show_success_message(status_bar, "新建EMS订单成功")
    render_sale_contract_table()
    render_purchase_table_data()
    fresh_add_sale_contract_by_contract_no(purchase_ems["sale_no"])


def save_purchase_emi_handle():
    window = gw["add_sale_contract_window"]
    status_bar = window.addPerfStatusbar
    try:
        purchase_emi = filter_emi_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    supply_data = {"company": purchase_emi["supply"],
                   "items": "EMI"}
    try:
        upsert_supply_data(supply_data)
    except Exception as exc:
        logger.error("upsert supply error. %s", exc)
        show_failed_message(status_bar, "保存EMI订单失败")
        return
    id = window.emiIDLineEdit.text()
    if id:
        id = int(id)
        update_purchase_data(id, purchase_emi)
        show_success_message(status_bar, "保存EMI订单成功")
    else:
        try:
            purchase_model = save_purchase_data(purchase_emi)
        except Exception as exc:
            show_failed_message(status_bar, str(exc))
            return
        paid_amount = window.emiPaidAmountLineEdit.text()
        try:
            save_purchase_payout_data(paid_amount, purchase_model)
        except ValueTypeErrException as exc:
            show_failed_message(status_bar, str(exc))
            return
        except Exception as exc:
            logger.error("save purchase payout error. %s", exc)
            logger.exception(exc)
            show_failed_message(status_bar, str(exc))
            return
        invoice_amount = window.emiInvoiceLineEdit.text()
        invoice_amount = check_float(invoice_amount)
        invoice_date = window.emiInvoiceDateEdit.date().toPython()
        if invoice_amount is False:
            show_failed_message(status_bar, "EMI收票金额错误")
            return
        if invoice_amount:
            invoice_data = {"amount": invoice_amount, "purchase_id": purchase_model.id,
                            "sale_id": purchase_model.sale_id,
                            "date": invoice_date, "company": purchase_model.supply}
            try:
                save_recv_invoice(invoice_data)
            except Exception as exc:
                show_failed_message(status_bar, str(exc))
                return
        show_success_message(status_bar, "新建EMI订单成功")
    render_sale_contract_table()
    render_purchase_table_data()
    fresh_add_sale_contract_by_contract_no(purchase_emi["sale_no"])


def filter_vol_trans_data():
    window = gw["add_sale_contract_window"]
    sale_id = int(window.idLineEdit.text())
    if not sale_id:
        raise ValueTypeErrException("没有关联销售合同")
    contract_no = window.transSerialLineEdit.text()
    if not contract_no:
        raise ValueTypeErrException("合同编号错误")
    vol_trans_cost = window.voltransCostLineEdit.text()
    vol_trans_cost = check_float(vol_trans_cost)
    if not vol_trans_cost:
        raise ValueTypeErrException("隔离变压器采购金额错误")
    vol_trans_supply = window.voltransSupplyCombo.currentText()
    if vol_trans_cost != 0 and not vol_trans_supply:
        raise ValueTypeErrException("隔离变压器供应商错误")
    trans_date = window.transDateEdit.date().toPython()
    vol_trans_product_type = window.voltransProductLineEdit.text()
    vol_trans_item = window.voltransItemLineEdit.text()
    vol_trans_count = window.voltransCountLineEdit.text()
    vol_trans_mark = window.voltransMarkLineEdit.text()
    trans_file_path = window.transPathLineEdit.text()
    trans_file_id = window.transLobIDLineEdit.text()
    if trans_file_id:
        trans_file_id = int(trans_file_id)
    vol_trans_purchase = {"supply": vol_trans_supply,
                          "item": vol_trans_item,
                          "product_type": vol_trans_product_type,
                          "count": vol_trans_count,
                          "amount": vol_trans_cost,
                          "mark": vol_trans_mark,
                          "sale_id": sale_id,
                          "purchase_no": contract_no,
                          "date": trans_date,
                          "file_path": trans_file_path,
                          "lob_id": trans_file_id,
                          }
    return vol_trans_purchase


def save_purchase_trans_handle():
    window = gw["add_sale_contract_window"]
    status_bar = window.addPerfStatusbar
    try:
        purchase_trans = filter_vol_trans_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    supply_data = {"company": purchase_trans["supply"],
                   "items": "隔离变压器"}
    try:
        upsert_supply_data(supply_data)
    except Exception as exc:
        logger.error("upsert supply error. %s", exc)
        show_failed_message(status_bar, "保存隔离变压器供应商失败")
        return
    id = window.voltransIDLineEdit.text()
    if id:
        id = int(id)
        update_purchase_data(id, purchase_trans)
        show_success_message(status_bar, "保存隔离变压器订单成功")
    else:
        try:
            purchase_model = save_purchase_data(purchase_trans)
        except Exception as exc:
            show_failed_message(status_bar, f"新建隔离变压器订单失败. {exc}")
            return
        paid_amount = window.transPaidAmountLineEdit.text()
        try:
            save_purchase_payout_data(paid_amount, purchase_model)
        except ValueTypeErrException as exc:
            show_failed_message(status_bar, str(exc))
            return
        except Exception as exc:
            logger.error("save purchase payout error. %s", exc)
            show_failed_message(status_bar, str(exc))
        invoice_amount = window.transInvoiceLineEdit.text()
        invoice_amount = check_float(invoice_amount)
        if invoice_amount is False:
            show_failed_message(status_bar, "开票金额错误")
            return
        invoice_date = window.transInvoiceDateEdit.date().toPython()
        if invoice_amount:
            invoice_data = {"amount": invoice_amount, "purchase_id": purchase_model.id,
                            "sale_id": purchase_model.sale_id,
                            "company": purchase_model.supply,
                            "date": invoice_date}
            try:
                save_recv_invoice(invoice_data)
            except Exception as exc:
                show_failed_message(status_bar, str(exc))
                return
        show_success_message(status_bar, "新建隔离变压器订单成功")
    render_sale_contract_table()
    render_purchase_table_data()
    fresh_add_sale_contract_by_contract_no(purchase_trans["sale_no"])


def filter_shield_data():
    window = gw["add_sale_contract_window"]
    sale_id = int(window.idLineEdit.text())
    if not sale_id:
        raise ValueTypeErrException("没有关联销售合同")
    contract_no = window.shiedSerialLineEdit.text()
    if not contract_no:
        raise ValueTypeErrException("合同编号错误")
    shield_cost = window.shieldCostLineEdit.text()
    shield_cost = check_float(shield_cost)
    if not shield_cost:
        raise ValueTypeErrException("屏蔽房采购金额错误")
    shield_supply = window.shieldSupplyCombo.currentText()
    if shield_cost != 0 and not shield_supply:
        raise ValueTypeErrException("屏蔽房供应商错误")
    shield_date = window.shieldDateEdit.date().toPython()
    shield_item = window.shieldItemLineEdit.text()
    shield_product_type = window.shieldProductLineEdit.text()
    shield_count = window.shieldCountLineEdit.text()
    shield_mark = window.shieldMarkLineEdit.text()
    shield_file_path = window.shieldPathLineEdit.text()
    shield_file_id = window.shieldLobIDLineEdit.text()
    if shield_file_id:
        shield_file_id = int(shield_file_id)
    shield_purchase = {"supply": shield_supply,
                       "item": shield_item,
                       "product_type": shield_product_type,
                       "count": shield_count,
                       "amount": shield_cost,
                       "mark": shield_mark,
                       "purchase_no": contract_no,
                       "sale_id": sale_id,
                       "date": shield_date,
                       "file_path": shield_file_path,
                       "lob_id": shield_file_id,
                       }
    return shield_purchase


def save_purchase_shield_handle():
    window = gw["add_sale_contract_window"]
    status_bar = window.addPerfStatusbar
    try:
        purchase_shield = filter_shield_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    supply_data = {"company": purchase_shield["supply"],
                   "items": "屏蔽房"}
    try:
        upsert_supply_data(supply_data)
    except Exception as exc:
        logger.error("upsert supply error. %s", exc)
        show_failed_message(status_bar, "保存屏蔽房供应商失败")
        return
    id = window.shieldIDLineEdit.text()
    if id:
        id = int(id)
        update_purchase_data(id, purchase_shield)
        show_success_message(status_bar, "保存屏蔽房订单成功")
    else:
        try:
            purchase_model = save_purchase_data(purchase_shield)
        except Exception as exc:
            show_failed_message(status_bar, f"新建屏蔽房订单错误. {exc}")
            return
        paid_amount = window.shieldPaidAmountLineEdit.text()
        try:
            save_purchase_payout_data(paid_amount, purchase_model)
        except ValueTypeErrException as exc:
            show_failed_message(status_bar, str(exc))
            return
        except Exception as exc:
            logger.error("save purchase payout error. %s", exc)
            show_failed_message(status_bar, str(exc))
            return
        invoice_amount = window.shieldInvoiceLineEdit.text()
        invoice_amount = check_float(invoice_amount)
        if invoice_amount is False:
            show_failed_message(status_bar, "收票金额错误")
            return
        invoice_date = window.shieldInvoiceDateEdit.date().toPython()
        if invoice_amount:
            invoice_data = {"amount": invoice_amount, "purchase_id": purchase_model.id,
                            "sale_id": purchase_model.sale_id,
                            "company": purchase_model.supply,
                            "date": invoice_date}
            try:
                save_recv_invoice(invoice_data)
            except Exception as exc:
                show_failed_message(status_bar, str(exc))
                return
        show_success_message(status_bar, "新建屏蔽房订单成功")
    render_sale_contract_table()
    render_purchase_table_data()
    fresh_add_sale_contract_by_contract_no(purchase_shield["sale_no"])


def filter_computer_data():
    window = gw["add_sale_contract_window"]
    sale_id = int(window.idLineEdit.text())
    if not sale_id:
        raise ValueTypeErrException("没有关联销售合同")
    contract_no = window.computerSerialLineEdit.text()
    computer_cost = window.computerCostLineEdit.text()
    computer_cost = check_float(computer_cost)
    if not computer_cost:
        raise ValueTypeErrException("电脑采购金额错误")
    computer_supply = window.computerSupplyCombo.currentText()
    if computer_cost != 0 and not computer_supply:
        raise ValueTypeErrException("电脑供应商错误")
    computer_prudoct_type = window.computerProductLineEdit.text()
    computer_item = window.computerItemLineEdit.text()
    computer_count = window.computerCountLineEdit.text()
    computer_mark = window.computerMarkLineEdit.text()
    computer_date = window.computerDateEdit.date().toPython()
    computer_file_path = window.compPathLineEdit.text()
    computer_file_id = window.compLobIDLineEdit.text()
    if computer_file_id:
        computer_file_id = int(computer_file_id)
    computer_purchase = {"supply": computer_supply,
                         "item": computer_item,
                         "product_type": computer_prudoct_type,
                         "count": computer_count,
                         "amount": computer_cost,
                         "mark": computer_mark,
                         "purchase_no": contract_no,
                         "sale_id": sale_id,
                         "date": computer_date,
                         "file_path": computer_file_path,
                         "lob_id": computer_file_id,
                         }
    return computer_purchase


def save_purchase_computer_handle():
    window = gw["add_sale_contract_window"]
    status_bar = window.addPerfStatusbar
    try:
        purchase_computer = filter_computer_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    supply_data = {"company": purchase_computer["supply"],
                   "items": "电脑"}
    try:
        upsert_supply_data(supply_data)
    except Exception as exc:
        logger.error("upsert supply error. %s", exc)
        show_failed_message(status_bar, "保存电脑供应商失败")
        return
    id = window.computerIDLineEdit.text()
    if id:
        id = int(id)
        update_purchase_data(id, purchase_computer)
        show_success_message(status_bar, "保存电脑订单成功")
    else:
        try:
            purchase_model = save_purchase_data(purchase_computer)
        except Exception:
            show_failed_message(status_bar, "新建电脑订单错误")
            return
        paid_amount = window.computerPaidAmountLineEdit.text()
        try:
            save_purchase_payout_data(paid_amount, purchase_model)
        except ValueTypeErrException as exc:
            show_failed_message(status_bar, str(exc))
            return
        except Exception as exc:
            logger.error("save purchase payout error. %s", exc)
            show_failed_message(status_bar, str(exc))
            return
        invoice_amount = window.compInvoiceLineEdit.text()
        invoice_amount = check_float(invoice_amount)
        if invoice_amount is False:
            show_failed_message(status_bar, "收票金额错误")
            return
        invoice_date = window.compInvoiceDateEdit.date().toPython()
        if invoice_amount:
            invoice_data = {"amount": invoice_amount, "purchase_id": purchase_model.id,
                            "sale_id": purchase_model.sale_id,
                            "company": purchase_model.company,
                            "date": invoice_date}
            try:
                save_recv_invoice(invoice_data)
            except Exception as exc:
                show_failed_message(status_bar, str(exc))
                return
        show_success_message(status_bar, "新建电脑订单成功")
    render_sale_contract_table()
    render_purchase_table_data()
    fresh_add_sale_contract_by_contract_no(purchase_computer["sale_no"])


def filter_env_desk_data():
    window = gw["add_sale_contract_window"]
    sale_id = int(window.idLineEdit.text())
    if not sale_id:
        raise ValueTypeErrException("没有关联销售合同")
    contract_no = window.deskSerialLineEdit.text()
    desk_cost = window.deskCostLineEdit.text()
    desk_cost = check_float(desk_cost)
    if not desk_cost:
        raise ValueTypeErrException("环境和桌子采购金额错误")
    desk_supply = window.deskSupplyCombo.currentText()
    if desk_cost != 0 and not desk_supply:
        raise ValueTypeErrException("环境和桌子供应商错误")
    desk_item = window.deskItemLineEdit.text()
    desk_product_type = window.deskProductLineEdit.text()
    desk_count = window.deskCountLineEdit.text()
    desk_mark = window.deskMarkLineEdit.text()
    desk_date = window.deskDateEdit.date().toPython()
    desk_file_path = window.deskPathLineEdit.text()
    desk_file_id = window.deskLobIDLineEdit.text()
    if desk_file_id:
        desk_file_id = int(desk_file_id)
    desk_purchase = {"supply": desk_supply,
                     "item": desk_item,
                     "product_type": desk_product_type,
                     "count": desk_count,
                     "amount": desk_cost,
                     "mark": desk_mark,
                     "sale_id": sale_id,
                     "purchase_no": contract_no,
                     "date": desk_date,
                     "file_path": desk_file_path,
                     "lob_id": desk_file_id,
                     }
    return desk_purchase


def save_purchase_desk_handle():
    window = gw["add_sale_contract_window"]
    status_bar = window.addPerfStatusbar
    try:
        purchase_desk = filter_env_desk_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    supply_data = {"company": purchase_desk["supply"],
                   "items": "环境和桌子"}
    try:
        upsert_supply_data(supply_data)
    except Exception as exc:
        logger.error("upsert supply error. %s", exc)
        show_failed_message(status_bar, "保存环境和桌子供应商失败")
        return
    id = window.deskIDLineEdit.text()
    if id:
        id = int(id)
        update_purchase_data(id, purchase_desk)
        show_success_message(status_bar, "保存环境桌子订单成功")
    else:
        try:
            purchase_model = save_purchase_data(purchase_desk)
        except Exception:
            show_failed_message(status_bar, "新建环境桌子订单错误")
            return
        paid_amount = window.deskPaidAmountLineEdit.text()
        try:
            save_purchase_payout_data(paid_amount, purchase_model)
        except ValueTypeErrException as exc:
            show_failed_message(status_bar, str(exc))
            return
        except Exception as exc:
            logger.error("save purchase payout error. %s", exc)
            show_failed_message(status_bar, str(exc))
            return
        invoice_amount = window.deskInvoiceAmtLineEdit.text()
        invoice_amount = check_float(invoice_amount)
        if invoice_amount is False:
            show_failed_message(status_bar, "收票金额错误")
            return
        invoice_date = window.deskInvoiceDateEdit.date().toPython()
        if invoice_amount:
            invoice_data = {"amount": invoice_amount, "purchase_id": purchase_model.id,
                            "sale_id": purchase_model.sale_id,
                            "company": purchase_model.supply,
                            "date": invoice_date}
            try:
                save_recv_invoice(invoice_data)
            except Exception as exc:
                show_failed_message(status_bar, str(exc))
                return
        show_success_message(status_bar, "新建环境桌子订单成功")
    render_sale_contract_table()
    render_purchase_table_data()
    fresh_add_sale_contract_by_contract_no(purchase_desk["sale_no"])


def filter_other_data():
    window = gw["add_sale_contract_window"]
    sale_id = int(window.idLineEdit.text())
    if not sale_id:
        raise ValueTypeErrException("没有关联销售合同")
    contract_no = window.otherSerialLineEdit.text()
    other_cost = window.otherCostLineEdit.text()
    other_cost = check_float(other_cost)
    if not other_cost:
        raise ValueTypeErrException("其他项采购金额错误")
    other_supply = window.otherSupplyCombo.currentText()
    if other_cost != 0 and not other_supply:
        raise ValueTypeErrException("其他支出供应商错误")
    other_item = window.otherItemLineEdit.text()
    other_product_type = window.otherProductLineEdit.text()
    other_count = window.otherCountLineEdit.text()
    other_mark = window.otherMarkLineEdit.text()
    other_date = window.otherDateEdit.date().toPython()
    other_file_path = window.otherPathLineEdit.text()
    other_file_id = window.otherLobIDLineEdit.text()
    if other_file_id:
        other_file_id = int(other_file_id)
    other_purchase = {"supply": other_supply,
                      "item": other_item,
                      "product_type": other_product_type,
                      "count": other_count,
                      "amount": other_cost,
                      "mark": other_mark,
                      "purchase_no": contract_no,
                      "sale_id": sale_id,
                      "date": other_date,
                      "file_path": other_file_path,
                      "lob_id": other_file_id,
                      }
    return other_purchase


def save_purchase_other_handle():
    window = gw["add_sale_contract_window"]
    status_bar = window.addPerfStatusbar
    try:
        purchase_other = filter_other_data()
    except ValueTypeErrException as exc:
        show_failed_message(status_bar, str(exc))
        return
    supply_data = {"company": purchase_other["supply"],
                   "items": "其他"}
    try:
        upsert_supply_data(supply_data)
    except Exception as exc:
        logger.error("upsert supply error. %s", exc)
        show_failed_message(status_bar, "保存其他支出供应商失败")
        return
    id = window.otherIDLineEdit.text()
    if id:
        id = int(id)
        update_purchase_data(id, purchase_other)
        show_success_message(status_bar, "保存其他支出成功")
    else:
        try:
            purchase_model = save_purchase_data(purchase_other)
        except:
            show_failed_message(status_bar, "新建其他支出错误")
            return
        paid_amount = window.otherPaidAmountLineEdit.text()
        try:
            save_purchase_payout_data(paid_amount, purchase_model)
        except ValueTypeErrException as exc:
            show_failed_message(status_bar, str(exc))
            return
        except Exception as exc:
            logger.error("save purchase payout error. %s", exc)
            show_failed_message(status_bar, str(exc))
            return
        invoice_amount = window.otherInvioceLineEdit.text()
        invoice_amount = check_float(invoice_amount)
        if invoice_amount is False:
            show_failed_message(status_bar, "出票金额错误")
            return
        invoice_date = window.otherInvoiceDateEdit.date().toPython()
        if invoice_amount:
            invoice_data = {"amount": invoice_amount, "purchase_id": purchase_model.id,
                            "sale_id": purchase_model.sale_id,
                            "company": purchase_model.company,
                            "date": invoice_date}
            try:
                save_recv_invoice(invoice_data)
            except Exception as exc:
                show_failed_message(status_bar, str(exc))
                return
        show_success_message(status_bar, "新建其他支出成功")
    render_sale_contract_table()
    render_purchase_table_data()
    fresh_add_sale_contract_by_contract_no(purchase_other["sale_no"])


def save_purchase_payout_data(paid_amount, purchase_model):
    paid_amount = check_float(paid_amount)
    if paid_amount is False:
        raise ValueTypeErrException("付款金额错误")
    date = purchase_model.date
    sale_id = purchase_model.sale_id
    purchase_id = purchase_model.id
    if paid_amount:
        payout_data = {"amount": paid_amount, "date": date, "sale_id": sale_id,
                       "purchase_id": purchase_id}
        save_payout_data(payout_data)


def save_purchase_data_in_tab():
    window = gw["add_sale_contract_window"]
    index = window.saleTabWidget.currentIndex()
    tab_name = window.saleTabWidget.tabText(index)
    if tab_name == "EMI":
        save_purchase_emi_handle()
    elif tab_name == "EMS":
        save_purchase_ems_handle()
    elif tab_name == "隔离变压器":
        save_purchase_trans_handle()
    elif tab_name == "屏蔽房":
        save_purchase_shield_handle()
    elif tab_name == "环境和桌子":
        save_purchase_desk_handle()
    elif tab_name == "电脑":
        save_purchase_computer_handle()
    elif tab_name == "其他":
        save_purchase_other_handle()
