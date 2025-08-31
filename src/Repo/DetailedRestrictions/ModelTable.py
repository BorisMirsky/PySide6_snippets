import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import pandas as pd
from ServiceInfo import SUMMARY_LEN, fill_first_stackwidget  # get_csv_column, DATA_LEN, FILENAME



table1 = {'qqq': ['111', '222'],
          'www': ['333', '444'],
          'eee': ['555', '666']}

table2 = {'aaa': ['777', '888'],
          'sss': ['999', '000'],
          'ddd': ['123', '321']}

table3 = {'jjj': ['345', '654'],
          'xxx': ['135', '753'],
          'ccc': ['098', '579']}

table_straight = [['','', '', ''],
          ['','', '', ''],
          ['','', '', '']]

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


class MyTable(QWidget):
    def __init__(self, model:QAbstractTableModel, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.model = model
        layout = QVBoxLayout()
        self.table = QTableView()
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.model = model(pd.DataFrame(data, columns=['Параметры', 'Существующие', 'Допускаемые']))
        self.table.setModel(self.model)
        layout.addWidget(self.table)
        self.setLayout(layout)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    #model = table1   #table_transition #fill_first_stackwidget('Data/summary.csv', 0)
    window = MyTable(PandasModel, table_curve)
    window.show()
    sys.exit(app.exec())
