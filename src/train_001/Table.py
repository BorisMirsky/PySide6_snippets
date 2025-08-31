from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
#import pandas as pd
#from NumpyTableModel import NumpyTableModel
#from AbstractModels import AbstractReadModel
from MockModels import SinMockModel

class TableModel(QAbstractTableModel):
    def __init__(self, data: list, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, index=QModelIndex()): #parent=None):
        return self._data[0]                        # =+ 1

    def columnCount(self, index=QModelIndex()): #parent=None):
        return len(self._data)                      # 5

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return self._data
        return None

    def insertRow(self, row: list, parent=QModelIndex()):
        self._data.append(row)


class TableClass(QWidget):
    def __init__(self,
                 data: list,
                 timer: QTimer(qApp),
                 parent=None,
                 ):
        super().__init__()
        self.data = data
        self.model = TableModel([0, 0, 0, 0 ])
        self.insertionTimer = timer
        self.insertionTimer.start(100)
        self.insertionTimer.timeout.connect(self.dataUpdate)
        layout = QVBoxLayout()
        self.table = QTableView()
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def dataUpdate(self):
        self.positionValue += 1
        #self.positionValue, 
        self.model = TableModel([self.data[0].read(), self.data[1].read(), self.data[2].read(), self.data[3].read()])
        #self.model.insertRow([self.positionValue, self.data[1].read(), self.data[2].read(), self.data[3].read(), self.data[4].read()])
        #self.model.dataChanged.emit(self.positionValue, 1, [2]) #[self.positionValue, self.data[1].read(), self.data[2].read(), self.data[3].read(), self.data[4].read()])
        print(self.positionValue, self.data[0].read(), self.data[2].read(), self.data[2].read(), self.data[3].read())
        self.table.setModel(self.model)

    positionValue = 0



if __name__ == "__main__":
        app = QApplication([])
        sensor1 = SinMockModel(amplitude=5, frequency=2, parent=app)
        sensor2 = SinMockModel(amplitude=4, frequency=3, parent=app)
        sensor3 = SinMockModel(amplitude=3, frequency=4, parent=app)
        sensor4 = SinMockModel(amplitude=2, frequency=5, parent=app)
        insertionTimer = QTimer(qApp)
        data = [sensor1, sensor2, sensor3, sensor4]
        window = TableClass(data, insertionTimer)
        window.show()
        sys.exit(app.exec())

