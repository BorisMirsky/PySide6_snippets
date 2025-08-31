import sys
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPointF, QObject
from math import sin


class Label(QLabel):
    def __init__(self, title, parent):
        super(Label, self).__init__(title, parent)
        self.move(150,100)


class ChartView(QChartView):
    def __init__(self, chart1, parent):
        super(ChartView, self).__init__(parent)
        self.chart1 = chart1


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
        self.chart.axisY().setRange(-5, 5)
        self.chart_view = ChartView(self, self.chart)
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.chart_view)
        self.label = Label(
            '<h3>_____Title_____</h3>\n'
            '--------------------------------------------------------------\n'
            '999999999999999999999999999999\n'
            'cccccccccccccccccccccccccccccc\n'
            'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            self.chart_view)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("background-color:yellow;border:1px solid black;padding :15px;")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Chart1()
    window.resize(500, 400)
    window.show()
    sys.exit(app.exec())