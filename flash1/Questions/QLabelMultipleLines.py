from PySide6.QtWidgets import QWidget, QVBoxLayout,QPushButton, QApplication, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis
from PySide6.QtGui import Qt, QPen, QIntValidator, QBrush
from PySide6.QtCore import Qt,  QCoreApplication
import sys


class ChartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(150, 100)
        #lbl = QLabel("%s\n%s " % ('sss', 'gfghfgh'), self)
        lbl = QLabel(" %s \n %s \n %s" % ('Принять', 'все изменения', 'и уйти со страницы'), self)
        vbox = QVBoxLayout()
        vbox.addWidget(lbl)
        self.setLayout(vbox)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cw = ChartWindow()
    cw.show()
    sys.exit(app.exec())
