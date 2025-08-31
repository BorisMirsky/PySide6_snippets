import sys
import threading
import time

import PySide6.QtWidgets
from PySide6.QtCore import *
from PySide6.QtWidgets import * 
from PySide6.QtGui import *

class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self._data[index.row()][index.column()]
                return str(value)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            return True
        return False

externalData = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

class MainWindow(QWidget):
    def __init__(self, data):
        super().__init__()
        self.resize(500, 200)
        self.data = data
        self.table = QTableView()
        self.model = PandasModel(self.data)
        self.table.setModel(self.model)
        self.spinBox = QSpinBox()
        self.spinBox.setRange(-100, 100)
        self.spinBox.setValue(0)
        self.spinBox.valueChanged.connect(self.__handleSpinBox)
        hbox = PySide6.QtWidgets.QHBoxLayout()
        hbox.addWidget(self.spinBox, 1)
        hbox.addWidget(self.table, 3)
        self.setLayout(hbox)

    def __handleSpinBox(self, value):
        self.model.setData(self.model.index(1,1), value, Qt.EditRole)
        self.model.dataChanged.connect(self.table.update(self.model.index(1,1)))


app = QApplication(sys.argv)
window = MainWindow(externalData)
window.show()
app.exec()
