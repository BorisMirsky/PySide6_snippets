from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
#from tableHeader import Header


class Table(QWidget):   #QMainWindow):
    def __init__(self, parent=None):
        #super(Table, self).__init__(parent)
        #super(MainDialog, self).__init__(parent) 
        super().__init__()
        #QMainWindow.__init__(self)
        #self.setMinimumSize(QSize(800, 80))    
        central_widget = QWidget(self)            
        self.setCentralWidget(central_widget)  
        self.grid_layout = QGridLayout(self)        
        central_widget.setLayout(self.grid_layout)  
        self.createTable()

    def createTable(self):
        table = QTableWidget(self) 
        table.setColumnCount(5)    
        table.setRowCount(10)       
        #table.setHorizontalHeaderLabels(["Описание элементов плана \n линии",
        #                                 "Установленная \n скорость\n км\ч",
        #                                 "Факторы ограничения скорости",
        #                                 "Допускаемая\n скорость\n км\ч",
        #                                 "Причины\n ограничений\n скорости"])
        table.horizontalHeader().setVisible(False)  #
        #table.verticalHeader().setVisible(False)    #
        #table.horizontalHeaderItem(0).setToolTip("Column 1 ")
        #table.horizontalHeaderItem(1).setToolTip("Column 2 ")
        #table.horizontalHeaderItem(2).setToolTip("Column 3 ")
        #table.horizontalHeaderItem(3).setToolTip("Column 4 ")
        #table.horizontalHeaderItem(4).setToolTip("Column 5 ")
        #table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
        #table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
        #table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignRight)
        #table.horizontalHeaderItem(3).setTextAlignment(Qt.AlignRight)
        #table.horizontalHeaderItem(4).setTextAlignment(Qt.AlignRight)
        #table.setSpan(0, 0, 2, 1)   # 3,0,3,1
        #newItem = QTableWidgetItem("tableWidget.setSpan(3, 0, 3, 1)")  
        #table.setItem(3, 0, newItem)

        table.setSpan(0, 0, 2, 1)   # 3,0,3,1
        newItem = QTableWidgetItem("Описание элементов плана \n линии")  
        table.setItem(3, 0, newItem)

        table.setSpan(1, 0, 2, 1)   # 3,0,3,1
        newItem = QTableWidgetItem("Установленная \n скорость\n км\ч")  
        table.setItem(3, 0, newItem)
        #table.setItem(0, 0, QTableWidgetItem("Text in column 1"))
        #table.setItem(0, 1, QTableWidgetItem("Text in column 2"))
        #table.setItem(0, 2, QTableWidgetItem("Text in column 3"))
        #table.setItem(0, 3, QTableWidgetItem("Text in column 4"))
        #table.setItem(0, 4, QTableWidgetItem("Text in column 5"))
        table.resizeColumnsToContents()    
        self.grid_layout.addWidget(table, 0, 0)  
        

#if __name__ == "__main__":
#    import sys 
#    app = QApplication(sys.argv)
#    t = Table()
#    t.show()
#    sys.exit(app.exec())

#import sys 
#app = QApplication(sys.argv)
t = Table()
t.show()
#sys.exit(app.exec())
