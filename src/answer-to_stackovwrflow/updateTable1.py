import sys
import threading
import time

from PySide6.QtCore import *
from PySide6.QtWidgets import * #QWidget, QHBoxLayout, QTableView, QApplication, QAbstractItemView, QSpinBox
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
            print(index.row(), index.column(), value)
            return True
        return False

    #def flags(self, index):
    #    return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


class MainWindow(QWidget): #QMainWindow):
    def __init__(self):
        super().__init__()
        self.table = QTableView()
        data = [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]]
        self.model = PandasModel(data)
        self.table.setModel(self.model)
        self.spinBox = QSpinBox()
        self.spinBox.setRange(-100, 100)
        self.spinBox.setValue(0)
        self.spinBox.valueChanged.connect(self.__handleSpinBox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.spinBox, 1)
        hbox.addWidget(self.table, 2)
        self.setLayout(hbox)

    def __handleSpinBox(self, value):
        self.model.setData(self.model.index(1,1), value, Qt.EditRole)
        self.table.update()   #item(1,1).setText(str(value))


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
