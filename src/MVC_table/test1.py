from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


class Table(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.model = QStandardItemModel()
        self.table = QTableView()
        self.table.setModel(self.model)
        #self.table.horizontalHeader().setSectionResizeMode(1)
        self.btnLoad = QPushButton("Load")
        self.btnClear = QPushButton("Clear")
        self.btnGet = QPushButton('Get')
        self.btnLoad.clicked.connect(self.load_data)
        self.btnClear.clicked.connect(self.on_clear)
        self.btnGet.clicked.connect(self.get_data)
        grid = QGridLayout(self)
        grid.setContentsMargins(1,1,1,1)
        grid.addWidget(self.table,0,0,4,4)
        grid.addWidget(self.btnLoad,4,0,1,1)
        grid.addWidget(self.btnClear,4,1,1,1)
        grid.addWidget(self.btnGet,4,3,1,1)
        self.rows = 2
        self.cols = 3
        
    def load_data(self):
        self.model.setRowCount(self.rows)
        self.model.setColumnCount(self.cols)
        for row in range(self.rows):
            for col in range(self.cols):
                item = QStandardItem(str(row)+':'+str(col))
                self.model.setItem(row,col,item)
        self.rows += 1
        self.cols += 1
            
    def on_clear(self):
        self.model.clear()
        self.rows = 2
        self.cols = 3
    
    def get_data(self):
        rows = self.model.rowCount()
        cols = self.model.columnCount()
        out = [[self.model.item(i,j).text() for j in range(cols)] for i in range(rows)]
        print(out)


        
if __name__=="__main__":
    app = QApplication([])
    w = Table()
    w.show()
    app.exec()
