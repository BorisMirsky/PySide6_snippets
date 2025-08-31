from PySide6.QtCore import *
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QApplication
#from PySide6.QtCharts import *
from PySide6.QtGui import *
#from Data import 'data.csv'
# from NumpyTableModel import NumpyTableModel
# from VerticalLine2 import MoveLineController, VerticalLineModel
import sys
import numpy as np
import pandas as pd
#import warnings
#warnings.filterwarnings("ignore", category=DeprecationWarning)
#from ModelTable import *
#import math


# picket,plan_mes,plan_prj,plan_d,prof_mes,prof_prj,prof_d,vozv_mes,vozv_prj,col10,col11,col12,col13,col14
table_straight = [['','', ''],
                  ['','', ''],
                  ['','', ''],
                  ['','', ''],
                  ['','', '']]

table_transition = [['Длина Lпк, м', '', ''],
            ['Уклон отвода ВНР', '', ''],
            ['Кси, мм/c кб.', '', ''],
            ['Fv, мм/c', '', ''],
            ['Vmax, км/ч', '', '']]

table_curve = [['Радиус, м', '', ''],
            ['Длина КК, м','', ''],
            ['ВНР, мм','', ''],
            ['Анеп, м/с','', ''],
            ['Vmax, км/ч','', '']]

def read_csv_file(filename):
    df = pd.read_csv(filename, sep=";")
    return df

def get_csv_column(filename, column_name):
    df = read_csv_file(filename)
    column = df.loc[:, column_name]
    return column.tolist()

def get_csv_row(filename, row_index):
    df = read_csv_file(filename)
    row = df.iloc[[row_index]]#df.iloc[[2]]
    return row.values.tolist()




FILENAME = 'Data/data.csv'
SUMMARYFILENAME = 'Data/summary.csv'
DATA_LEN = len(get_csv_column(FILENAME, 'plan_prj'))
first_points = get_csv_column(SUMMARYFILENAME, 'picket_start')
second_points = get_csv_column(SUMMARYFILENAME, 'picket_end')
# curve_types = get_csv_column('Data/summary.csv', 'curve_type')
SUMMARY_LEN = len(first_points)


#print(get_csv_row(SUMMARYFILENAME, 0)[0][-1])



######################################################
class PandasModel(QAbstractTableModel):
    def __init__(self, table):
        QAbstractTableModel.__init__(self)
        data =  pd.DataFrame(table)
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
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class MyTable(QTableView):
    def __init__(self, model:QAbstractTableModel, data, parent=None):
        super().__init__(parent)
        self.data = data
        #self.model = model
        #layout = QVBoxLayout()
        #self.table = QTableView()
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.model = model(pd.DataFrame(data, columns=['Параметры', 'Существующие', 'Допускаемые']))
        self.setModel(self.model)
        #layout.addWidget(self.table)
        #self.setLayout(layout)

def fill_first_stackwidget(filename:str, ind:int):
    data = read_csv_file(filename)
    row = data.iloc[[ind]]
    if row.values.tolist()[0][-1] == 'transition':
        table_transition[0][1] = row.values.tolist()[0][2]         # Длина
        result = table_transition
    elif row.values.tolist()[0][-1] == 'curve':
        table_curve[0][1] = row.values.tolist()[0][3]              # радиус
        table_curve[2][1] = row.values.tolist()[0][4]              # ВНР
        result = table_curve
    elif row.values.tolist()[0][-1] == 'straight':
        result = table_straight
    return result


#if __name__ == '__main__':
    #app = QApplication(sys.argv)
    #window = MyTable(PandasModel, fill_first_stackwidget(SUMMARYFILENAME, 2))
    #window.show()
    #for i in range(0, SUMMARY_LEN, 1):
    #    print(fill_first_stackwidget('Data/summary.csv', i))
        #window = MyTable(PandasModel, fill_first_stackwidget(SUMMARYFILENAME, i))
        #window.show()
    #sys.exit(app.exec())

