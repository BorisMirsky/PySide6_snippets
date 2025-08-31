import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import pandas as pd

table_straight = [['','', ''],
                  ['','', ''],
                  ['','', ''],
                  ['','', ''],
                  ['','', '']]

table_transition = [['Длина Lпк, м', '', ''],
            ['Уклон отвода ВНР', '', ''],
            [chr(936) + ' (Пси)' + ' м/c\u00B3', '', ''],
            ['Fv, мм/c', '', ''],
            ['Vmax, км/ч', '', '']]

table_curve = [['Радиус, м', '', ''],
            ['Длина КК, м','', ''],
            ['ВНР, мм','', ''],
            ['Анеп, м/с\u00B2','', ''],
            ['Vmax, км/ч','', '']]


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super(PandasModel, self).__init__()
        self._data = pd.DataFrame(data, columns=['Параметры', 'Существующие', 'Допускаемые'])

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        else:                                           # index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role: Qt.EditRole):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            self._data.iat[index.row(), index.column()] = value
            return True
        return False

    def setHeaderData(self, section, orientation: Qt.Horizontal, data: list, role: int = Qt.ItemDataRole.EditRole):
        if orientation == Qt.Horizontal and role in (Qt.DisplayRole, Qt.EditRole):
            try:
                self.horizontalHeaders[section] = data
                return True
            except:
                return False
        return super().setHeaderData(section, orientation, data, role)

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def flags(self, index):
        flags = super().flags(index)
        if index.data() is None:
            flags &= Qt.ItemIsSelectable
        return flags
        #return super().flags(index) | Qt.ItemIsEditable


class MyHeaderView(QHeaderView):
    def __init__(self,parent):
        QHeaderView.__init__(self, Qt.Horizontal, parent)
        self.sectionResized.connect(self.myresize)

    def myresize(self, *args):
        ws=[]
        for c in range(self.count()):
            wii=self.sectionSize(c)
            ws.append(wii)

        if args[0]>0 or args[0]<self.count():
            for ii in range(args[0],self.count()):
                if ii==args[0]:
                    self.resizeSection(ii,args[2])
                elif ii==args[0]+1:
                    self.resizeSection(ii,ws[ii]-(args[2]-args[1]))
                else:
                    self.resizeSection(ii,ws[ii])

    def resizeEvent(self, event):
        super(QHeaderView, self).resizeEvent(event)
        self.setSectionResizeMode(1,QHeaderView.Stretch)
        for column in range(self.count()):
            self.setSectionResizeMode(column, QHeaderView.Stretch)
            width = self.sectionSize(column)
            self.setSectionResizeMode(column, QHeaderView.Interactive)
            self.resizeSection(column, width)
        return


class MyTable(QTableView):
    def __init__(self, parent=None):
        super(MyTable, self).__init__(parent)
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        #
        hh = MyHeaderView(self)
        self.setHorizontalHeader(hh)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setShowGrid(True)
        hh.setSectionsMovable(True)
        hh.setStretchLastSection(False)

