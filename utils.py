from sqlalchemy import inspect
import datetime
from PySide6.QtCore import QDate


def comma_format(integer):
    return f"{integer:,}"


def check_integer(data):
    if not data:
        data = 0
    data = str(data)
    data = data.replace(",", "")
    try:
        data = int(data)
    except ValueError:
        return False
    return data


def check_float(data):
    if not data:
        return None
    data = str(data)
    data = data.replace(",", "")
    try:
        data = float(data)
    except ValueError:
        return False
    return data


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


def reverse_dict(data):
    new_dict = {}
    for key, value in data.items():
        new_dict[value] = key
    return new_dict


def show_success_message(status_bar, message):
    status_bar.setStyleSheet("color: green;font-size: 15px;")
    status_bar.showMessage(message)


def show_failed_message(status_bar, message):
    status_bar.setStyleSheet("color: red;font-size: 15px;")
    status_bar.showMessage(message)


def show_window(window, status_bar):
    window.activateWindow()
    status_bar.showMessage("")
    window.show()


def amount_str_to_float(amount):
    amount = amount.replace(",", "")
    amount = float(amount)
    return amount


def set_date(qdate, date=None):
    if not date:
        date = datetime.datetime.now()
    qdate.setDate(QDate(date.year, date.month, date.day))
