import sys
from random import randint
from typing import Union, Optional

from PySide6.QtCharts import * #(QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis)
from PySide6.QtCore import * #Qt, QDateTime, QTimer
from PySide6.QtWidgets import * # QApplication
from PySide6.QtGui import * #(QWidget, QGridLayout)


class Window(QWidget):
    running = False

    def __init__(self, window_name: str = 'Chart',
                 chart_title: Optional[str] = None,
                 geometry_ratio: int = 2,
                 histo_tick_size: int = 200):
        QWidget.__init__(self)
        # GUI
        self.window_wideness: int = 300
        self.histo_tick_size: int = histo_tick_size
        self.setGeometry(200,
                         200,
                         int(self.window_wideness * geometry_ratio),
                         self.window_wideness
                         )
        self.window_name: str = window_name
        self.setWindowTitle(self.window_name)
        self.label_color: str = 'grey'
        self.text_color: str = 'white'
        # Layout
        layout = QGridLayout(self)

        # Gui components
        bold_font = QFont()
        bold_font.setBold(True)

        self.label_last_px = QLabel('-', self)
        self.label_last_px.setFont(bold_font)
        self.label_last_px.setStyleSheet("QLabel { color : blue; }")
        layout.addWidget(self.label_last_px)

        # change the color of the window
        self.setStyleSheet('background-color:black')
        # QChart
        self.chart = QChart()
        if chart_title:
            self.chart.setTitle(chart_title)
        # Series
        self.high_dataset = QLineSeries(self.chart)
        self.high_dataset.setName("High")

        self.low_dataset = QLineSeries(self.chart)
        self.low_dataset.setName("Low")

        self.mid_dataset = QLineSeries(self.chart)
        self.mid_dataset.setName("Mid")

        self.low_of_day: Union[float, None] = 5
        self.high_of_day: Union[float, None] = 15
        self.last_data_point: dict = {"last_date": None, "mid_px": None, "low_px": None, "high_px": None}

        # Y Axis
        self.time_axis_y = QValueAxis()
        self.time_axis_y.setLabelFormat("%.2f")
        self.time_axis_y.setTitleText("Price")

        # X Axis
        self.time_axis_x = QDateTimeAxis()
        self.time_axis_x.setTitleText("Datetime")

        # Events
        self.qt_timer = QTimer()

        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.addSeries(self.mid_dataset)
        self.chart.addSeries(self.low_dataset)
        self.chart.addSeries(self.high_dataset)
        # https://linuxtut.com/fr/35fb93c7ca35f9665d9f/

        self.chart.legend().setVisible(True)
        # self.chart.legend().setAlignment(Qt.AlignBottom)

        self.chartview = QChartView(self.chart)
        # self.chartview.chart().setAxisX(self.axisX, self.mid_dataset)

        # using -1 to span through all rows available in the window
        layout.addWidget(self.chartview, 2, 0, -1, 3)

        self.chartview.setChart(self.chart)

    def set_yaxis(self):
        # Y Axis Settings
        self.time_axis_y.setRange(int(self.low_of_day * .9), int(self.high_of_day * 1.1))

        self.chart.addAxis(self.time_axis_y, Qt.AlignLeft)

        self.mid_dataset.attachAxis(self.time_axis_y)
        self.high_dataset.attachAxis(self.time_axis_y)
        self.low_dataset.attachAxis(self.time_axis_y)

    def set_xaxis(self):
        # X Axis Settings
        self.chart.removeAxis(self.time_axis_x)
        # X Axis
        self.time_axis_x = QDateTimeAxis()
        self.time_axis_x.setFormat("hh:mm:ss")
        self.time_axis_x.setTitleText("Datetime")

        point_first: QPointF = self.mid_dataset.at(0)
        point_last: QPointF = self.mid_dataset.at(len(self.mid_dataset) - 1)

        # needs to be updated each time for chart to render
        # https://stackoverflow.com/questions/57079698/qdatetimeaxis-series-are-not-displayed
        self.time_axis_x.setMin(QDateTime().fromMSecsSinceEpoch(point_first.x()).addSecs(0))
        self.time_axis_x.setMax(QDateTime().fromMSecsSinceEpoch(point_last.x()).addSecs(0))

        self.chart.addAxis(self.time_axis_x, Qt.AlignBottom)

        self.mid_dataset.attachAxis(self.time_axis_x)
        self.high_dataset.attachAxis(self.time_axis_x)
        self.low_dataset.attachAxis(self.time_axis_x)

    def _update_label_last_px(self):
        last_point: QPointF = self.mid_dataset.at(self.mid_dataset.count() - 1)
        last_date: datetime = datetime.fromtimestamp(last_point.x() / 1000)
        last_price = last_point.y()
        self.label_last_px.setText(f"Date time: {last_date.strftime('%d-%m-%y %H:%M %S')}  "
                                   f"Price: {last_price:.2f}")

    def start_app(self):
        """Start Thread generator"""
        # This method is supposed to stream data but not the issue, problem is that chart is not updating
        self.qt_timer.timeout.connect(self.update, )
        time_to_wait: int = 10000  # milliseconds
        self.qt_timer.start(time_to_wait)

    def update(self):
        """ Update chart and Label with the latest data in Series"""
        print("updating chart")
        self._update_label_last_px()
        # date_px = QDateTime()
        # self.last_data_point['last_date'] = date_px.currentDateTime().toMSecsSinceEpoch()

        date_px = datetime.now().timestamp() * 1000
        self.last_data_point['last_date'] = date_px
        # Make up a price
        self.last_data_point['mid_px'] = randint(int((self.low_of_day + 2) * 100),
                                                 int((self.high_of_day - 2) * 100)) / 100
        self.last_data_point['low_date'] = self.low_of_day
        self.last_data_point['high_date'] = self.high_of_day
        print(self.last_data_point)

        # Feed datasets and simulate deque
        # https://www.qtcentre.org/threads/67774-Dynamically-updating-QChart
        if self.mid_dataset.count() > self.histo_tick_size:
            self.mid_dataset.remove(0)
            self.low_dataset.remove(0)
            self.high_dataset.remove(0)

        self.mid_dataset.append(self.last_data_point['last_date'], self.last_data_point['mid_px'])
        self.low_dataset.append(self.last_data_point['last_date'], self.last_data_point['low_date'])
        self.high_dataset.append(self.last_data_point['last_date'], self.last_data_point['high_date'])
        self.set_xaxis()
        self.set_yaxis()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.start_app()

    sys.exit(app.exec())