from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem,QTextEdit,QStackedWidget,QLabel,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QToolButton, QSpinBox)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QShortcut
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QSize, Slot

import sys
import numpy as np
import pandas as pd
import copy


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
    df_copy = df.__deepcopy__()
    row = df_copy.iloc[[row_index]]
    return row.values.tolist()

# взяли строку в summary, в зависимости от последнего значения в строке заполнили таблицу
def getRowFromSummary(filename:str, idx:int):
    data = read_csv_file(filename)
    row = data.iloc[[idx]]
    if row.values.tolist()[0][-1] == 'transition':
        table_transition[0][1] = row.values.tolist()[0][2]         # Длина
        result = table_transition
    elif row.values.tolist()[0][-1] == 'curve':
        table_curve[0][1] = row.values.tolist()[0][3]              # радиус
        table_curve[1][1] = row.values.tolist()[0][2]              # Длина
        table_curve[2][1] = row.values.tolist()[0][4]              # ВНР
        result = table_curve
    elif row.values.tolist()[0][-1] == 'straight':
        result = table_straight
    return result


FILENAME = 'Data/data.csv'
SUMMARYFILENAME = 'Data/summary.csv'
DATA_LEN = len(get_csv_column(FILENAME, 'plan_prj'))
first_points = get_csv_column(SUMMARYFILENAME, 'picket_start')   # все координаты первой вертикальной линии
second_points = get_csv_column(SUMMARYFILENAME, 'picket_end')    # вск координаты второй вертикальной линии
SUMMARY_LEN = len(first_points)


######################################################
class PandasModel(QAbstractTableModel):
    def __init__(self, table):
        super(PandasModel, self).__init__()
        data = pd.DataFrame(table)
        self._data = data

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
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            row = index.row()   #index[0]      #index.row()
            column = index.column()   #index[1]   #index.column()
            self._data[row][column] = value
            self.dataChanged.emit(index)
            return True
        return False

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    #def flags(self, index):
   #     if not index.isValid():
   #         return  Qt.ItemIsEditable # Qt.ItemIsEnabled

    # def func(self, value):
    #     print(value, "_______________")


class MyTable(QTableView):
    def __init__(self, model:QAbstractTableModel, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        #self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.model = model(pd.DataFrame(data, columns=['Параметры', 'Существующие', 'Допускаемые']))
        self.setModel(self.model)


