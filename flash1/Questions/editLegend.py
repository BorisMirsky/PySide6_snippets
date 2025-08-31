from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis, QLegend
from PySide6.QtCore import *
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class Chart(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        self.chart = QChart()
        self.data = [math.sin(i * 0.1) for i in range(0, 100, 1)]
        self.series1 = QLineSeries()
        for i in range (0, 100, 1):
            self.series1.append(i, self.data[i])
        self.series1.setName("series1")
        self.series2 = QLineSeries()
        self.series2.append(0, 0)
        self.series2.append(100, 4)
        self.series2.setName("series2")
        self.series3 = QLineSeries()
        self.series3.append(0, 4)
        self.series3.append(100, -3)
        self.series3.setName("series3")
        self.axisX = QValueAxis()
        self.axisY = QValueAxis()
        self.chart = QChart()
        self.chart.addSeries(self.series1)
        self.chart.addSeries(self.series2)
        self.chart.addSeries(self.series3)
        self.chart.setAxisX(self.axisX)
        self.chart.setAxisY(self.axisY)
        self.chart.axisY().setRange(-5, 5)
        self.chart.axisX().setRange(0, 100)
        self.chart.legend().setVisible(True)
        self.chart_view = QChartView(self.chart)
        #
        legend = self.chart.legend()
        #legend.setMarkerShape(QLegend.MarkerShapeFromSeries)
        for marker in legend.markers():
            if marker.label() == "series2":
                marker.setVisible(False)
        #
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Chart()
    window.show()
    sys.exit(app.exec())