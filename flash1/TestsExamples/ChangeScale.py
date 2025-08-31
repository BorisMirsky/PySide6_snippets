import PySide6.QtCharts
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCharts import *
import math
import sys



class Charts(QWidget):
    def __init__(self, parent=None):
        super(Charts, self).__init__(parent)
        self.chart = QChart()
        self.series = PySide6.QtCharts.QLineSeries()    #QLineSeries()
        self.x_start = 0
        self.x_stop = 100
        self.zoomFactor = self.x_stop / 20
        self.zoom_value = 0
        for i in range(self.x_start, self.x_stop, 1):
            self.series.append([QPointF(i, math.cos(i * 0.1))])
        self.chart.addSeries(self.series)
        self.y_axis = QValueAxis()
        self.y_axis.setRange(-1, 1)
        self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.y_axis.setTickInterval(5)
        self.x_axis = QValueAxis()
        self.x_axis.setRange(self.x_start, self.x_stop)
        self.x_axis.setTickInterval(5)
        self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.x_axis)
        self.series.attachAxis(self.y_axis)
        self.chart.legend().hide()
        self.chartview = QChartView(self.chart)
        self.chartview.setRenderHint(QPainter.Antialiasing)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chartview)
        self.setLayout(vbox)

    def keyPressEvent(self, keyEvent):
        key = keyEvent.key()
        if key == Qt.Key_W and self.zoom_value < 10:
            self.x_start = self.x_start + self.zoomFactor
            self.x_stop = self.x_stop - self.zoomFactor
            self.x_axis.setRange(self.x_start, self.x_stop)
            self.zoom_value = self.zoom_value + 1
        elif key == Qt.Key_S and self.zoom_value > 0:
            self.x_start = self.x_start - self.zoomFactor
            self.x_stop = self.x_stop + self.zoomFactor
            self.x_axis.setRange(self.x_start, self.x_stop)
            self.zoom_value = self.zoom_value - 1
        elif key == Qt.Key_A and self.zoom_value > 0:          # to left
            self.x_start = self.x_start - self.zoomFactor
            self.x_stop = self.x_stop - self.zoomFactor
            self.x_axis.setRange(self.x_start, self.x_stop)
        if key == Qt.Key_D and self.zoom_value < 10:           # to right
            self.x_start = self.x_start + self.zoomFactor
            self.x_stop = self.x_stop + self.zoomFactor
            self.x_axis.setRange(self.x_start, self.x_stop)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    charts = Charts()
    charts.show()
    sys.exit(app.exec())