import sys
import copy
from PySide6 import QtWidgets
from PySide6 import QtCore



class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, table_data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.table_data = table_data

    def rowCount(self, parent):
        return len(self.table_data)

    def columnCount(self, parent):
        return len(self.table_data[0])

    #def flags(self, index):
    #    original_flags = super(MyTableModel, self).flags(index)
    #    return original_flags | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            item = index.internalPointer()
            if item is not None:
                print(item)
            value = self.table_data[row][column]
            return value

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            self.table_data[row][column] = value
            self.dataChanged.emit(index, index)
            print(index, value)
            return True
        return QtCore.QAbstractTableModel.setData(self, index, value, role)


class Widget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        self.view = QtWidgets.QTableView()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.view)

        table_data = [['HD', '1920', '1080', 'other', 'stuff', 'here'], ['lowres', '640', '480', 'other', 'stuff', 'here']]

        self._original_table_data = copy.deepcopy(table_data)

        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.model = MyTableModel(table_data=table_data)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setDynamicSortFilter(True)
        self.view.setModel(self.proxy_model)
        self.proxy_model.dataChanged.connect(self.on_data_changed)

        self.view.setSortingEnabled(True)  # requires proxy model
        self.view.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.horizontalHeader().setSectionsMovable(True)

    def on_data_changed(self, _from, _to):
        model = _from.model() # proxy model
        model.blockSignals(True)
        for index in self.view.selectionModel().selectedIndexes():
            model.setData(index, _from.data())
        model.blockSignals(False)
        #print('data was changed in table')

    def change_value(self, col, multiplier):
        #print('Multiply the value (for all rows) in column %s with: %s' % (col, multiplier))
        index = self.proxy_model.mapFromSource(QtCore.QModelIndex())
        row_count = self.proxy_model.rowCount(index)
        for row in range(0, row_count):
            original_value = self._original_table_data[row][col]
            index = self.proxy_model.index(row, col)
            self.proxy_model.setData(index, int(original_value)*int(multiplier))



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    m = QtWidgets.QWidget()
    w = Widget()
    q = QtWidgets.QLabel('Multiplier:')
    e = QtWidgets.QSpinBox()
    e.setValue(1)
    e.valueChanged.connect(lambda: w.change_value(col=1, multiplier=e.value()))
    e.valueChanged.connect(lambda: w.change_value(col=2, multiplier=e.value()))
    l = QtWidgets.QHBoxLayout()
    l.addWidget(w)
    l.addWidget(q)
    l.addWidget(e)
    m.setLayout(l)
    m.show()
    sys.exit(app.exec())