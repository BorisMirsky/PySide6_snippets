from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import pandas as pd


class AlignDelegate(QStyledItemDelegate):     
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter   
        

class TableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.initUI()
        self.read_data('dataWidgetTable.csv')

    def initUI(self):
        self.setWindowTitle("table's header")
        self.resize(1000,300);
        conLayout = QHBoxLayout()

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(7)
        conLayout.addWidget(self.tableWidget)

        # bold font
        fnt = self.tableWidget.font()
        fnt.setPointSize(10)
        fnt.setBold(True)
        #self.tableWidget.setFont(fnt)

        # Hide headers
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)

        self.tableWidget.setSpan(0, 0, 2, 1)  
        newItem = QTableWidgetItem("Описание элементов плана \n линии")  
        self.tableWidget.setItem(0, 0, newItem)
        self.tableWidget.item(0,0).setFont(fnt)

        self.tableWidget.setSpan(0, 1, 2, 1)
        newItem = QTableWidgetItem("Установленная \n скорость\n км\ч")  
        self.tableWidget.setItem(0, 1, newItem)
        self.tableWidget.item(0,1).setFont(fnt)
        
        self.tableWidget.setSpan(0, 2, 1, 3) 
        newItem = QTableWidgetItem("Факторы ограничения скорости")  
        self.tableWidget.setItem(0, 2, newItem)
        self.tableWidget.item(0,2).setFont(fnt)

        newItem = QTableWidgetItem("Анеп\n м/с кв")  
        self.tableWidget.setItem(1, 2, newItem)
        self.tableWidget.item(1,2).setFont(fnt)

        newItem = QTableWidgetItem("Кси\n м/с кб")  
        self.tableWidget.setItem(1, 3, newItem)
        self.tableWidget.item(1,3).setFont(fnt)

        newItem = QTableWidgetItem("Fv\n мм/с")  
        self.tableWidget.setItem(1, 4, newItem)
        self.tableWidget.item(1,4).setFont(fnt)
        
        self.tableWidget.setSpan(0, 5, 2, 1)   
        newItem = QTableWidgetItem("Допускаемая\n скорость\n км\ч")  
        self.tableWidget.setItem(0, 5, newItem)
        self.tableWidget.item(0,5).setFont(fnt)

        self.tableWidget.setSpan(0, 6, 2, 1) 
        newItem = QTableWidgetItem("Причины\n ограничений\n скорости")  
        self.tableWidget.setItem(0, 6, newItem)
        self.tableWidget.item(0,6).setFont(fnt)

        self.tableWidget.resizeRowsToContents()
        #self.tableWidget.resizeColumnsToContents()

        # align center
        delegate = AlignDelegate(self.tableWidget)
        for j in range(self.tableWidget.columnCount()):
            self.tableWidget.setItemDelegateForColumn(j, delegate)

        self.setLayout(conLayout)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # disable editing

    def read_data(self, fname):
        df = pd.read_csv(fname)
        for i, row in df.iterrows():
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i+2, j, QTableWidgetItem(str(row[j])))
            
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = TableWidget()  
    example.show()   
    sys.exit(app.exec())











    
