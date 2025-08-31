from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QCandlestickSeries, QCandlestickSet, QChart, QChartView

from sqlite import MySql


class MainWindow(QMainWindow):
    def __init__(self, db, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle("Indicator Tool")

        self.db = db
        data = db.view_chart_data("5m")

        self.stockWidget = StockChart()
        self.extraCharts = ExtraCharts()

        self.stockWidget.drawChart(data)
        self.extraCharts.drawChart(data)

        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 2)

        grid.addWidget(self.stockWidget, 0, 0, 2, 2)
        grid.addWidget(self.extraCharts, 1, 0, 2, 2)

        centralWidget = QWidget()
        centralWidget.setLayout(grid)
        self.setCentralWidget(centralWidget)


class StockChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.addWidget(self.chart_view)

    @cached_property
    def chart_view(self):
        chart = QChart()
        chart.legend().hide()
        chart.createDefaultAxes()
        chart.setTitle("/ES Candlestick Chart")
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        return view

    def drawChart(self, data):
        series = QCandlestickSeries()
        for row in data:
            time = row[1] * 1000
            open = row[2]
            high = row[3]
            low = row[4]
            close = row[5]
            volume = row[6]
            series.append(QCandlestickSet(open, high, low, close, time))
        self.chart_view.chart().addSeries(series)


class ExtraCharts(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    @cached_property
    def views(self):
        return list()

    def init_ui(self):
        grid = QGridLayout(self)

        positions = (
            (0, 0, "Chart 1"),
            (0, 1, "Chart 2"),
            (1, 0, "Chart 3"),
            (1, 1, "Chart 4"),
        )
        for (row, column, title) in positions:
            view = QChartView()
            view.setRenderHint(QPainter.Antialiasing)
            view.chart().setTitle(title)
            view.chart().legend().hide()
            view.chart().createDefaultAxes()

            grid.addWidget(view, row, column)
            self.views.append(view)

    def drawChart(self, data):
        for view in self.views:
            series = QCandlestickSeries()
            view.chart().addSeries(series)
            for row in data:
                time = row[1] * 1000
                open = row[2]
                high = row[3]
                low = row[4]
                close = row[5]
                volume = row[6]
                series.append(QCandlestickSet(open, high, low, close, time))


if __name__ == "__main__":
    app = QApplication([])
    db = MySql()
    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())
