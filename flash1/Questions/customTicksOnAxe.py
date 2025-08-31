from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QHBoxLayout, QGraphicsLineItem, QMainWindow
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis, QBarSet, QHorizontalBarSeries, QBarCategoryAxis
from PySide6.QtGui import Qt, QPen, QBrush, QPainter
from PySide6.QtCore import Qt, QCoreApplication, QPointF
import sys



# class ChartWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.resize(700, 500)
#         self.chart = QChart()
#         self.chart.legend().setVisible(False)
#         self.y_axis = QValueAxis()
#         self.y_axis.setRange(0, 20)
#         self.y_axis.setLabelFormat("%d")
#         self.y_axis.setTickType(QValueAxis.TickType.TicksFixed) #     TicksDynamic)
#         self.y_axis.setTickInterval(5)
#         self.y_axis.applyNiceNumbers()
#         self.y_axis.setTickCount(11)
#         self.x_axis = QValueAxis()
#         self.x_axis.setRange(0, 100)
#         self.x_axis.setLabelFormat("%d")
#         self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
#         self.x_axis.setTickInterval(10)
#         self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
#         self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
#         self.series = QLineSeries()
#         for i in range(0, 100, 1):
#             self.series.append(i, 12)
#         self.series.setPen(QPen(Qt.GlobalColor.red, 2))
#         self.chart.addSeries(self.series)
#         self.series.attachAxis(self.x_axis)
#         self.series.attachAxis(self.y_axis)
#         chart_view = QChartView(self.chart)
#         vbox = QVBoxLayout()
#         vbox.addWidget(chart_view)
#         self.setLayout(vbox)
#
#
# class ChartWindow1(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.resize(900, 650)
#         self.chart = QChart()
#         self.chart.legend().setVisible(False)
#         self.chart.setAnimationOptions(QChart.SeriesAnimations)
#         self.chart.setTheme(QChart.ChartThemeBlueCerulean)
#
#         self.y_axis = QValueAxis()
#         self.y_axis.setRange(0, 20)
#         self.y_axis.setLabelFormat("%d")
#         self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
#         self.y_axis.setTickAnchor(11)
#         self.y_axis.setTickInterval(5)
#         self.x_axis = QValueAxis()
#
#         #       self.x_axis.setRange( 0  , 100)
#         self.x_axis.setRange(-0.3, 101)
#
#         self.x_axis.setLabelFormat("%d")
#         self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
#         self.x_axis.setTickInterval(10)
#         self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
#         self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
#
#         self.series = QLineSeries()
#         for i in range(0, 101, 1):
#             self.series.append(i, 12)
#         self.series.setPen(QPen(Qt.GlobalColor.green, 3))  #
#         self.chart.addSeries(self.series)
#         self.series.attachAxis(self.x_axis)
#         self.series.attachAxis(self.y_axis)
#
#         chart_view = QChartView(self.chart)
#
#         vbox = QVBoxLayout(self)
#         vbox.setContentsMargins(0, 0, 0, 0)
#         vbox.addWidget(chart_view)
#
#         # +++ vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#         list_point_y = [12, 0.3, 0.17, 3, 17]
#         for point in list_point_y:
#             series1 = QLineSeries()
#             series1.append(-0.3, point)
#             series1.append(-0.1, point)
#             series1.setPen(QPen(Qt.GlobalColor.red, 4))
#             self.chart.addSeries(series1)
#             self.chart.createDefaultAxes()
#             series1.hovered.connect(self.tooltip)
#
#     # +++ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
#     def tooltip(self, point: QPointF, state: bool):
#         print(f'Y: {point.y():.1f};')  #


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        set0 = QBarSet('X0')
        set1 = QBarSet('X1')
        set2 = QBarSet('X2')
        set3 = QBarSet('X3')
        set4 = QBarSet('X4')
        set0.append([1, 2, 3, 4, 5, 6])
        set1.append([5, 0, 0, 4, 0, 7])
        set2.append([3, 5, 8, 13, 8, 5])
        set3.append([5, 6, 7, 3, 4, 5])
        set4.append([9, 7, 5, 3, 1, 2])
        series = QHorizontalBarSeries()
        series.append(set0)
        series.append(set1)
        series.append(set2)
        series.append(set3)
        series.append(set4)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle('Horizontal Bar Chart Demo')
        chart.setAnimationOptions(QChart.SeriesAnimations)
        months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'June')
        axisY = QBarCategoryAxis()
        axisY.append(months)
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)
        axisX = QValueAxis()
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)
        #axisX.applyNiceNumbers()
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(chartView)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    cw = MainWindow()   #ChartWindow()
    cw.show()
    sys.exit(app.exec())
