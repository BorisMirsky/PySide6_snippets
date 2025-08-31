from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor

class CustomTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        QAbstractTableModel.__init__(self)
        self.load_data(data)

    def load_data(self, data):
        self.col1 = data[0].values
        self.col2 = data[1].values
        self.col3 = data[2].values
        self.col4 = data[3].values
        self.col5 = data[4].values
        self.col6 = data[5].values
        self.col7 = data[6].values
        self.col8 = data[7].values
        self.column_count = 8
        self.row_count = len(self.col1)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("1", "2", "3", "4", "5", "6", "7", "8")[section]
        else:
            return f"{section}"
 
    def data(self, index, role):   
        column = index.column()
        row = index.row()
        if role == Qt.DisplayRole:
            if column == 0:
                col1_ = self.col1[row]
                return str(col1_)#[:]
            elif column == 1:
                col2_ = self.col2[row]
                return str(col2_)#[:]
            elif column == 2:
                col3_ = self.col3[row]
                return str(col3_)#[:]
            elif column == 3:
                col4_ = self.col4[row]
                return str(col4_)#[:]
            elif column == 4:
                col5_ = self.col5[row]
                return str(col5_)#[:]
            elif column == 5:
                col6_ = self.col6[row]
                return str(col6_)#[:]
            elif column == 6:
                col7_ = self.col7[row]
                return str(col7_)#[:]
            elif column == 7:
                col8_ = self.col8[row]
                return str(col8_)#[:]
        #elif role == Qt.BackgroundRole:
        #    return QColor(Qt.white)
        #elif role == Qt.TextAlignmentRole:
        #    return Qt.AlignRight
        return None
