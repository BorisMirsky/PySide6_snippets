from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import pandas as pd


headers = [
          ['Пикетаж характерных точек', '', 'Длина кривой, м', '', 'Радиус, м', 'Возвышение наружного\n рельса, мм', '', ''], 
          ['Точка', 'км + м', 'круговой', 'переходной', '', 'левого', 'правого', 'уклон\n отвода']
        ]

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
        self.table.setSpan(0, 0, 1, 2)
        self.table.setSpan(0, 2, 1, 2)
        self.table.setSpan(0, 4, 2, 1)
        self.table.setSpan(0, 5, 1, 3)

        fnt = self.table.font()
        fnt.setPointSize(12)
        fnt.setBold(True)
        
        layout.addWidget(self.table)
        #layout.addStretch()
        #layout.setSpacing(0)
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

   
class Plan1Class(QWidget):
    def __init__(self):
        super().__init__()
        #self.headers = MyHeaders()
        self.setStyleSheet("margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.resize(850,600)
        self.initUI()

        
    def initUI(self, ):
        layout = QVBoxLayout()
        self.table = QTableView()
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        # в модели передаются только именованные аргументы
        data = self.read_data('EightColumnsData.csv') 
        model = pandasModel(data) 
        self.table.setModel(model)
        #layout.addWidget(self.headers)
        layout.addWidget(self.table)
        #layout.addStretch()
        #layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        delegate = AlignDelegate(self.table)
        for j in range(8):               
            self.table.setItemDelegateForColumn(j, delegate)
        self.setLayout(layout)

    def read_data(self, fname):
        df = pd.read_csv(fname)
        return df


class MainClass(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = MyHeaders()
        self.TableModel = Plan1Class()
        self.setStyleSheet("margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.resize(850,600)
        self.initUI()

        
    def initUI(self, ):
        layout = QVBoxLayout()
        #self.table = QTableView()
        #self.table.horizontalHeader().setVisible(False)
        #self.table.verticalHeader().setVisible(False)
        # в модели передаются только именованные аргументы
        #data = self.read_data('EightColumnsData.csv') 
        #model = pandasModel(data) 
        #self.table.setModel(model)
        layout.addWidget(self.headers, stretch=1)
        layout.addWidget(self.TableModel, stretch=7)
        #layout.addStretch(1)
        #layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)


    
app=QApplication(sys.argv)
window=MainClass()    
window.show()
app.exec()


"""
1 убрать пустое пространство у заголовков
2 вплотную сблизить 2 виджета
3 убрать бордер у заголовков
4 растянуть таблицы по всей коробке
5 цвет шрифта в заголовках серый + везде крупнее (?)

7 сделать ещё 3 такие же
"""
