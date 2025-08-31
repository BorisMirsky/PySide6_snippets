from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import sys


class TableModel(QAbstractTableModel):
    def __init__(self, tasks, parent=None):  # +++
        super(TableModel, self).__init__(parent)

        self.tasks = tasks  # +++

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.tasks)

    def columnCount(self, parent=None, *args, **kwargs):
        return 7

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if column == 0:
                return self.tasks[row]  # .title
            elif column == 1:
                return self.tasks[row]  # .start_date.toString()
            elif column == 2:
                return self.tasks[row]  # .end_date.toString()
            elif column == 3:
                return self.tasks[row]  # .man_hours
            elif column == 4:
                return self.tasks[row]  # .task_type
            elif column == 5:
                return self.tasks[row]  # .done
        return None

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["Задача", "Дата начала", "Дата конца",
                        "Отдел", "Количество человек", "Трудоёмкость",
                        "Выполнение"][section]

    def setData(self, index, tasks, role):  # <--- # +++
        if role == Qt.EditRole:
            row = index.row()
            # column = index.column()
            self.tasks[row] = tasks[row]
            return True
        return False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        tasks = ["1a", "2a", "3a", "4a", "5a", "6a"]  # Начальное заполнение
        self.model = TableModel(tasks)
        self.table = QTableView()
        self.table.verticalHeader().hide()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setModel(self.model)

        btn = QPushButton("Click me")
        btn.clicked.connect(self.btnClicked)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        grid = QGridLayout(centralWidget)
        grid.addWidget(self.table, 0, 0)
        grid.addWidget(btn, 1, 0)

    def btnClicked(self):
        rows = self.model.rowCount()
        for row in range(rows):
            self.model.setData(self.model.index(row, 0),
                               ["21a", "22a", "23a", "24a", "25a", "26a"],  # +++
                               Qt.EditRole)
        self.table.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    mw.setGeometry(400, 100, 550, 300)
    sys.exit(app.exec())