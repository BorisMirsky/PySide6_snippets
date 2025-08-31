from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QSpinBox
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis
from PySide6.QtCore import QPoint, QPointF
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


# spinbox
class SB(QWidget):
    def __init__(self):
        super().__init__()
        self.sp = QSpinBox()
        self.sp.setRange(-100, 100)
        self.sp.setValue(0)
        vbox = QVBoxLayout()
        vbox.addWidget(self.sp)
        self.setLayout(vbox)

# Chart
class Chart(QWidget):
    def __init__(self):
        super().__init__()
        self.chart = QChart()
        self.data = [math.sin(i * 0.05) for i in range(0, 100, 1)]
        self.series = QLineSeries()
        for i in range (0, 100, 1):
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
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)

# all together
class ResultWidget(QWidget):
    def __init__(self):
        super().__init__()
        spInstance = SB()
        spInstance.sp.valueChanged.connect(self.updateChart)
        self.ch = Chart()
        vbox = QVBoxLayout()
        vbox.addWidget(self.ch)
        vbox.addWidget(spInstance)
        self.setLayout(vbox)

    def updateChart(self, value):
        self.ch.series.clear()
        for i in range(0, 100, 1):
           self.ch.series.append(QPointF(i, self.ch.data[i] + value))
        self.ch.chart_view.update()



######################################## Всё в одном классе #############################################
class OnlyChart(QWidget):
    def __init__(self):
        super().__init__()
        self.chart = QChart()
        self.data = [math.sin(i * 0.05) for i in range(0, 100, 1)]
        self.series = QLineSeries()
        for i in range (0, 100, 1):
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
        sp = QSpinBox()
        sp.setRange(-100, 100)
        sp.setValue(0)
        sp.valueChanged.connect(self.updateChart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        vbox.addWidget(sp)
        self.setLayout(vbox)

    def updateChart(self, value):
        self.series.clear()
        for i in range(0, 100, 1):
           self.series.append(QPointF(i, self.data[i] + value))
        self.chart_view.update()
###############################################################################################################



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ResultWidget()   # OnlyChart()
    window.show()
    sys.exit(app.exec())