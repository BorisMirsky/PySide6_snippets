import sys
import threading
import time

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import SIGNAL, Slot, SLOT

class CopterDataModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(CopterDataModel, self).__init__(parent)
        self.data_contents = [[1, 2]]

    def rowCount(self, n=None):
        return len(self.data_contents)

    def columnCount(self, n=None):
        return 2

    def data(self, index, role):
        row = index.row()
        col = index.column()
        # print('row {}, col {}, role {}'.format(row, col, role)) #for debug
        if role == QtCore.Qt.DisplayRole:
            return self.data_contents[row][col] or ""

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        if role == QtCore.Qt.EditRole:
            self.data_contents[index.row()][index.column()] = value
            print("edit", value)
            self.dataChanged.emit(
                index, index, (QtCore.Qt.EditRole,)
            )  # NOT WORKING
        else:
            return False
        return True

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    @Slot(int, int) #, QVariant)
    def update_item(self, row, col, value):
        ix = self.index(row, col)
        self.setData(ix, value)


class SignalManager(QtCore.QObject):
    fooSignal = SIGNAL((int, int)) #, QtCore.QVariant)


if __name__ == "__main__":

    def timer(obj):
        idc = 1001
        while True:
            obj.fooSignal.emit(0, 0, idc)
            idc += 1
            time.sleep(1)

    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    foo = SignalManager()

    tableView = QtWidgets.QTableView()
    myModel = CopterDataModel()
    foo.fooSignal.connect(myModel.update_item)

    tableView.setModel(myModel)

    tableView.show()

    t = threading.Thread(target=timer, args=(foo,), daemon=True)
    t.start()

    app.exec()