from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class Chart(QWidget):
    def __init__(self):
        super().__init__()
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.data = [math.sin(i * 0.1) for i in range(0, 1000, 1)]
        self.series = QLineSeries()
        for i in range (0, 1000, 1):
            self.series.append(i, self.data[i])
        self.axisX = QValueAxis()
        self.axisY = QValueAxis()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.legend().setVisible(False)
        self.axisX.setLabelFormat("%d")
        #self.axisY.labelFormat()
        self.axisY.setLabelFormat("%.1f   ")                          # "{:4d}"    #"{:<4}"    # "%.3d"
        self.chart.setAxisX(self.axisX)
        self.chart.setAxisY(self.axisY)
        self.chart.axisY().setRange(-2, 2)
        self.chart.axisX().setRange(0, 1000)
        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)
        self.chart.legend().setVisible(False)
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Chart()
    window.show()
    sys.exit(app.exec())