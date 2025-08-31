import sys
from PySide6 import QtGui, QtWidgets, QtCore
from PySide6.QtCore import Qt


class Counter(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Counter, self).__init__(parent)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.table = QtWidgets.QTableView(self)
        self.model = QtGui.QStandardItemModel()
        self.model.setColumnCount(2)
        self.model.setRowCount(0)
        self.model.setHorizontalHeaderLabels(['ADDRESS', 'NUMBER', ])
        self.table.setModel(self.model)

        self.label = QtWidgets.QLabel("Укажите количество строк:")
        self.lineEdit = QtWidgets.QLineEdit("7")
        update_button = QtWidgets.QPushButton("Update")
        update_button.clicked.connect(self.on_update_button)

        self.iter = None
        self.timer = QtCore.QTimer(interval=200, timeout=self.add_row)

        grid_layout = QtWidgets.QGridLayout(central_widget)
        grid_layout.addWidget(self.label, 0, 0)
        grid_layout.addWidget(self.lineEdit, 0, 1, 1, 2)
        grid_layout.addWidget(update_button, 0, 3)
        grid_layout.addWidget(self.table, 1, 0, 1, 4)

    def on_update_button(self):
        try:
            rows = int(self.lineEdit.text())
        except ValueError:
            print("Введенное значение должно быть целым числом.")
        else:
            if rows > 0:
                self.model.setRowCount(0)
                self.iter = iter(range(rows))
                self.add_row()
                self.timer.start()
            else:
                print("Введенное значение должно быть положительным целым числом.")

    def add_row(self):
        try:
            i = next(self.iter)
        except StopIteration:
            self.iter = None
            self.timer.stop()
        else:
            item1 = QtGui.QStandardItem("item" + str(i))
            item1.setTextAlignment(QtCore.Qt.AlignCenter)
            item2 = QtGui.QStandardItem("item" + str(i))
            item2.setTextAlignment(QtCore.Qt.AlignCenter)
            self.model.appendRow([item1, item2])


if __name__ == "__main__":
    application = QtWidgets.QApplication([])
    window = Counter()
    window.setWindowTitle("Counter")
    window.setMinimumSize(480, 380)
    window.show()
    sys.exit(application.exec())