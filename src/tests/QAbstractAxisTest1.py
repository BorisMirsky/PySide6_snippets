from PySide6.QtWidgets import *
from PySide6.QtGui import QPen
from PySide6.QtCore import *
from PySide6.QtCharts import *
import pandas_datareader.data as web
 
df = web.DataReader('GE', 'yahoo', start='2022-05-01', end='2022-05-25')
 
date = df.index
x = len(date)
 
qt = [None] * x
 
for i in range(0, x):
   qt[i] = QDateTime(date[i]).toMSecsSinceEpoch()
 
 
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
 
        self._chart_view = QtChart.QChartView()
 
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
 
        lay = QtWidgets.QVBoxLayout(central_widget)
        lay.addWidget(self._chart_view)
 
        self._chart = QtChart.QChart()
        self._candlestick_serie = QtChart.QCandlestickSeries()
        self.dt_line_serie = QtChart.QLineSeries()
        self.int_line_serie = QtChart.QLineSeries()
 
        st = QPen(Qt.red)
        st.setWidth(3)
        self.int_line_serie.setPen(st)
 
        for i in range(0, len(df)):
            o_ = df.iloc[i, 2]
            h_ = df.iloc[i, 0]
            l_ = df.iloc[i, 1]
            c_ = df.iloc[i, 3]
            self._candlestick_serie.append(QtChart.QCandlestickSet(o_, h_, l_, c_, float(i)))
            self.dt_line_serie.append(qt[i], o_)
            self.int_line_serie.append(float(i), o_)
 
        self._chart.addSeries(self._candlestick_serie)
        self._chart.addSeries(self.dt_line_serie)
        self._chart.addSeries(self.int_line_serie)
        self._chart.legend().hide()
 
        self._chart_view.setChart(self._chart)
 
        axisX = QValueAxis()
        axisX.setLabelFormat("%d")
        self._chart.addAxis(axisX, Qt.AlignBottom)
        self._candlestick_serie.attachAxis(axisX)
        self.int_line_serie.attachAxis(axisX)
 
        axisX = QDateTimeAxis()
        axisX.setFormat("yyyy-MM-dd")
        self._chart.addAxis(axisX, Qt.AlignBottom)
        self.dt_line_serie.attachAxis(axisX)
 
        axisY = QValueAxis()
        self._chart.addAxis(axisY, Qt.AlignLeft)
        self._candlestick_serie.attachAxis(axisY)
        self.dt_line_serie.attachAxis(axisY)
        self.int_line_serie.attachAxis(axisY)
 
 
if __name__ == "__main__":
    import sys
 
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
