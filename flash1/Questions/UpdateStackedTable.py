from PySide6.QtCore import *
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QTableView,
                               QApplication, QAbstractItemView, QSpinBox, QStackedWidget, QLabel)
import sys
import pandas as pd




externalData = [[[0,0,0], [0,0,0], [0,0,0]],
                [[1,1,1], [1,1,1], [1,1,1]],
                [[2,2,2], [2,2,2], [2,2,2]]]

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
        self.spinBox1 = QSpinBox()
        self.spinBox1.setRange(-100, 100)
        self.spinBox1.setValue(0)
        self.spinBox1.valueChanged.connect(self.__handleSpinBox1)
        spinBox1Label = QLabel("Change table's data")
        #
        self.spinBox2 = QSpinBox()
        self.spinBox2.setRange(0, 2)
        self.spinBox2.setValue(0)
        self.spinBox2.valueChanged.connect(self.__handleSpinBox2)
        spinBox2Label = QLabel("Select table")
        self.Stack = QStackedWidget()
        #
        self.counter = 0
        #
        self.model_list = []
        self.table_list = []
        self.__fillStack()
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        vbox.addWidget(spinBox1Label)
        vbox.addWidget(self.spinBox1)
        vbox.addWidget(spinBox2Label)
        vbox.addWidget(self.spinBox2)
        hbox.addLayout(vbox, 1)
        hbox.addWidget(self.Stack, 3)
        self.setLayout(hbox)

    def __fillStack(self):
        for i in range(0,3,1):
            self.table = MyTable()
            self.model = PandasModel(self.data[i])
            self.model_list.append(self.model)
            self.table.setModel(self.model)
            self.table_list.append(self.table)
            self.Stack.addWidget(self.table)


    # меняем данные в ячейке
    def __handleSpinBox1(self, value):
        self.model_list[self.counter].setData(self.model_list[self.counter].index(1, 1), value, Qt.EditRole)
        self.model_list[self.counter].dataChanged.connect(self.table_list[self.counter].update(self.model_list[self.counter].index(1, 1)))
        #self.model.setData(self.model.index(1, 1), value, Qt.EditRole)
        #self.model.dataChanged.connect(self.table.update(self.model.index(1, 1)))

    # меняем таблицу
    def __handleSpinBox2(self, value):
        self.Stack.setCurrentIndex(value)
        self.counter = value
        #self.spinBox1.setValue(self.model_list[self.counter].index(1, 1))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MW = MainWidget(externalData)
    MW.show()
    sys.exit(app.exec())