import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import pandas as pd


df = pd.DataFrame({'x': range(5),
                   'x²': [i ** 2 for i in range(5)],
                   'x³': [i ** 3 for i in range(5)]
                   })



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
        if not value.isdigit():  # только числа
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

class Main(QWidget):
    def __init__(self):
        super().__init__()
        model = PandasModelEditable(df)
        view = QTableView()
        view.setModel(model)
        edit_cell_button = QPushButton('allow to edit')
        edit_cell_button.clicked.connect(self.handle_edit_cell_button)
        disable_access_table_button = QPushButton('deny to edit')
        disable_access_table_button.clicked.connect(self.handle_disable_access_table_button)
        vbox = QVBoxLayout()
        vbox.addWidget(view)
        vbox.addWidget(edit_cell_button)
        vbox.addWidget(disable_access_table_button)
        self.setLayout(vbox)

    def handle_edit_cell_button(self):
        print('edit')

    def handle_disable_access_table_button(self):
        print('deny')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())