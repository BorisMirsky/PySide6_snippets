from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import pandas as pd


headers = [
          ['Номер\n точки', 'Положение\n характерной\n точки, м',
           'Стрелы изгиба',
           '', 'Сдвиги,\n мм', 'Измерение\n зазоров, мм', 'Возвышение\n наружногорельса, мм', ''], 
          ['', '', 'Натура, мм', 'Проект, мм',
           '', '', 'левого', 'правого']
        ]

#headers = [['11','12','13','','15','16','17',''],
#           ['','','23','24','','','27','28']]

# alignement
class AlignDelegate(QStyledItemDelegate):     
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter

        
class HeadersModel(QAbstractTableModel):
    def __init__(self, data):
        super(HeadersModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])


    
class MyHeaders(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(850,50)
        self.initUI()
        
    def initUI(self):        
        layout = QVBoxLayout()
        self.table = QTableView()
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.model = HeadersModel(headers)  
        self.table.setModel(self.model)
        self.table.setSpan(0, 0, 2, 1)
        self.table.setSpan(0, 1, 2, 1)
        self.table.setSpan(0, 2, 1, 2)
        self.table.setSpan(0, 4, 2, 1)
        self.table.setSpan(0, 5, 2, 1)
        self.table.setSpan(0, 6, 1, 2)

        fnt = self.table.font()
        fnt.setPointSize(12)
        fnt.setBold(True)
        
        layout.addWidget(self.table)
        layout.addStretch()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        delegate = AlignDelegate(self.table)
        for j in range(8):                #self.model.columnCount()):
            self.table.setItemDelegateForColumn(j, delegate)
        self.setLayout(layout)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)   # disable to edit
        

class pandasModel(QAbstractTableModel):
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
        return None

   
class Plan2Class(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = MyHeaders()
        self.setStyleSheet("margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.resize(850,400)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.table = QTableView()
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.model = pandasModel(self.read_data('EightColumnsData.csv')) 
        self.table.setModel(self.model)
        layout.addWidget(self.headers)
        layout.addWidget(self.table)
        #layout.addStretch()
        #layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        delegate = AlignDelegate(self.table)
        for j in range(8):                #self.model.columnCount()):
            self.table.setItemDelegateForColumn(j, delegate)
        self.setLayout(layout)

    def read_data(self, fname):
        df = pd.read_csv(fname)
        return df


#app=QApplication(sys.argv)
#window=Plan2Class()   
#window.show()
#app.exec()


