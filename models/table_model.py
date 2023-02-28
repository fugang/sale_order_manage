from PySide6.QtCore import QAbstractTableModel, Qt
import datetime


class TableModel(QAbstractTableModel):
    def __init__(self, data, column_name, column_params):
        super(TableModel, self).__init__()
        self._data = data
        self._column_name = column_name
        self._column_param = column_params

    def data(self, index, role):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                data = self._data[index.row()][index.column()]
                if isinstance(data, datetime.date):
                    data = data.strftime("%Y/%m/%d")
                elif isinstance(data, int) or isinstance(data, float):
                    data = f"{data:,}"
                return data

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        if not self._data:
            return 0
        else:
            return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._column_name[section])
            if orientation == Qt.Vertical:
                return ""

    def get_row_id(self, row):
        return self._data[row][0]

    def get_row_data(self, row):
        row_data = self._data[row]
        return row_data

    def get_row_dict(self, row):
        row_data = self.get_row_data(row)
        row_dict = {}
        for index, key in enumerate(self._column_param):
            row_dict[key] = row_data[index]
        return row_dict


class StaticTableModel(QAbstractTableModel):
    def __init__(self, data, column_name, column_params):
        super(StaticTableModel, self).__init__()
        self._data = data
        self._column_name = column_name
        self._column_param = column_params

    def data(self, index, role):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                row_data = self._data[index.row()]
                column = index.column()
                param = self._column_param[column]
                data = row_data.get(param, "")
                if isinstance(data, datetime.date):
                    data = data.strftime("%Y/%m/%d")
                elif isinstance(data, int) or isinstance(data, float):
                    data = f"{data:,}"
                return data

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._column_name)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._column_name[section])
            if orientation == Qt.Vertical:
                return ""

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            column = index.column()
            param = self._column_param[column]
            self._data[index.row()][param] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def get_row_data(self, index):
        return self._data[index.row()]


class ModifyTableModel(QAbstractTableModel):
    def __init__(self, data, column_name, column_params):
        super(ModifyTableModel, self).__init__()
        self._data = data
        self._column_name = column_name
        self._column_param = column_params

    def data(self, index, role):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                row_data = self._data[index.row()]
                column = index.column()
                param = self._column_param[column]
                data = row_data.get(param, "")
                return data

    def flags(self, index):
        if index.column() != 0:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._column_name)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._column_name[section])
            if orientation == Qt.Vertical:
                return ""

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            column = index.column()
            param = self._column_param[column]
            self._data[index.row()][param] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def get_row_data(self, index):
        return self._data[index.row()]


class ItemModifyTableModel(ModifyTableModel):
    def __init__(self, data, column_name, column_params):
        super(ItemModifyTableModel, self).__init__(data, column_name, column_params)

    def flags(self, index):
        if index.column() not in [0, 1]:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
