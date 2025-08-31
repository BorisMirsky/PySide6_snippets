import sys
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import QPointF, QEvent, QPoint, QRect
from PySide6.QtWidgets import QApplication, QMainWindow, QRubberBand



class ChartView(QChartView):
    def init_rubber_band(self):
        chart = self.chart()

        start1 = chart.mapToPosition(QPointF(0, 0))
        start2 = chart.mapToScene(start1)
        start3 = QPoint()
        start3.setX(int(start2.x()))
        start3.setY(int(start2.y()))

        end = QPoint(200, 200)

        self.rubber = QRubberBand(QRubberBand.Rectangle, self);
        self.rubber.setGeometry(QRect(start3, end))
        self.rubber.show()


app = QApplication(sys.argv)
series0 = QLineSeries()
series1 = QLineSeries()

series0 << QPointF(1, 15) << QPointF(3, 17) << QPointF(7, 16) << QPointF(9, 17) \
        << QPointF(12, 16) << QPointF(16, 17) << QPointF(18, 15)
series1 << QPointF(1, 3) << QPointF(3, 4) << QPointF(7, 3) << QPointF(8, 2) \
        << QPointF(12, 3) << QPointF(16, 4) << QPointF(18, 3)

chart = QChart()
chart.addSeries(series0)
chart.addSeries(series1)
chart.createDefaultAxes()
chartView = ChartView(chart)

chartView.init_rubber_band()

window = QMainWindow()
window.setCentralWidget(chartView)
window.resize(400, 300)
window.show()

sys.exit(app.exec())