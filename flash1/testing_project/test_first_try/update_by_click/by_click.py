from PySide6.QtCore import Qt, QPointF
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis
from PySide6.QtWidgets import QApplication,QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)



class UpdateChartByClick(QWidget):
    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self.resize(400, 300)
        self.counter = 0
        self.btn_up = QPushButton('up')
        self.btn_down = QPushButton('down')
        self.btn_up.clicked.connect(self.handle_btn_up)
        self.btn_down.clicked.connect(self.handle_btn_down)
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_up)
        hbox.addWidget(self.btn_down)
        self.chart = self.run_chart()
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.chart)
        self.setLayout(vbox)

    def handle_btn_up(self):
        self.counter += 1
        self.updateChart(self.counter)

    def handle_btn_down(self):
        self.counter -= 1
        self.updateChart(self.counter)

    def run_chart(self):
        self.chart = QChart()
        self.data = [math.sin(i * 0.05) for i in range(0, 100, 1)]
        self.series = QtCharts.QLineSeries()
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


    def updateChart(self, value):
        self.series.clear()
        for i in range(0, 100, 1):
            self.series.append(QPointF(i, round(self.data[i] + value * 0.1, 2)))
        #self.chart_view.update()




if __name__ == "__main__":
    app = QApplication([])
    main = UpdateChartByClick()
    main.show()
    sys.exit(app.exec())
