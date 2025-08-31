import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import pandas as pd



table_data = [['parameter 1', '111', '222'],
            ['parameter 2', '333', '444'],
            ['parameter 3', '555', '666'],
            ['parameter 4', '777', '888']]


class PandasModel(QAbstractTableModel):
    def __init__(self, table, c, r):
        QAbstractTableModel.__init__(self)
        data =  pd.DataFrame(table)
        self._data = data
        self.c = c
        self.r = r
    def rowCount(self, parent=None):
        return self._data.shape[0]
    def columnCount(self, parnet=None):
        return self._data.shape[1]
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None
    def flags(self, index):
        fl = QAbstractTableModel.flags(self, index)  # +++
        if index.column() == self.c and index.row() == self.r:  # +++
            fl |= Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable  # +++
        return fl  # +++


class MyTable(QTableView):
    def __init__(self, model:QAbstractTableModel, data, c, r, parent=None):
        super().__init__(parent)
        self.data = data
        self.model = model
        self.horizontalHeader().setVisible(True)
        self.model = model(pd.DataFrame(data, columns=['Parameters', 'Existing', 'Acceptable']), c, r)
        self.setModel(self.model)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.c, self.r = 0, 0
        self.t  = MyTable(PandasModel, table_data, self.c, self.r)
        edit_cell_button = QPushButton('to allow to edit cell')
        edit_cell_button.clicked.connect(self.handle_edit_cell_button)
        disable_access_table_button = QPushButton('to deny to edit cell')
        disable_access_table_button.clicked.connect(self.handle_disable_access_table_button)
        vbox = QVBoxLayout()
        vbox.addWidget(self.t)
        vbox.addWidget(edit_cell_button)
        vbox.addWidget(disable_access_table_button)
        self.setLayout(vbox)

    # to allow access (select & edit) to table
    def handle_edit_cell_button(self):
        self.c, self.r = 0, 0

    # to deny access to table
    def handle_disable_access_table_button(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())
