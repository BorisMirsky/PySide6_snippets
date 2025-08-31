from PySide6.QtCore import *
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTableView, QApplication, QAbstractItemView, QSpinBox
#from PySide6.QtGui import *
import sys
#import numpy as np
import pandas as pd
#import copy




class PandasModel(QAbstractTableModel):
    def __init__(self, table):
        super(PandasModel, self).__init__()
        data = pd.DataFrame(table)
        self._data = data

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
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            row = index.row()  
            column = index.column() 
            self._data[row][column] = value
            self.dataChanged.emit(index)
            return True
        return False

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class MyTable(QTableView):
    def __init__(self, model:QAbstractTableModel, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)
        self.model = model(pd.DataFrame(data, columns=['Col1', 'Col2', 'Col3']))
        self.setModel(self.model)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.spinBox = QSpinBox()
        self.spinBox.setRange(-100, 100)
        self.spinBox.setValue(0)
        self.spinBox.valueChanged.connect(self.__handleSpinBox)
        self.pandasModel = PandasModel
        table = MyTable(PandasModel, [[0,0,0], [0,0,0]])
        hbox = QHBoxLayout()
        hbox.addWidget(self.spinBox, 1)
        hbox.addWidget(table, 1)
        self.setLayout(hbox)

    def __handleSpinBox(self, value):
        #self.pandasModel.setData(self.pandasModel.index(1,1), result, Qt.EditRole)
        self.pandasModel.setData(PandasModel.index(1,1), result, Qt.EditRole) 




if __name__ == '__main__':
    app = QApplication(sys.argv)
    MW = MainWidget()
    MW.show()
    sys.exit(app.exec())     
