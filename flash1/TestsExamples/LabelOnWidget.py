import sys
from PySide6.QtCharts import QCandlestickSeries, QChart, QChartView, QCandlestickSet, QLineSeries
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget,QVBoxLayout
from PySide6.QtCore import Qt, QPointF, QObject, QTimer, Signal,QMimeData
from PySide6.QtGui import QDrag
import random
from math import sin


class LabelOnParent(QLabel):
    def __init__(self, title, parent):
        super(LabelOnParent, self).__init__(title, parent)
        self.move(1600,10)

class Chart1(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300,500)
        lbl = QLabel(989797987987)
        vbox = QVBoxLayout(self)
        vbox.addWidget(lbl)
        self.setLayout(vbox)

        self.label = LabelOnParent(
            "iou31fffhko3hnfkjl", self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Chart1()
    window.resize(500, 400)
    window.show()
    sys.exit(app.exec())
