from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QChart, QChartView
from PySide6.QtCore import Qt, QObject, QPointF
import sys
from math import sin


class Chart1(QWidget):
    def __init__(self):
        super().__init__()
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.series1 = QLineSeries()
        for i in range(0, 500, 1):
            self.series1.append([QPointF(i, sin(i * 0.05))])
        self.chart.addSeries(self.series1)
        self.chart.createDefaultAxes()
        self.chart.axisX().setRange(0, 500)
        self.chart.axisY().setRange(-5,5)
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Chart1()
    window.show()
    sys.exit(app.exec())