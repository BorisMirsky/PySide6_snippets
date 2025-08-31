from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication, QSpinBox, QLabel, QPushButton,QStackedLayout
from PySide6.QtCharts import * #QLineSeries, QChart, QChartView, QValueAxis
from PySide6.QtCore import QPoint, QPointF
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from ..update_by_click.by_click import UpdateChartByClick


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300,200)
        btn1 = QPushButton("update chart by click")
        btn1.clicked.connect(self.__handleBtnMain1)
        btn2 = QPushButton("update chart by timer")
        btn2.clicked.connect(self.__handleBtnMain2)
        vbox = QVBoxLayout()
        vbox.addWidget(btn1)
        vbox.addWidget(btn2)
        widget = QWidget()
        widget.setLayout(vbox)
        self.stackedLayout = QStackedLayout()
        self.stackedLayout.addWidget(widget)
        self.setLayout(self.stackedLayout)

    def __handleBtnMain1(self):
        print("__handleBtnMain1")
        chart = UpdateChartByClick()
        chart.show()
        #self.setWindowTitle("change_layout_1_to_2")
        #self.stackedLayout.setCurrentIndex(0)

    def __handleBtnMain2(self):
        print("__handleBtnMain2")
        #self.setWindowTitle("change_layout_2_to_1")
        #self.stackedLayout.setCurrentIndex(1)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())