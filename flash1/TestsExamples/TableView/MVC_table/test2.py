import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


data = [
          [4, 9, 2, 3, 5, 6, 6, 7],
          [1, 0, 0, 4, 5, 2, 1, 1],
          [3, 5, 0, 2, 3, 4, 5, 6],
          [3, 3, 2, 1, 1, 2, 3, 4],
          [7, 8, 9, 3, 5, 5, 6, 7],
          [4, 9, 2, 5, 5, 7, 8, 9],
          [1, 0, 0, 8, 9, 0, 0, 5],
          [3, 5, 0, 4, 1, 2, 2, 2],
          [4, 9, 2, 3, 5, 6, 6, 7],
          [1, 0, 0, 4, 5, 2, 1, 1],
          [3, 5, 0, 2, 3, 4, 5, 6],
          [3, 3, 2, 1, 1, 2, 3, 4],
          [7, 8, 9, 3, 5, 5, 6, 7],
          [4, 9, 2, 5, 5, 7, 8, 9],
          [1, 0, 0, 8, 9, 0, 0, 5],
          [3, 5, 0, 4, 1, 2, 2, 2],
        ]

data1 = [
          ['A1', '', 'A2', '', 'A3', 'A4', '', ''], 
          ['B1', 'B2', 'B3', 'B4', '', 'B5', 'B6', 'B7']
        ]



# class MyHeaders(QWidget):
#     def __init__(self, data):
#         super().__init__()
#         #self.resize(850,50)
#         self.data = data
#         layout = QVBoxLayout()
#         self.table = QTableView()
#         self.table.horizontalHeader().setVisible(False)
#         self.table.verticalHeader().setVisible(False)
#         self.model = TableModel(self.data)  #HeadersModel(data1)
#         self.table.setModel(self.model)
#         self.table.setSpan(0, 0, 1, 2)
#         self.table.setSpan(0, 2, 1, 2)
#         self.table.setSpan(0, 4, 2, 1)
#         self.table.setSpan(0, 5, 1, 3)
#         layout.addWidget(self.table)
#         layout.setContentsMargins(0,0,0,0)
#         self.setLayout(layout)

table_curve = [['Радиус, м', '', ''],
            ['Длина КК, м','', ''],
            ['ВНР, мм','', ''],
            ['Анеп, м/с','', ''],
            ['Vmax, км/ч','', '']]


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self.data = data
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]
    def rowCount(self, index):
        return len(self.data)
    def columnCount(self, index):
        return len(self.data[0])

class MyTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.table = QTableView()
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.model = TableModel(table_curve)
        self.table.setModel(self.model)
        layout.addWidget(self.table)
        self.setLayout(layout)

        
app=QApplication(sys.argv)
window=MyTable()   
window.show()
app.exec()
