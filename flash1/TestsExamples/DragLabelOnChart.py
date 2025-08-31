import sys
from PySide6.QtCharts import QCandlestickSeries, QChart, QChartView, QCandlestickSet, QLineSeries
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget,QVBoxLayout
from PySide6.QtCore import Qt, QPointF, QObject, QTimer, Signal,QMimeData
from PySide6.QtGui import QDrag
import random
from math import sin


class Label(QLabel):
    def __init__(self, title, parent):
        super(Label, self).__init__(title, parent)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.RightButton):
            return
        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setText(self.text())
        if mimedata.hasText():
            print("hattext")
        else:
            print("hasnotext")
        drag.setMimeData(mimedata)
        drag.exec_(Qt.CopyAction)


class ChartView(QChartView):
    def __init__(self, chart1, parent):
        super(ChartView, self).__init__(parent)
        self.chart1 = chart1
        self.setAcceptDrops(True)

    def dragMoveEvent(self, e):
        e.accept()

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        if e.mimeData().hasText():
            indy = e.pos().y()
            indx = e.pos().x()
            # print("index", indx, indy)
            self.chart1.label.move(indx, indy)
            e.setDropAction(Qt.CopyAction)
            e.accept()


class Chart1(QWidget):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)

        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.series1 = QLineSeries()
        for i in range(0, 500, 1):
            self.series1.append([QPointF(i, sin(i * 0.05))])
        self.chart.addSeries(self.series1)
        self.chart.createDefaultAxes()
        self.chart.axisX().setRange(0, 500)
        self.chart.axisY().setRange(-5, 5)

        self.chart_view = ChartView(self, self.chart)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.chart_view)

        self.label = Label(
            '<h3>Это Label <br>Перетащи меня!<br>&nbsp;&nbsp;&nbsp;ПКМ</h3>',
            self.chart_view)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Chart1()
    window.resize(500, 400)
    window.show()
    sys.exit(app.exec())

# thislist = ["apple", "banana", "cherry"]
# thislist.remove(thislist[-1])
# print(thislist)


