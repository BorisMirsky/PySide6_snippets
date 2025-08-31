import unittest
from PySide6.QtCore import Qt
#from PySide6.QtGui import QMainWindow, QLineEdit
from PySide6.QtTest import QTest
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis
from PySide6.QtWidgets import QApplication,QVBoxLayout, QWidget, QPushButton, QLabel
import sys
import math




class Window(QWidget):
    #mySignal = Signal(str)
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.resize(400, 200)
        self.counter = 0
        self.btn = QPushButton('go')
        self.lbl = QLabel(str(self.counter))
        self.btn.clicked.connect(self.handle_btn)
        chart = self.run_chart()
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn)
        vbox.addWidget(self.lbl)
        vbox.addWidget(chart)
        self.setLayout(vbox)

    def handle_btn(self):
        self.counter += 1
        self.lbl.setNum(self.counter)
        print(self.counter)
        #return self.counter

    def run_chart(self):
        self.chart = QChart()
        self.data = [math.sin(i * 0.05) for i in range(0, 100, 1)]
        self.series = QLineSeries()
        for i in range(0, 100, 1):
            self.series.append(i, self.data[i])
        self.axisX = QValueAxis()
        self.axisY = QValueAxis()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setAxisX(self.axisX)
        self.chart.setAxisY(self.axisY)
        self.chart.axisY().setRange(-5, 5)
        self.chart.axisX().setRange(0, 100)
        self.chart.legend().setVisible(False)
        self.chart_view = QChartView(self.chart)
        return self.chart_view



class AppTestCase(unittest.TestCase):
    def setUp(self):
        qApp = QApplication.instance()
        if qApp is None:
            self.app = QApplication([])
        else:
            self.app = qApp

class WindowTestCase(AppTestCase):
    def setUp(self):
        #super(WindowTestCase, self).setUp()
        self.window = Window()
        #self.window.show()
        #QTest.qWaitForWindowExposed(self.window)

    def test_btn_clicked(self):
        #assert self.window.handle_btn()
        btn = self.window.btn
        QTest.mouseClick(btn, Qt.LeftButton)









if __name__ == "__main__":
    app = QApplication([])
    w = Window()
    w.show()
    #unittest.main()
    sys.exit(app.exec())