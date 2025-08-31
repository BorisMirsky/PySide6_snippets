from PySide6.QtCore import *
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTableView, QApplication, QAbstractItemView, QSpinBox
import sys
import pandas as pd




externalData = [[0,0,0], [0,0,0], [0,0,0]]

class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super(PandasModel, self).__init__()
        self._data = pd.DataFrame(data, columns=['Col1', 'Col2', 'Col3'])

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role: Qt.EditRole):
        if role == Qt.EditRole:
            self._data.iat[index.row(), index.column()] = value
            return True
        return False

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class MyTable(QTableView):
    def __init__(self):
        super(MyTable, self).__init__()
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)


class MainWidget(QWidget):
    def __init__(self, data):
        super().__init__()
        self.resize(500,200)
        self.data = data
        self.spinBox = QSpinBox()
        self.spinBox.setRange(-100, 100)
        self.spinBox.setValue(0)
        self.spinBox.valueChanged.connect(self.__handleSpinBox)
        self.model = PandasModel(self.data)
        self.table = MyTable()
        self.table.setModel(self.model)
        hbox = QHBoxLayout()
        hbox.addWidget(self.spinBox, 1)
        hbox.addWidget(self.table, 3)
        self.setLayout(hbox)

    def __handleSpinBox(self, value):
        self.model.setData(self.model.index(1, 1), value, Qt.EditRole)
        self.model.dataChanged.connect(self.table.update(self.model.index(1, 1)))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    MW = MainWidget(externalData)
    MW.show()
    sys.exit(app.exec())