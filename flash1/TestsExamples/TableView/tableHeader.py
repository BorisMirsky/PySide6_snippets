from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import pandas as pd


class AlignDelegate(QStyledItemDelegate):     
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter   
        

class Headers(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.initUI()
        self.read_data('dataWidgetTable.csv')

    def initUI(self):
        self.setWindowTitle("table's header")
        self.resize(1200,200);
        conLayout = QHBoxLayout()

        tableWidget = QTableWidget()
        tableWidget.setRowCount(20)
        tableWidget.setColumnCount(7)
        conLayout.addWidget(tableWidget)

        # Hide headers
        tableWidget.horizontalHeader().setVisible(False)
        tableWidget.verticalHeader().setVisible(False)

        tableWidget.setSpan(0, 0, 2, 1)  
        newItem = QTableWidgetItem("Описание элементов плана \n линии")  
        tableWidget.setItem(0, 0, newItem)

        tableWidget.setSpan(0, 1, 2, 1)
        newItem = QTableWidgetItem("Установленная \n скорость\n км\ч")  
        tableWidget.setItem(0, 1, newItem)

        tableWidget.setSpan(0, 2, 1, 3) 
        newItem = QTableWidgetItem("Факторы ограничения скорости")  
        tableWidget.setItem(0, 2, newItem)

        newItem = QTableWidgetItem("Анеп\n м/с кв")  
        tableWidget.setItem(1, 2, newItem)

        newItem = QTableWidgetItem("Кси\n м/с кб")  
        tableWidget.setItem(1, 3, newItem)

        newItem = QTableWidgetItem("Fv\n мм/с")  
        tableWidget.setItem(1, 4, newItem)      
        
        tableWidget.setSpan(0, 5, 2, 1)   
        newItem = QTableWidgetItem("Допускаемая\n скорость\n км\ч")  
        tableWidget.setItem(0, 5, newItem)

        tableWidget.setSpan(0, 6, 2, 1) 
        newItem = QTableWidgetItem("Причины\n ограничений\n скорости")  
        tableWidget.setItem(0, 6, newItem)

        tableWidget.resizeRowsToContents()

        # bold font
        fnt = tableWidget.font()
        fnt.setPointSize(10)
        fnt.setBold(True)
        tableWidget.setFont(fnt)
        # align center
        delegate = AlignDelegate(tableWidget)
        for j in range(tableWidget.columnCount()):
            tableWidget.setItemDelegateForColumn(j, delegate)

        self.setLayout(conLayout)
        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # disable editing

    def read_data(self, fname):
        df = pd.read_csv(fname)
        a,b,c,d,e,f,k,n = df['Точка'],df['км+м'],df['круговой'],df['переходной'],df['Радиус'],df['левого'],df['правого'],df['уклонОтвода']
        return a,b,c,d,e,f,k,n
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = Headers()  
    example.show()   
    sys.exit(app.exec())
