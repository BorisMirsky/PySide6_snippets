import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import pandas as pd



class PandasModelEditable(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])

            column_count = self.columnCount()
            for column in range(0, column_count):
                if (index.column() == column and role == Qt.TextAlignmentRole):
                    return Qt.AlignHCenter | Qt.AlignVCenter

        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def setData(self, index, value, role):
        if not value.isdigit():  # +++
            return False  # +++

        if not index.isValid():
            return False

        if role != Qt.EditRole:
            return False

        row = index.row()
        if row < 0 or row >= len(self._data.values):
            return False

        column = index.column()
        if column < 0 or column >= self._data.columns.size:
            return False

        self._data.values[row][column] = value

        self._data.values[row][1] = int(value) ** 2  # +++
        self._data.values[row][2] = int(value) ** 3  # +++

        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        fl = QAbstractTableModel.flags(self, index)  # +++
        if index.column() == 0:  # +++
            fl |= Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable  # +++
        return fl  # +++


if __name__ == '__main__':
    df = pd.DataFrame({'x': range(5),
                       'x²': [i ** 2 for i in range(5)],
                       'x³': [i ** 3 for i in range(5)]
                       })

    app = QApplication(sys.argv)
    model = PandasModelEditable(df)
    view = QTableView()
    view.setModel(model)
    view.resize(350, 200)
    view.show()
    sys.exit(app.exec())